from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import WEB_DIR
from app.modeling import get_model_info_payload, load_model_metadata, predict_payload
from app.schemas import HealthOutput, ModelInfoOutput, PredictionInput, PredictionOutput


app = FastAPI(
    title="Diabetes Risk Predictor",
    version="1.0.0",
    summary="Notebook-derived diabetes risk inference backend with a visual website.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health", response_model=HealthOutput)
def health() -> dict:
    try:
        metadata = load_model_metadata()
        model_loaded = True
    except FileNotFoundError:
        metadata = {}
        model_loaded = False
    return {
        "status": "ok" if model_loaded else "artifact-missing",
        "model_loaded": model_loaded,
        "model_version": metadata.get("model_version", "dev"),
    }


@app.get("/api/model-info", response_model=ModelInfoOutput)
def model_info() -> dict:
    return get_model_info_payload()


@app.post("/api/predict", response_model=PredictionOutput)
def predict(payload: PredictionInput) -> dict:
    return predict_payload(payload)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    icon_path = WEB_DIR / "favicon.svg"
    if icon_path.exists():
        return FileResponse(icon_path)
    return FileResponse(WEB_DIR / "index.html")
