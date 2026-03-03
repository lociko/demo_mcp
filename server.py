import json
import datetime
import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("test-hello", json_response=True)


@mcp.tool('<img src=x onerror=alert>')
def hello(name: str = "world") -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"


# --- detailed request logging via custom ASGI middleware ---

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        now = datetime.datetime.now().isoformat()
        method = scope["method"]
        path = scope["path"]
        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}

        # capture request body
        body_parts = []
        async def logging_receive():
            msg = await receive()
            if msg.get("body"):
                body_parts.append(msg["body"])
            return msg

        # capture response status + headers
        resp_status = None
        resp_headers = {}
        async def logging_send(msg):
            nonlocal resp_status, resp_headers
            if msg["type"] == "http.response.start":
                resp_status = msg["status"]
                resp_headers = {k.decode(): v.decode() for k, v in msg.get("headers", [])}
            await send(msg)

        await self.app(scope, logging_receive, logging_send)

        # pretty-print the log
        body_raw = b"".join(body_parts).decode(errors="replace")
        try:
            body_json = json.loads(body_raw) if body_raw else None
        except json.JSONDecodeError:
            body_json = None

        print(f"\n{'='*60}", file=sys.stderr)
        print(f"[{now}] {method} {path}  ->  {resp_status}", file=sys.stderr)
        print(f"--- Request Headers ---", file=sys.stderr)
        for k, v in headers.items():
            print(f"  {k}: {v}", file=sys.stderr)
        print(f"--- Request Body ---", file=sys.stderr)
        if body_json:
            print(json.dumps(body_json, indent=2), file=sys.stderr)
        else:
            print(body_raw or "(empty)", file=sys.stderr)
        print(f"--- Response ---", file=sys.stderr)
        print(f"  status: {resp_status}", file=sys.stderr)
        for k, v in resp_headers.items():
            print(f"  {k}: {v}", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr, flush=True)


if __name__ == "__main__":
    # wrap the ASGI app with logging before running
    from starlette.applications import Starlette
    import uvicorn

    app = mcp.streamable_http_app()
    logged_app = LoggingMiddleware(app)
    uvicorn.run(logged_app, host="127.0.0.1", port=8000)
