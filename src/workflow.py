
import os
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, START, StateGraph, END
from pydantic import BaseModel
from typing import Literal
from .utils import print_messages_so_far



# Model

from src.model import get_model

model = get_model("openai")



# Tools

from src.tools import execute_tool_calls, get_tools

tools = get_tools()



# Bind the tools (tavily search) to the model to create a search model

search_model = model.bind_tools(tools)



# State

class State(MessagesState):
    topic: str 
    search_query: str
    search_results: str
    summarized_search_results: str
    quiz_question: str
    quiz_answer: str
    quiz_grade: str
    quiz_grade_explanation: str
    repeat: bool



# Nodes


def ask_topic(state: State):
    # Clear the state
    state = State()

    """Ask the user for a healh topic they would like to learn about"""
    print_messages_so_far(state)
    state["topic"] = input("Enter a health topic you would like to learn about: ")
    if (state["topic"] == ""):
        raise Exception("You forgot to enter a topic!")
    return state



search_instructions = """
Generate a well-structured query for use in web-search related to the
medical topic of {topic}.
"""

def search_for_topic(state):
    print_messages_so_far(state)

    # Generate the search query (should be a tool call)
    state["messages"].append(
        HumanMessage(search_instructions.format(topic=state["topic"]))
    )
    search_query_response = search_model.invoke(state["messages"])
    print("\nSearch Query Response:", search_query_response, "\n")
    
    # Execute the search tool call - will append search results to messages
    execute_tool_calls(search_query_response, state, tools)
    
    # Get the search results from the last message and put it
    # into the state search_results field, returning the resulting state
    return {"search_results": state["messages"][-1].content}



summarize_instructions = """
Organize these search results documents into patient-friendly language
to help them learn about the topic.

{documents}
"""

def summarize(state):
    prompt = summarize_instructions.format(documents=state["search_results"])

    summary_response = model.invoke(prompt)
    
    state["messages"].append(
        AIMessage(summary_response.content)
    )
    
    return {"summarized_search_results": summary_response.content}



def present_summarization(state):
    print(f"""
    Here is a summary on the topic of {state["topic"]}.
    Take your time reading it and then enter "ready" when you are ready to
    take a comprehension check quiz, or "q" to quit.
    
    {state["summarized_search_results"]}
    """)
    
    user_entry = input("\n: ")
    
    if user_entry.strip().lower() == 'q':
        return "quit"
    
    return "continue"



generate_quiz_question_instructions = """
Create a quiz question based on the following summary. This question is meant
to test whether a reader has read the summary carefully.

Summary: {summary}
"""

def generate_quiz_question(state):
    prompt = generate_quiz_question_instructions.format(
        summary=state["summarized_search_results"])
    
    quiz_question_response = model.invoke(prompt)

    return {"quiz_question": quiz_question_response.content}



def present_quiz_question_and_obtain_answer(state):
    print("\nHere is a quiz question to check your comprehension:\n")
    print(state["quiz_question"])

    answer = input("\nEnter your answer: ")

    return {"quiz_answer": answer}



generate_feedback_instructions = """
Evaluate the patient's answer to the quiz question.
1. Give a letter grade ("A+", "A", "A-", "B+", "B", ... "D", "F") based on how
   well the answer shows that the patient understood the material. Allow for 
   answers that answer the question accurately, even if phrased differently or
   uses different words for the same thing. Allow for partial answers, but 
   give those a lower letter grade.
2. Explain why the patient received the letter grade, addressed toward the
   patient.
3. Include in the explanation relevant citations from the summary to reinforce
   learning.

Quiz question: {question}

Quiz answer: {answer}

Summary: {summary}
"""

def generate_feedback(state):

    # Create a structured evaluation to ensure the model returns a letter grade
    # AND an explanation
    class QuizEvaluationState(BaseModel):
        quiz_grade: Literal["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
        quiz_grade_explanation: str

    evaluator = model.with_structured_output(QuizEvaluationState)

    prompt = generate_feedback_instructions.format(
        question=state["quiz_question"],
        answer=state["quiz_answer"],
        summary=state["summarized_search_results"]
    )

    feedback = evaluator.invoke(prompt)

    return feedback



feedback_template = """
Here is your grade: {grade}

{explanation}
"""

def present_feedback(state):

    feedback = feedback_template.format(
        grade = state["quiz_grade"],
        explanation = state["quiz_grade_explanation"]
    )

    print("\n" + feedback + "\n")



def ask_for_repeat_or_exit(state):

    print("\n")

    repeat = input("Would you like to learn about another health topic? [y/n]: ")

    if repeat.strip().lower() == "y":
        return "yes"
    return "no"





def build_graph():

    workflow = StateGraph(State)

    workflow.add_node("ask_topic", ask_topic)
    workflow.add_node("search_for_topic", search_for_topic)
    workflow.add_node("summarize", summarize)
    workflow.add_node("generate_quiz_question", generate_quiz_question)
    workflow.add_node("present_quiz_question_and_obtain_answer", present_quiz_question_and_obtain_answer)
    workflow.add_node("generate_feedback", generate_feedback)
    workflow.add_node("present_feedback", present_feedback)

    workflow.add_edge(START, "ask_topic")
    workflow.add_edge("ask_topic", "search_for_topic")
    workflow.add_edge("search_for_topic", "summarize")
    workflow.add_conditional_edges("summarize", present_summarization, {
        "quit": END, 
        "continue": "generate_quiz_question"
    })
    workflow.add_edge("generate_quiz_question", "present_quiz_question_and_obtain_answer")
    workflow.add_edge("present_quiz_question_and_obtain_answer", "generate_feedback")
    workflow.add_edge("generate_feedback", "present_feedback")
    workflow.add_conditional_edges("present_feedback", ask_for_repeat_or_exit, {
        "yes": "ask_topic",
        "no": END
    })

    # Add memory
    memory = MemorySaver()

    # Compile
    graph = workflow.compile(checkpointer=memory)

    # Draw the graph to file 'graph_diagram.png' (need to open manually to view)
    png_data = graph.get_graph().draw_mermaid_png()
    output_path = "graph_diagram.png"
    with open(output_path, "wb") as f:
        f.write(png_data)

    return graph

