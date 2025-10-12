
import os
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, START, StateGraph, END
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
    """Ask the user for a healh topic they would like to learn about"""
    print_messages_so_far(state)
    state["topic"] = input("Enter a health topic you would like to learn about:")
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
Summarize these search results documents into patient-friendly language.

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



def build_graph():

    workflow = StateGraph(State)

    workflow.add_node("ask_topic", ask_topic)
    workflow.add_node("search_for_topic", search_for_topic)
    workflow.add_node("summarize", summarize)
    workflow.add_node("present_summarization", present_summarization)

    workflow.add_edge(START, "ask_topic")
    workflow.add_edge("ask_topic", "search_for_topic")
    workflow.add_edge("search_for_topic", "summarize")
    workflow.add_conditional_edges("summarize", present_summarization, {
        "quit": END, 
        "continue": END
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
    # try:
    #     os.startfile(output_path)
    # except OSError:
    #     print("No default application set for viewing .png files on Windows or not running on Windows")


    return graph

