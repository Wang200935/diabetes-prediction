# diabetes-prediction

This repository now includes:

- the original notebook-based research workflow
- a reproducible training/export script
- a deployable FastAPI inference backend
- a browser-based questionnaire UI with risk visualization and recommendation cards

## Project layout

- `diabetes-prediction-eda-preprocessing-models.ipynb`: research notebook
- `scripts/train_and_export.py`: retrain the final deployable model and export artifacts
- `scripts/smoke_test.py`: quick end-to-end inference smoke test
- `app/main.py`: FastAPI entrypoint
- `web/`: frontend assets served by FastAPI

## Quick start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Export the deployable model bundle:

```bash
python scripts/train_and_export.py
```

3. Run the API and website:

```bash
uvicorn app.main:app --reload
```

4. Open:

```text
http://127.0.0.1:8000
```

## API

- `GET /health`
- `GET /api/model-info`
- `POST /api/predict`

## Notes

- The training script prefers the local dataset directory `/Users/wang/Downloads/archive`.
- If the local file is not found, it falls back to `kagglehub`.
- The deployable training flow prefers `XGBoost`, but falls back to `HistGradientBoosting` if XGBoost is unavailable in the environment.
