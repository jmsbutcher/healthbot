
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

    if model_name == "openai":
        from pydantic import SecretStr
        return ChatOpenAI(
            temperature=0.1, 
            api_key=SecretStr(os.getenv("OPENAI_API_KEY")),
            streaming=True
        )

    if model_name == "ollama":
        return ChatOllama(
            model="llama3.1:8b",
            temperature=0.1
        )
