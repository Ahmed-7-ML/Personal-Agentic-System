import streamlit as st
import requests
import json
import os

# Configure the page
st.set_page_config(page_title="Agentic Personal Assistant", layout="wide")

# API Configuration
API_URL = "http://localhost:3001"

st.title("Agentic Personal Assistant")
st.markdown("Upload PDFs, then chat with your knowledge base.")

# Initialize session state for chat history and session ID
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = "streamlit_session_1"

# Sidebar for file upload
with st.sidebar:
    st.header("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if st.button("Ingest PDF", disabled=not uploaded_file):
        with st.spinner("Uploading and indexing..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{API_URL}/api/ingest", files=files)
                response.raise_for_status()
                st.success("Uploaded and ingested successfully.")
            except Exception as e:
                st.error(f"Error uploading file: {e}")

# Main chat interface
st.header("Chat")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Message your assistant..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Thinking..."):
        try:
            # Send to backend
            payload = {
                "message": prompt,
                "sessionId": st.session_state.session_id
            }
            response = requests.post(f"{API_URL}/api/chat", json=payload)
            response.raise_for_status()
            
            answer = response.json().get("answer", "No answer received.")
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(answer)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error communicating with backend: {e}")
