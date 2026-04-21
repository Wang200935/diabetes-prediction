#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.modeling import get_model_info_payload, predict_payload  # noqa: E402
from app.schemas import PredictionInput  # noqa: E402


def main() -> int:
    sample = PredictionInput(
        HighBP=1,
        HighChol=1,
        BMI=31.5,
        Smoker=0,
        Stroke=0,
        HeartDiseaseorAttack=0,
        PhysActivity=1,
        HvyAlcoholConsump=0,
        NoDocbcCost=0,
        GenHlth=3,
        MentHlth=4,
        PhysHlth=8,
        DiffWalk=0,
        Age=9,
        Education=5,
        Income=6,
    )

    print("Model info:")
    print(json.dumps(get_model_info_payload(), ensure_ascii=False, indent=2))
    print("\nSample prediction:")
    print(json.dumps(predict_payload(sample), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
