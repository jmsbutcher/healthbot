
import warnings 
warnings.filterwarnings('ignore')

from langchain.tools import tool
from langchain_core.output_parsers.openai_tools import parse_tool_calls
from langchain_core.messages import ToolMessage



#------------------------------------------------------------------------------
# Define tools


# Tavily search tool

from langchain_community.tools.tavily_search import TavilySearchResults
search = TavilySearchResults(max_results=3)

@tool
def search_tool(query: str):
    """
    Search the web for information using Tavily API.

    :param query: The search query string
    :return: Search results related to the query
    """
    search_docs = search.invoke(query)
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}">\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )
    return formatted_search_docs


# ... define additional tools here ...



#------------------------------------------------------------------------------
# List all tools

tools_list = [
    search_tool
    # ... add additional tools here ...
]

tool_map = {tool.name: tool for tool in tools_list}





#------------------------------------------------------------------------------
# Helper functions


def get_tools():
    return tools_list


def execute_tool_calls(response, state, tools_list):
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool = next(t for t in tools_list if t.name == tool_call["name"])
            
            result = tool.invoke(tool_call["args"])

            # Pass the result back to the model by adding a ToolMessage
            # to the messages history, then invoking the model later.
            tool_message = ToolMessage(
                content=str(result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"]
            )
            state["messages"].append(tool_message)


