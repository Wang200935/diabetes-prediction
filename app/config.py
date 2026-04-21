from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_DIR = ROOT_DIR / "artifacts"
MODEL_BUNDLE_PATH = ARTIFACT_DIR / "model_bundle.joblib"
MODEL_METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"
FEATURE_SCHEMA_PATH = ARTIFACT_DIR / "feature_schema.json"
WEB_DIR = ROOT_DIR / "web"

