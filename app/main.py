import asyncio
import time
from collections import defaultdict, deque

import anyio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import WEB_DIR
from app.modeling import load_model_metadata, predict_payload
from app.schemas import HealthOutput, PredictionInput, PredictionOutput


app = FastAPI(
    title="Diabetes Risk Predictor",
    version="1.0.0",
    summary="Notebook-derived diabetes risk inference backend with a visual website.",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
}
PREDICT_CONCURRENCY_LIMIT = 4
PREDICT_ACQUIRE_TIMEOUT_SECONDS = 0.25
PREDICT_EXEC_TIMEOUT_SECONDS = 8
PREDICT_RATE_LIMIT_WINDOW_SECONDS = 60
PREDICT_RATE_LIMIT_MAX_REQUESTS = 600
_predict_semaphore = asyncio.Semaphore(PREDICT_CONCURRENCY_LIMIT)
_predict_ip_windows = defaultdict(deque)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(ALLOWED_ORIGINS),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost"],
)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


def _security_headers(path: str) -> dict:
    headers = {
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'"
        ),
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-origin",
    }
    if path.startswith("/api/") or path in {"/result", "/assessment", "/about", "/"}:
        headers["Cache-Control"] = "no-store, max-age=0"
        headers["Pragma"] = "no-cache"
    return headers


@app.middleware("http")
async def apply_security_headers(request: Request, call_next):
    response = await call_next(request)
    for key, value in _security_headers(request.url.path).items():
        response.headers[key] = value
    if "server" in response.headers:
        del response.headers["server"]
    return response


def _check_predict_rate_limit(client_ip: str) -> None:
    now = time.monotonic()
    bucket = _predict_ip_windows[client_ip]
    while bucket and now - bucket[0] > PREDICT_RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= PREDICT_RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="請稍後再試，系統目前收到較多預測請求。")
    bucket.append(now)


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(WEB_DIR / "home.html")


@app.get("/assessment", include_in_schema=False)
def assessment() -> FileResponse:
    return FileResponse(WEB_DIR / "assessment.html")


@app.get("/result", include_in_schema=False)
def result_page() -> FileResponse:
    return FileResponse(WEB_DIR / "result.html")


@app.get("/about", include_in_schema=False)
def about_page() -> FileResponse:
    return FileResponse(WEB_DIR / "about.html")


@app.get("/health", response_model=HealthOutput)
def health() -> dict:
    try:
        load_model_metadata()
        model_loaded = True
    except FileNotFoundError:
        model_loaded = False
    return {
        "status": "ok" if model_loaded else "artifact-missing",
        "model_loaded": model_loaded,
    }


@app.post("/api/predict", response_model=PredictionOutput)
async def predict(request: Request, payload: PredictionInput) -> dict:
    client_ip = request.client.host if request.client else "unknown"
    _check_predict_rate_limit(client_ip)

    try:
        await asyncio.wait_for(_predict_semaphore.acquire(), timeout=PREDICT_ACQUIRE_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=503, detail="目前同時預測請求較多，請稍後再試。")

    try:
        result = await asyncio.wait_for(
            anyio.to_thread.run_sync(predict_payload, payload),
            timeout=PREDICT_EXEC_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=503, detail="預測處理逾時，請稍後再試。")
    finally:
        _predict_semaphore.release()

    return result


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    icon_path = WEB_DIR / "favicon.svg"
    if icon_path.exists():
        return FileResponse(icon_path)
    return FileResponse(WEB_DIR / "home.html")
