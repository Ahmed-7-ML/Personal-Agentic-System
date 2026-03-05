#!/bin/bash
# run.sh
# Script to run both the FastAPI server and Streamlit client concurrently

echo "Starting FastAPI server..."
cd server
uvicorn main:app --port 3001 --reload &
SERVER_PID=$!
cd ..

echo "Starting Streamlit client..."
cd client
streamlit run app.py &
CLIENT_PID=$!
cd ..

echo "Both services started. Press Ctrl+C to stop."

# Wait for both processes
wait $SERVER_PID
wait $CLIENT_PID
