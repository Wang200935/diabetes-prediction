#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from imblearn.under_sampling import NearMiss
from kagglehub import dataset_download
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import ARTIFACT_DIR, FEATURE_SCHEMA_PATH, MODEL_BUNDLE_PATH, MODEL_METADATA_PATH  # noqa: E402
from app.domain import (  # noqa: E402
    CSV_NAME,
    DATASET_ID,
    DROPPED_COLUMNS,
    FEATURE_ORDER,
    FEATURE_SCHEMA,
    FEATURE_GROUPS,
    FEATURE_LABELS,
    LOCAL_DATASET_DIR,
    VALUE_OPTIONS,
    build_feature_schema_payload,
)


def resolve_data_path() -> Path:
    local_path = Path(LOCAL_DATASET_DIR) / CSV_NAME
    if local_path.exists():
        return local_path

    dataset_dir = Path(dataset_download(DATASET_ID))
    dataset_path = dataset_dir / CSV_NAME
    if dataset_path.exists():
        return dataset_path

    raise FileNotFoundError(f"Unable to find dataset file {CSV_NAME}")


def select_model():
    try:
        from xgboost import XGBClassifier

        return (
            XGBClassifier(
                eval_metric="error",
                learning_rate=0.1,
                random_state=42,
            ),
            "XGBoost",
        )
    except Exception:
        return HistGradientBoostingClassifier(random_state=42), "HistGradientBoosting"


def main() -> int:
    data_path = resolve_data_path()
    raw_df = pd.read_csv(data_path, encoding="utf-8")

    working_df = raw_df.drop(columns=[col for col in DROPPED_COLUMNS if col in raw_df.columns])
    X = working_df[FEATURE_ORDER].copy()
    y = working_df["Diabetes_binary"].astype(int).copy()

    sampler = NearMiss(version=1, n_neighbors=10)
    x_sampled, y_sampled = sampler.fit_resample(X, y)

    X_train, X_test, y_train, y_test = train_test_split(
        x_sampled,
        y_sampled,
        test_size=0.3,
        random_state=42,
        stratify=y_sampled,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model, model_name = select_model()
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_test_scaled)[:, 1]
    else:
        y_prob = y_pred.astype(float)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
    }

    model_version = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "model_name": model_name,
        "model_version": model_version,
        "threshold": 0.5,
        "dataset_path": str(data_path),
        "dataset_id": DATASET_ID,
        "csv_name": CSV_NAME,
        "feature_order": FEATURE_ORDER,
        "metrics": metrics,
        "disclaimer": "此結果僅供風險評估與健康教育參考，不能替代醫師診斷。",
    }

    bundle = {
        "model": model,
        "scaler": scaler,
        "feature_order": FEATURE_ORDER,
        "metadata": metadata,
    }

    joblib.dump(bundle, MODEL_BUNDLE_PATH)
    MODEL_METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    schema_payload = build_feature_schema_payload()
    FEATURE_SCHEMA_PATH.write_text(
        json.dumps(schema_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
