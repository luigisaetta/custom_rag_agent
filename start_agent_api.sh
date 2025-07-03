export HOST=0.0.0.0
export PORT=8080
uvicorn rag_agent_api:app --host $HOST --port $PORT --reload