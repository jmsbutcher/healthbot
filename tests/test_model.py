
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.ollama import ChatOllama

from model import get_model


def test_get_model_openai():
    openai_model = get_model("openai")
    print("Got openai model!")
    assert isinstance(openai_model, ChatOpenAI)


def test_get_model_ollama():
    openai_model = get_model("ollama")
    print("Got openai model!")
    assert isinstance(openai_model, ChatOllama)

