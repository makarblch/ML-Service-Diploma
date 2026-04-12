import pandas as pd
from enum import Enum


class PredictionInputBuilder:
    COMPANY_SIZE_MAPPING = {
        "SE": 0,
        "ME": 1,
        "LE": 2,
    }

    @staticmethod
    def _normalize_value(feature_name, value):
        if isinstance(value, Enum):
            value = value.value

        if feature_name == "company_size":
            return PredictionInputBuilder.COMPANY_SIZE_MAPPING.get(value)

        return value

    @staticmethod
    def build_dataframe(features: dict, feature_order: list[str]) -> pd.DataFrame:
        row = {
            feature_name: PredictionInputBuilder._normalize_value(
                feature_name,
                features.get(feature_name),
            )
            for feature_name in feature_order
        }
        return pd.DataFrame([row])