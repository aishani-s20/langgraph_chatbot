# LangGraph & Streamlit Chatbot App

This project demonstrates how to build a stateful, AI-powered chatbot using **LangGraph**, **Streamlit**, and **Google's Gemini 3.1 Flash-Lite** model.

The repository is structured to show the evolution of a chatbot application from a basic request-response interface to an advanced, multi-threaded conversational agent with streaming capabilities and dynamic chat management.

## 🚀 Features & Progression

This project contains three distinct frontend iterations, all powered by a single, robust LangGraph backend:

1. **Basic Chatbot (`streamlit_frontend.py`)**: A foundational implementation. It takes user input, sends it to the LangGraph backend, waits for the complete response, and displays it.

2. **Streaming Chatbot (`streamlit_streaming_frontend.py`)**: Enhances user experience by utilizing Streamlit's `st.write_stream` and LangGraph's message streaming. Responses are generated token-by-token, reducing perceived latency.

3. **Multi-Threaded Chatbot (`streamlit_threading_frontend.py`)**: A production-style interface featuring:

   * **Sidebar Chat History:** View, load, and resume previous conversations.

   * **Session Isolation:** Uses random UUIDs (`uuid.uuid4()`) to maintain isolated chat threads via LangGraph's `InMemorySaver`.

   * **AI-Powered Chat Naming:** Mimics modern chatbots by using the LLM to read the first exchange of a new thread and dynamically generate a concise chat title.

## 📁 Project Structure

* **`langgraph_backend.py`**: The core logic engine. It defines the LangGraph `StateGraph`, the `ChatState` (a TypedDict holding the message history), and the single `chat_node`. It utilizes `InMemorySaver` for checkpointing and `langchain-google-genai` to interface with the `gemini-3.1-flash-lite` model. It also includes a tool for structured output generation to create chat titles.

* **`streamlit_frontend.py`**: The V1 frontend (Basic blocking invoke).

* **`streamlit_streaming_frontend.py`**: The V2 frontend (Token-streaming).

* **`streamlit_threading_frontend.py`**: The V3 frontend (Full UI with threading, history, and chat naming).

## 🧠 Key Architectural Decisions

During the development of the advanced frontend (`streamlit_threading_frontend.py`), several important design decisions were made to improve reliability and user experience:

### 1. Rendering: `st.markdown` vs `st.text`

Initially, `st.text` was used to display and store messages. However, LLMs frequently output rich text formats, including bolding, lists, and especially **code blocks**.

* **The Problem:** `st.text` renders input as raw, plain text, stripping away formatting. Code snippets become unreadable, flat text blocks.

* **The Solution:** Switching to `st.markdown` ensures that all Markdown elements returned by the Gemini model are parsed and rendered correctly, complete with syntax highlighting for code blocks.

### 2. AI-Powered Chat Naming (Structured Output)

Instead of displaying raw, unreadable Thread IDs (UUIDs) in the sidebar, or simply truncating the user's first prompt (which can be messy), this app uses an AI-driven approach:

* When a new chat is initiated, the first user prompt and the AI's first response are passed to a secondary LLM call (`generate_chat_title`).

* This uses the `.with_structured_output()` feature mapped to a Pydantic model (`ChatTitle`) to strictly return a concise, 3-5 word summary.

* This dictionary of `[thread_id]: "AI Title"` is stored in Streamlit's session state, creating a clean, recognizable history for the user.

### 3. Stateful Threading via Checkpointers

LangGraph's `InMemorySaver` is used to persist the state (message history) of different conversations. By generating a unique `thread_id` via UUID for every new chat and passing it into the `config` dictionary (`{'configurable': {'thread_id': ...}}`), the backend can easily pull up the exact state of past conversations when a user clicks an old chat in the sidebar.

## 🛠️ Setup & Installation

**1. Clone the repository and install dependencies:**
Ensure you have `streamlit`, `langgraph`, `langchain-core`, `langchain-google-genai`, `python-dotenv`, and `pydantic` installed.

```
pip install streamlit langgraph langchain-core langchain-google-genai python-dotenv pydantic

```

**2. Configure Environment Variables:**
Create a `.env` file in the root directory of your project and add your Google Gemini API key:

```
GOOGLE_API_KEY=your_api_key_here

```

**3. Run the Application:**
Choose the frontend version you want to run and execute it via Streamlit. For the most feature-rich experience, run the threading frontend:

```
streamlit run streamlit_threading_frontend.py

```