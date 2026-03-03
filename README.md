# MCP Hello Server

Minimal MCP server with a single `hello` tool. Logs every request in detail to stderr.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]"
```

## Run

```bash
source .venv/bin/activate
python server.py
```

Server starts at `http://127.0.0.1:8000/mcp`.

## Expose via ngrok

```bash
ngrok http 8000 --host-header=rewrite
```

The `--host-header=rewrite` flag is required so uvicorn accepts the forwarded host.

When using the ngrok free tier, clients must send `ngrok-skip-browser-warning: true` header.

## Test with curl

```bash
# Initialize session (grab the Mcp-Session-Id from response headers)
curl -s http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}'

# Call the hello tool (replace SESSION_ID)
curl -s http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Mcp-Session-Id: SESSION_ID" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"hello","arguments":{"name":"World"}}}'
```

## Shut down

```bash
# Stop the MCP server
lsof -ti:8000 | xargs kill

# Stop ngrok
pkill -f "ngrok http"
```
