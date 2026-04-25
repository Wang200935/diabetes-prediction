from typing import Dict, List

from app.domain import FEATURE_LABELS, classify_risk


def build_attention_points(features: Dict[str, float]) -> List[Dict[str, str]]:
    points = []

    def add(feature_name: str, title: str, detail: str, severity: str) -> None:
        points.append(
            {
                "feature": feature_name,
                "label": FEATURE_LABELS.get(feature_name, feature_name),
                "title": title,
                "detail": detail,
                "severity": severity,
            }
        )

    if features["BMI"] >= 30:
        add("BMI", "BMI 偏高", "體重指標偏高通常會推升糖尿病風險，建議優先處理飲食與活動量。", "high")
    elif features["BMI"] >= 25:
        add("BMI", "BMI 稍高", "體重指標已進入需要留意的區間，可先從飲食與運動穩定調整。", "watch")

    if features["HighBP"] == 1:
        add("HighBP", "高血壓訊號", "血壓問題常與糖尿病風險一起出現，建議與醫師追蹤血壓控制。", "high")

    if features["HighChol"] == 1:
        add("HighChol", "高膽固醇訊號", "膽固醇異常與代謝風險相關，建議同時注意飲食與抽血追蹤。", "watch")

    if features["PhysActivity"] == 0:
        add("PhysActivity", "活動量不足", "規律活動不足會讓代謝風險提高，可先建立每週穩定運動節奏。", "watch")

    if features["Smoker"] == 1:
        add("Smoker", "吸菸習慣", "吸菸會增加心血管與代謝負擔，是需要優先處理的風險因子。", "high")

    if features["HvyAlcoholConsump"] == 1:
        add("HvyAlcoholConsump", "重度飲酒", "酒精攝取過量會增加代謝與肝臟負擔，建議減量或尋求專業協助。", "watch")

    if features["GenHlth"] >= 4:
        add("GenHlth", "整體健康評價偏低", "你對目前健康狀況的自評較差，通常代表已有多項需要追蹤的問題。", "high")

    if features["PhysHlth"] >= 14:
        add("PhysHlth", "身體不適天數偏多", "近期身體不舒服的天數較多，建議安排醫療評估而不是只看單次預測。", "high")
    elif features["PhysHlth"] >= 7:
        add("PhysHlth", "身體不適需要留意", "近期身體不適天數已有累積，建議開始記錄生活型態與症狀。", "watch")

    if features["MentHlth"] >= 14:
        add("MentHlth", "心理壓力偏高", "心理壓力與慢性病管理息息相關，建議同步照顧睡眠與心理健康。", "watch")

    if features["DiffWalk"] == 1:
        add("DiffWalk", "行動困難", "活動受限會降低日常能量消耗，也可能反映整體健康負擔較高。", "watch")

    if features["Age"] >= 60:
        add("Age", "年齡層風險上升", "年齡增長會提高代謝疾病風險，定期檢查的重要性也會提高。", "watch")

    return points[:5]


def build_recommendations(features: Dict[str, float], probability: float) -> List[Dict[str, str]]:
    risk = classify_risk(probability)
    recommendations = [
        {
            "title": "安排正式檢查",
            "description": "這個結果是風險預估，不是醫療診斷。若分數偏高，建議安排血糖或 HbA1c 檢查。",
            "priority": "high" if risk["token"] in {"elevated", "high"} else "medium",
        }
    ]

    if features["BMI"] >= 25:
        recommendations.append(
            {
                "title": "先從體重管理開始",
                "description": "把目標放在穩定飲食、總熱量控制與每週固定活動量，通常比一次做很多更容易持續。",
                "priority": "high",
            }
        )

    if features["PhysActivity"] == 0:
        recommendations.append(
            {
                "title": "建立規律運動節奏",
                "description": "先以可持續為主，例如每週 150 分鐘快走、室內單車或低衝擊有氧運動。",
                "priority": "medium",
            }
        )

    if features["HighBP"] == 1 or features["HighChol"] == 1:
        recommendations.append(
            {
                "title": "同步追蹤血壓與血脂",
                "description": "糖尿病風險常和高血壓、高膽固醇一起出現，建議把三者放在同一套追蹤習慣中。",
                "priority": "medium",
            }
        )

    if features["Smoker"] == 1 or features["HvyAlcoholConsump"] == 1:
        recommendations.append(
            {
                "title": "優先調整吸菸或飲酒",
                "description": "若同時存在吸菸或重度飲酒，先處理這些行為通常能同時改善多項慢性病風險。",
                "priority": "medium",
            }
        )

    if features["MentHlth"] >= 14 or features["PhysHlth"] >= 14:
        recommendations.append(
            {
                "title": "把心理與身體狀態一起管理",
                "description": "若近期心理或身體不適天數很多，建議不要只看飲食與運動，也要留意睡眠、壓力與就醫追蹤。",
                "priority": "medium",
            }
        )

    if risk["token"] == "low":
        recommendations.append(
            {
                "title": "維持現有健康習慣",
                "description": "目前風險相對較低，但仍建議持續規律運動、控制體重並定期檢查。",
                "priority": "low",
            }
        )

    return recommendations[:4]
