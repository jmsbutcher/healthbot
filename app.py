
from langchain_core.runnables import RunnableConfig
from src.workflow import build_graph


def main():
    
    graph = build_graph()

    config = RunnableConfig(recursion_limit=2000, configurable={"thread_id": "2"})  

    initial_state = {"messages": [],}
    
    output = graph.invoke(
        initial_state,
        config,
    )
    print("\n----------------------------------------\nFinal Output:\n")
    print(output)



if __name__ == "__main__":
    main()


