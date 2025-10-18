
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

import os
from dotenv import load_dotenv
load_dotenv('.env')
assert os.getenv('OPENAI_API_KEY') is not None
assert os.getenv('TAVILY_API_KEY') is not None



def get_model(model_name: str):
    """
    Choices: "openai", "ollama"
    """

    # Requires an Open AI api key.
    # Create a ".env" file in top level directory and include the line:
    #  OPENAI_API_KEY=<your api key>
    if model_name == "openai":
        from pydantic import SecretStr
        return ChatOpenAI(
            temperature=0.1, 
            api_key=SecretStr(os.getenv("OPENAI_API_KEY")),
            streaming=True
        )

    # Requires Ollama to be installed and running on your machine, and must 
    # pull the below model (Example: run "ollama pull llama3.1:8b" in terminal)
    if model_name == "ollama":
        return ChatOllama(
            model="llama3.1:8b",
            temperature=0.1
        )
    

    # ... Add additional models here ...
    
    
    raise Exception("Invalid model name: " + model_name)

