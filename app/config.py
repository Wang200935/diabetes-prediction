import os
from pathlib import Path
from typing import List


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value is not None and value.strip() else default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value is not None and value.strip() else default


def _get_csv(name: str, default: str) -> List[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


ROOT_DIR = Path(__file__).resolve().parent.parent

APP_ENV = os.getenv("APP_ENV", "development")
APP_TITLE = os.getenv("APP_TITLE", "Diabetes Risk Predictor")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_SUMMARY = os.getenv(
    "APP_SUMMARY",
    "Notebook-derived diabetes risk inference backend with a visual website.",
)

DOCS_ENABLED = _get_bool("APP_DOCS_ENABLED", False)
DOCS_URL = "/docs" if DOCS_ENABLED else None
REDOC_URL = "/redoc" if DOCS_ENABLED else None
OPENAPI_URL = "/openapi.json" if DOCS_ENABLED else None

WEB_DIR = Path(os.getenv("APP_WEB_DIR", str(ROOT_DIR / "web")))
ARTIFACT_DIR = Path(os.getenv("APP_ARTIFACT_DIR", str(ROOT_DIR / "artifacts")))
MODEL_BUNDLE_PATH = Path(
    os.getenv("APP_MODEL_BUNDLE_PATH", str(ARTIFACT_DIR / "model_bundle.joblib"))
)
MODEL_METADATA_PATH = Path(
    os.getenv("APP_MODEL_METADATA_PATH", str(ARTIFACT_DIR / "model_metadata.json"))
)
FEATURE_SCHEMA_PATH = Path(
    os.getenv("APP_FEATURE_SCHEMA_PATH", str(ARTIFACT_DIR / "feature_schema.json"))
)

ALLOWED_ORIGINS = _get_csv(
    "APP_ALLOWED_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000",
)
ALLOWED_HOSTS = _get_csv(
    "APP_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)
ALLOW_CREDENTIALS = _get_bool("APP_ALLOW_CREDENTIALS", False)

PREDICT_CONCURRENCY_LIMIT = _get_int("PREDICT_CONCURRENCY_LIMIT", 4)
PREDICT_ACQUIRE_TIMEOUT_SECONDS = _get_float("PREDICT_ACQUIRE_TIMEOUT_SECONDS", 0.25)
PREDICT_EXEC_TIMEOUT_SECONDS = _get_float("PREDICT_EXEC_TIMEOUT_SECONDS", 8.0)
PREDICT_RATE_LIMIT_WINDOW_SECONDS = _get_int("PREDICT_RATE_LIMIT_WINDOW_SECONDS", 60)
PREDICT_RATE_LIMIT_MAX_REQUESTS = _get_int("PREDICT_RATE_LIMIT_MAX_REQUESTS", 600)

PREDICTION_CACHE_CONTROL = os.getenv("APP_PREDICTION_CACHE_CONTROL", "no-store, max-age=0")
PREDICTION_PRAGMA = os.getenv("APP_PREDICTION_PRAGMA", "no-cache")

SECURITY_HEADERS = {
    "Content-Security-Policy": os.getenv(
        "APP_CSP",
        (
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
    ),
    "X-Content-Type-Options": os.getenv("APP_X_CONTENT_TYPE_OPTIONS", "nosniff"),
    "X-Frame-Options": os.getenv("APP_X_FRAME_OPTIONS", "DENY"),
    "Referrer-Policy": os.getenv("APP_REFERRER_POLICY", "no-referrer"),
    "Permissions-Policy": os.getenv(
        "APP_PERMISSIONS_POLICY",
        "camera=(), microphone=(), geolocation=()",
    ),
    "Cross-Origin-Opener-Policy": os.getenv(
        "APP_CROSS_ORIGIN_OPENER_POLICY",
        "same-origin",
    ),
    "Cross-Origin-Resource-Policy": os.getenv(
        "APP_CROSS_ORIGIN_RESOURCE_POLICY",
        "same-origin",
    ),
}
