from app.ml.models.constant_model import ConstantTurnoverModel


class ModelLoader:

    _models = {
        "v1.0.0": ConstantTurnoverModel(value=1_000_000)
    }

    @classmethod
    def get_model(cls, version: str):
        if version not in cls._models:
            raise ValueError(f"Model version {version} not found")

        return cls._models[version]