from pydantic import Field, HttpUrl, field_validator

from app.core.enums import CompanySize
from app.schemas.common import BaseSchema


class PredictionFeatures(BaseSchema):
    final_income: float = Field(..., ge=0)
    payments_bki: float = Field(..., ge=0)
    pti_bki: float = Field(..., ge=0)
    transaction_amt: float = Field(..., ge=0)
    company_size: CompanySize
    company_age: int = Field(..., ge=0)

    @field_validator("pti_bki")
    @classmethod
    def validate_pti_bki(cls, value: float) -> float:
        if value > 10:
            raise ValueError("pti_bki is out of allowed range")
        return value


class PredictJobRequest(BaseSchema):
    job_id: str = Field(..., min_length=1, max_length=64)
    features: PredictionFeatures
    callback_url: HttpUrl
    model_version: str | None = Field(default=None, max_length=64)