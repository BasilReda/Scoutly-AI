#!/bin/bash
# Start MCP server in the background on port 8001
export MCP_PORT=8001
export MCP_SERVER_HOST=localhost
export MCP_SERVER_PORT=8001
python -m backend.mcp_server.server &

# Start Backend API in the foreground on the port Render assigns
python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
