from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
import httpx


UPSTREAM = "http://127.0.0.1:8317"
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
}


@app.get("/")
async def root():
    return RedirectResponse(url="/management.html#/", status_code=302)


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def proxy(path: str, request: Request):
    upstream_url = f"{UPSTREAM}/{path}"
    if request.url.query:
        upstream_url = f"{upstream_url}?{request.url.query}"

    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP_HEADERS}
    body = await request.body()

    async with httpx.AsyncClient(follow_redirects=False, timeout=30.0) as client:
        upstream = await client.request(request.method, upstream_url, headers=headers, content=body)

    response_headers = {
        k: v for k, v in upstream.headers.items() if k.lower() not in HOP_HEADERS
    }
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )
