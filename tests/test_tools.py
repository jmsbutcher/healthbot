
from tools import get_tools


def test_search_tool():
    tools = get_tools()
    search_tool = next((tool for tool in tools if tool.name == 'search_tool'), None)
    assert search_tool is not None, "Search tool not found"
    assert callable(search_tool), "Search tool is not callable"

    # Example search query
    query = "hello world"
    result = search_tool.invoke(query)
    
    assert isinstance(result, str), "Search result should be a string"
    assert "<Document href=" in result, "Search result should contain Document tags"



