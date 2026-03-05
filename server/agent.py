from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from tools import search_knowledge_base
import os

# Global Store for Session Histories
# Key: session_id, Value: ChatMessageHistory
session_histories = {}

def get_session_history(session_id: str):
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]


# Initialize Model
llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0)

# Define System Prompt
system_prompt = """
    You are a helpful AI assistant with access to a knowledge base.
    When users ask questions, search the knowledge base using the available tools to find relevant information.
    Be concise and accurate.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# Define Tools
tools = [search_knowledge_base]

# Create Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# Create Agent Executer
agent_executor = AgentExecutor(agent, tools, verbose=True)

# Create Agent with Chat History
agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# Function to run the agent
def run_agent(session_id: str, message: str) -> dict:
    print(f"🤖 Running agent for: '{message}'")

    response = agent_with_chat_history.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    )

    output = response.get("output", "")
    print(f"✅ Agent response: {output[:100]}...")

    return {"output": output}

