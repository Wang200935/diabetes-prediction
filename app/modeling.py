import json
from functools import lru_cache
from typing import Dict

import joblib
import numpy as np
import pandas as pd

from app.config import FEATURE_SCHEMA_PATH, MODEL_BUNDLE_PATH, MODEL_METADATA_PATH
from app.domain import (
    FEATURE_ORDER,
    FEATURE_LABELS,
    build_feature_schema_payload,
    build_summary_label,
    classify_risk,
    humanize_value,
)
from app.recommendations import build_attention_points, build_recommendations
from app.schemas import PredictionInput


DEFAULT_DISCLAIMER = "此結果僅供風險評估與健康教育參考，不能替代醫師診斷。"


@lru_cache
def load_model_bundle() -> Dict[str, object]:
    if not MODEL_BUNDLE_PATH.exists():
        raise FileNotFoundError(
            f"Model bundle not found at {MODEL_BUNDLE_PATH}. "
            "Run `python scripts/train_and_export.py` first."
        )
    return joblib.load(MODEL_BUNDLE_PATH)


@lru_cache
def load_model_metadata() -> Dict[str, object]:
    if MODEL_METADATA_PATH.exists():
        return json.loads(MODEL_METADATA_PATH.read_text(encoding="utf-8"))

    bundle = load_model_bundle()
    return bundle.get("metadata", {})


def get_model_info_payload() -> Dict[str, object]:
    metadata = load_model_metadata()
    features = build_feature_schema_payload()

    if FEATURE_SCHEMA_PATH.exists():
        try:
            features = json.loads(FEATURE_SCHEMA_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    return {
        "model_name": metadata.get("model_name", "未命名模型"),
        "model_version": metadata.get("model_version", "dev"),
        "threshold": float(metadata.get("threshold", 0.5)),
        "features": features,
        "disclaimer": metadata.get("disclaimer", DEFAULT_DISCLAIMER),
    }


def _prepare_feature_frame(payload: PredictionInput) -> pd.DataFrame:
    row = {feature_name: float(getattr(payload, feature_name)) for feature_name in FEATURE_ORDER}
    return pd.DataFrame([row], columns=FEATURE_ORDER)


def _build_input_summary(payload: PredictionInput) -> Dict[str, str]:
    summary = {}
    for feature_name in FEATURE_ORDER:
        value = getattr(payload, feature_name)
        summary[FEATURE_LABELS[feature_name]] = humanize_value(feature_name, value)
    return summary


def predict_payload(payload: PredictionInput) -> Dict[str, object]:
    bundle = load_model_bundle()
    metadata = load_model_metadata()

    model = bundle["model"]
    scaler = bundle["scaler"]
    threshold = float(metadata.get("threshold", 0.5))

    raw_features = _prepare_feature_frame(payload)
    model_features = scaler.transform(raw_features) if scaler is not None else raw_features.values

    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(model_features)[0, 1])
    else:
        probability = float(model.predict(model_features)[0])

    predicted_class = int(probability >= threshold)
    risk = classify_risk(probability)

    payload_dict = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    return {
        "model_name": metadata.get("model_name", "未命名模型"),
        "model_version": metadata.get("model_version", "dev"),
        "predicted_class": predicted_class,
        "result_summary": build_summary_label(risk["token"]),
        "risk_probability": round(probability, 4),
        "risk_level": risk["label"],
        "risk_token": risk["token"],
        "threshold": threshold,
        "disclaimer": metadata.get("disclaimer", DEFAULT_DISCLAIMER),
        "input_summary": _build_input_summary(payload),
        "attention_points": build_attention_points(payload_dict),
        "recommendations": build_recommendations(payload_dict, probability),
    }
