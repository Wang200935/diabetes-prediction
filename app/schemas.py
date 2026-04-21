from typing import Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    HighBP: int = Field(ge=0, le=1)
    HighChol: int = Field(ge=0, le=1)
    BMI: float = Field(ge=10, le=80)
    Smoker: int = Field(ge=0, le=1)
    Stroke: int = Field(ge=0, le=1)
    HeartDiseaseorAttack: int = Field(ge=0, le=1)
    PhysActivity: int = Field(ge=0, le=1)
    HvyAlcoholConsump: int = Field(ge=0, le=1)
    NoDocbcCost: int = Field(ge=0, le=1)
    GenHlth: int = Field(ge=1, le=5)
    MentHlth: int = Field(ge=0, le=30)
    PhysHlth: int = Field(ge=0, le=30)
    DiffWalk: int = Field(ge=0, le=1)
    Age: int = Field(ge=18, le=120)
    Education: int = Field(ge=1, le=6)
    Income: int = Field(ge=1, le=8)


class AttentionPoint(BaseModel):
    feature: str
    label: str
    title: str
    detail: str
    severity: Literal["watch", "high"]


class Recommendation(BaseModel):
    title: str
    description: str
    priority: Literal["low", "medium", "high"]


class PredictionOutput(BaseModel):
    predicted_class: int
    result_summary: str
    risk_probability: float
    risk_level: str
    risk_token: Literal["low", "medium", "elevated", "high"]
    disclaimer: str
    input_summary: Dict[str, str]
    attention_points: List[AttentionPoint]
    recommendations: List[Recommendation]


class HealthOutput(BaseModel):
    status: str
    model_loaded: bool
