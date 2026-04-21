#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from kagglehub import dataset_download
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, f1_score, precision_score, recall_score, roc_auc_score
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


def build_candidate_models():
    candidates = [
        (
            "CalibratedLogisticRegression",
            LogisticRegression(
                max_iter=4000,
                class_weight="balanced",
                random_state=42,
            ),
            True,
        ),
        (
            "CalibratedRandomForest",
            RandomForestClassifier(
                n_estimators=180,
                max_depth=10,
                min_samples_leaf=8,
                class_weight="balanced_subsample",
                random_state=42,
                n_jobs=-1,
            ),
            False,
        ),
        (
            "CalibratedHistGradientBoosting",
            HistGradientBoostingClassifier(
                random_state=42,
                max_depth=6,
                learning_rate=0.06,
                max_iter=200,
            ),
            False,
        ),
    ]
    return candidates


def evaluate_candidate(model_name, estimator, use_scaler, X_train, y_train, X_test, y_test):
    scaler = StandardScaler() if use_scaler else None
    if scaler is not None:
        X_train_ready = scaler.fit_transform(X_train)
        X_test_ready = scaler.transform(X_test)
    else:
        X_train_ready = X_train.to_numpy()
        X_test_ready = X_test.to_numpy()

    calibrated_model = CalibratedClassifierCV(estimator=estimator, method="sigmoid", cv=3)
    calibrated_model.fit(X_train_ready, y_train)

    y_prob = calibrated_model.predict_proba(X_test_ready)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "brier_score": round(float(brier_score_loss(y_test, y_prob)), 4),
    }

    return {
        "model_name": model_name,
        "model": calibrated_model,
        "scaler": scaler,
        "metrics": metrics,
        "test_probability": y_prob,
        "test_prediction": y_pred,
    }


def build_sanity_examples():
    return {
        "low": {
            "HighBP": 0,
            "HighChol": 0,
            "BMI": 20,
            "Smoker": 0,
            "Stroke": 0,
            "HeartDiseaseorAttack": 0,
            "PhysActivity": 1,
            "HvyAlcoholConsump": 0,
            "NoDocbcCost": 0,
            "GenHlth": 1,
            "MentHlth": 0,
            "PhysHlth": 0,
            "DiffWalk": 0,
            "Age": 1,
            "Education": 6,
            "Income": 8,
        },
        "mid": {
            "HighBP": 0,
            "HighChol": 1,
            "BMI": 25,
            "Smoker": 0,
            "Stroke": 0,
            "HeartDiseaseorAttack": 0,
            "PhysActivity": 1,
            "HvyAlcoholConsump": 0,
            "NoDocbcCost": 0,
            "GenHlth": 3,
            "MentHlth": 3,
            "PhysHlth": 3,
            "DiffWalk": 0,
            "Age": 7,
            "Education": 4,
            "Income": 5,
        },
        "high": {
            "HighBP": 1,
            "HighChol": 1,
            "BMI": 35,
            "Smoker": 1,
            "Stroke": 1,
            "HeartDiseaseorAttack": 1,
            "PhysActivity": 0,
            "HvyAlcoholConsump": 1,
            "NoDocbcCost": 1,
            "GenHlth": 5,
            "MentHlth": 20,
            "PhysHlth": 20,
            "DiffWalk": 1,
            "Age": 13,
            "Education": 1,
            "Income": 1,
        },
    }


def predict_examples(calibrated_model, scaler, examples):
    example_df = pd.DataFrame(examples.values(), index=examples.keys(), columns=FEATURE_ORDER)
    if scaler is not None:
        features = scaler.transform(example_df)
    else:
        features = example_df.to_numpy()
    probs = calibrated_model.predict_proba(features)[:, 1]
    return {name: round(float(prob), 4) for name, prob in zip(example_df.index, probs)}


def main() -> int:
    data_path = resolve_data_path()
    raw_df = pd.read_csv(data_path, encoding="utf-8")

    working_df = raw_df.drop(columns=[col for col in DROPPED_COLUMNS if col in raw_df.columns])
    X = working_df[FEATURE_ORDER].copy()
    y = working_df["Diabetes_binary"].astype(int).copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    candidate_results = [
        evaluate_candidate(name, estimator, use_scaler, X_train, y_train, X_test, y_test)
        for name, estimator, use_scaler in build_candidate_models()
    ]
    candidate_results.sort(
        key=lambda item: (
            item["metrics"]["accuracy"],
            item["metrics"]["roc_auc"],
            -item["metrics"]["brier_score"],
        ),
        reverse=True,
    )
    best = candidate_results[0]

    example_probs = predict_examples(best["model"], best["scaler"], build_sanity_examples())

    model_version = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "model_name": best["model_name"],
        "model_version": model_version,
        "threshold": 0.5,
        "dataset_path": str(data_path),
        "dataset_id": DATASET_ID,
        "csv_name": CSV_NAME,
        "feature_order": FEATURE_ORDER,
        "metrics": best["metrics"],
        "candidate_metrics": [
            {
                "model_name": candidate["model_name"],
                **candidate["metrics"],
            }
            for candidate in candidate_results
        ],
        "class_distribution": {
            "negative": int((y == 0).sum()),
            "positive": int((y == 1).sum()),
        },
        "calibration": {
            "method": "sigmoid",
            "cv": 5,
        },
        "sanity_examples": example_probs,
        "disclaimer": "此結果僅供風險評估與健康教育參考，不能替代醫師診斷。",
    }

    bundle = {
        "model": best["model"],
        "scaler": best["scaler"],
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
