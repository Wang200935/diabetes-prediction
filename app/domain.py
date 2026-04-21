from typing import Dict, List, Tuple


DATASET_ID = "alexteboul/diabetes-health-indicators-dataset"
CSV_NAME = "diabetes_binary_health_indicators_BRFSS2015.csv"
LOCAL_DATASET_DIR = "/Users/wang/Downloads/archive"

FEATURE_ORDER = [
    "HighBP",
    "HighChol",
    "BMI",
    "Smoker",
    "Stroke",
    "HeartDiseaseorAttack",
    "PhysActivity",
    "HvyAlcoholConsump",
    "NoDocbcCost",
    "GenHlth",
    "MentHlth",
    "PhysHlth",
    "DiffWalk",
    "Age",
    "Education",
    "Income",
]

DROPPED_COLUMNS = [
    "Fruits",
    "Veggies",
    "Sex",
    "CholCheck",
    "AnyHealthcare",
    "Diabetes_binary_str",
]

FEATURE_LABELS = {
    "HighBP": "是否有高血壓",
    "HighChol": "是否有高膽固醇",
    "BMI": "BMI",
    "Smoker": "是否吸菸",
    "Stroke": "是否曾中風",
    "HeartDiseaseorAttack": "是否曾有心臟病或心肌梗塞",
    "PhysActivity": "是否規律運動",
    "HvyAlcoholConsump": "是否重度飲酒",
    "NoDocbcCost": "是否曾因費用而無法就醫",
    "GenHlth": "自評整體健康",
    "MentHlth": "過去 30 天心理不佳天數",
    "PhysHlth": "過去 30 天身體不佳天數",
    "DiffWalk": "是否行走困難",
    "Age": "年齡組別",
    "Education": "教育程度",
    "Income": "收入等級",
}

FEATURE_GROUPS = {
    "HighBP": "慢性病與病史",
    "HighChol": "慢性病與病史",
    "BMI": "基本資料",
    "Smoker": "生活習慣",
    "Stroke": "慢性病與病史",
    "HeartDiseaseorAttack": "慢性病與病史",
    "PhysActivity": "生活習慣",
    "HvyAlcoholConsump": "生活習慣",
    "NoDocbcCost": "健康狀況",
    "GenHlth": "健康狀況",
    "MentHlth": "健康狀況",
    "PhysHlth": "健康狀況",
    "DiffWalk": "健康狀況",
    "Age": "基本資料",
    "Education": "基本資料",
    "Income": "基本資料",
}

VALUE_OPTIONS = {
    "HighBP": {0: "否", 1: "是"},
    "HighChol": {0: "否", 1: "是"},
    "Smoker": {0: "否", 1: "是"},
    "Stroke": {0: "否", 1: "是"},
    "HeartDiseaseorAttack": {0: "否", 1: "是"},
    "PhysActivity": {0: "否", 1: "是"},
    "HvyAlcoholConsump": {0: "否", 1: "是"},
    "NoDocbcCost": {0: "否", 1: "是"},
    "DiffWalk": {0: "否", 1: "是"},
    "GenHlth": {
        1: "極佳",
        2: "很好",
        3: "普通",
        4: "較差",
        5: "很差",
    },
    "Age": {
        1: "18-24歲",
        2: "25-29歲",
        3: "30-34歲",
        4: "35-39歲",
        5: "40-44歲",
        6: "45-49歲",
        7: "50-54歲",
        8: "55-59歲",
        9: "60-64歲",
        10: "65-69歲",
        11: "70-74歲",
        12: "75-79歲",
        13: "80歲以上",
    },
    "Education": {
        1: "未曾就學",
        2: "國小",
        3: "國中",
        4: "高中",
        5: "大學",
        6: "研究所以上",
    },
    "Income": {
        1: "低於 10,000 美元",
        2: "10,000-14,999 美元",
        3: "15,000-19,999 美元",
        4: "20,000-24,999 美元",
        5: "25,000-34,999 美元",
        6: "35,000-49,999 美元",
        7: "50,000-74,999 美元",
        8: "75,000 美元以上",
    },
}

FEATURE_SCHEMA = {
    "HighBP": {"type": "binary", "min": 0, "max": 1},
    "HighChol": {"type": "binary", "min": 0, "max": 1},
    "BMI": {"type": "float", "min": 10, "max": 80},
    "Smoker": {"type": "binary", "min": 0, "max": 1},
    "Stroke": {"type": "binary", "min": 0, "max": 1},
    "HeartDiseaseorAttack": {"type": "binary", "min": 0, "max": 1},
    "PhysActivity": {"type": "binary", "min": 0, "max": 1},
    "HvyAlcoholConsump": {"type": "binary", "min": 0, "max": 1},
    "NoDocbcCost": {"type": "binary", "min": 0, "max": 1},
    "GenHlth": {"type": "ordinal", "min": 1, "max": 5},
    "MentHlth": {"type": "integer", "min": 0, "max": 30},
    "PhysHlth": {"type": "integer", "min": 0, "max": 30},
    "DiffWalk": {"type": "binary", "min": 0, "max": 1},
    "Age": {"type": "ordinal", "min": 1, "max": 13},
    "Education": {"type": "ordinal", "min": 1, "max": 6},
    "Income": {"type": "ordinal", "min": 1, "max": 8},
}

RISK_BANDS: List[Tuple[float, str, str]] = [
    (0.25, "低風險", "low"),
    (0.50, "中等風險", "medium"),
    (0.75, "偏高風險", "elevated"),
    (1.01, "高風險", "high"),
]


def classify_risk(probability: float) -> Dict[str, str]:
    for upper_bound, label, token in RISK_BANDS:
        if probability < upper_bound:
            return {"label": label, "token": token}
    return {"label": "高風險", "token": "high"}


def humanize_value(feature_name: str, value: float) -> str:
    options = VALUE_OPTIONS.get(feature_name)
    if options is not None:
        try:
            value = int(value)
        except (TypeError, ValueError):
            return str(value)
        return options.get(value, str(value))

    if feature_name == "BMI":
        return f"{value:.1f}"

    if feature_name in {"MentHlth", "PhysHlth"}:
        return f"{int(value)} 天"

    return str(value)


def build_feature_schema_payload() -> List[Dict[str, object]]:
    payload = []
    for feature_name in FEATURE_ORDER:
        field_meta = FEATURE_SCHEMA[feature_name]
        payload.append(
            {
                "name": feature_name,
                "label": FEATURE_LABELS[feature_name],
                "group": FEATURE_GROUPS[feature_name],
                "meta": field_meta,
                "options": VALUE_OPTIONS.get(feature_name),
            }
        )
    return payload

