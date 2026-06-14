# router_models.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal

# 锁死企业级5大核心意图
IntentType = Literal["FACT_QA", "PROCEDURE", "TROUBLESHOOTING", "COMPARE", "CONFIGURATION"]

class RouterOutput(BaseModel):
    """第一层：Pydantic 契约网"""
    intent: IntentType = Field(description="必须且只能是 5 大核心意图之一")
    confidence: float = Field(description="意图识别置信度，0.0 到 1.0 之间")

    @field_validator("confidence")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("置信度必须在 0.0 到 1.0 之间")
        return v
