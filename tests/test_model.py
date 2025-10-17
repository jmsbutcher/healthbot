
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from src.model import get_model


def test_get_model_openai():
    openai_model = get_model("openai")
    assert isinstance(openai_model, ChatOpenAI)


def test_get_model_ollama():
    openai_model = get_model("ollama")
    assert isinstance(openai_model, ChatOllama)

