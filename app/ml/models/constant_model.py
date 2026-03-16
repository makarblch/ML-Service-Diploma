class ConstantTurnoverModel:
    """
    Dummy model used for development and testing.
    Always returns constant turnover prediction.
    """

    def __init__(self, value: float = 1_000_000):
        self.value = value

    def predict(self, features: dict) -> float:
        return self.value