from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Automatically find the .env file even if the .py script is in a subfolder
# dotenv_path = find_dotenv()
# loaded = load_dotenv(dotenv_path, override=True)
# print(f".env loaded: {loaded} (from: {dotenv_path})")

# # 2. Fetch GEMINI_API_KEY and pass it explicitly so version differences don't break it
# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     raise ValueError("GEMINI_API_KEY not found! Check that .env is saved and in the project folder.")

# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-flash-lite",
#     api_key=api_key
# )

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Checkpointer
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)