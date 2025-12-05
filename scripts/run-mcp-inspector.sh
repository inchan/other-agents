#!/bin/bash

PORT=8080

# 1. Check if port 8080 is in use
PID=$(lsof -ti :$PORT)

if [ ! -z "$PID" ]; then
  echo "⚠️  Port $PORT is already in use by process $PID."
  # Show process details
  lsof -i :$PORT

  echo ""
  read -p "Do you want to kill this process to free up port $PORT? (y/N) " response

  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Killing process $PID..."
    kill -9 $PID
    sleep 1 # Wait for process to terminate
    echo "Process killed. Port $PORT is now free."
  else
    echo "Operation cancelled. Cannot start MCP Inspector on port $PORT."
    exit 1
  fi
fi

echo "Starting MCP Inspector with Other Agents MCP server..."
echo "Access the inspector at: http://localhost:$PORT"
echo "Press Ctrl+C to stop the server."

npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server

echo "MCP Inspector stopped."
