import asyncio
import time
from collections import defaultdict, deque

import anyio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import (
    ALLOWED_HOSTS,
    ALLOWED_ORIGINS,
    ALLOW_CREDENTIALS,
    APP_SUMMARY,
    APP_TITLE,
    APP_VERSION,
    DOCS_URL,
    OPENAPI_URL,
    PREDICTION_CACHE_CONTROL,
    PREDICTION_PRAGMA,
    PREDICT_ACQUIRE_TIMEOUT_SECONDS,
    PREDICT_CONCURRENCY_LIMIT,
    PREDICT_EXEC_TIMEOUT_SECONDS,
    PREDICT_RATE_LIMIT_MAX_REQUESTS,
    PREDICT_RATE_LIMIT_WINDOW_SECONDS,
    REDOC_URL,
    SECURITY_HEADERS,
    WEB_DIR,
)
from app.modeling import load_model_metadata, predict_payload
from app.schemas import HealthOutput, PredictionInput, PredictionOutput


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    summary=APP_SUMMARY,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)
_predict_semaphore = asyncio.Semaphore(PREDICT_CONCURRENCY_LIMIT)
_predict_ip_windows = defaultdict(deque)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(ALLOWED_ORIGINS),
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS,
)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


def _security_headers(path: str) -> dict:
    headers = dict(SECURITY_HEADERS)
    if path.startswith("/api/") or path in {"/result", "/assessment", "/about", "/"}:
        headers["Cache-Control"] = PREDICTION_CACHE_CONTROL
        headers["Pragma"] = PREDICTION_PRAGMA
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
