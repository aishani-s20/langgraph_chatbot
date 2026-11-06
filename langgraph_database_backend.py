from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import sqlite3

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

conn = sqlite3.connect('chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer=SqliteSaver(conn=conn)
checkpointer.setup()

# Custom Table for Titles
def init_title_db():
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_titles (
            thread_id TEXT PRIMARY KEY,
            title TEXT
        )
    ''')
    conn.commit()

init_title_db()

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

class ChatTitle(BaseModel):
    title: str = Field(description="A concise 3 to 5 word title summarizing the conversation topic, no quotes.")

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

def generate_chat_title(user_msg: str, ai_msg: str) -> str:
    structured_llm = llm.with_structured_output(ChatTitle)
    res = structured_llm.invoke(
        f"Generate a short 3-5 word title for a chat that starts with:\nUser: {user_msg}\nAI: {ai_msg[:300]}"
    )
    return res.title

def save_chat_title(thread_id: str, title: str):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO chat_titles (thread_id, title)
        VALUES (?, ?)
    ''', (thread_id, title))
    conn.commit()

def get_all_chat_titles() -> dict:
    cursor = conn.cursor()
    cursor.execute('SELECT thread_id, title FROM chat_titles')
    rows = cursor.fetchall()
    # Returns a dictionary like {"123-uuid": "Helpful Chat Title"}
    return {row[0]: row[1] for row in rows}

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# response = chatbot.invoke({'messages': 'give c++ code for factorial'}, config={'configurable': {'thread_id': 'thread-1'}})
# print(response)
# print(chatbot.get_state(config={'configurable': {'thread_id': 'thread-1'}}))
