import httpx

from app.schemas.callback_payload import PredictionCallbackPayload


class CallbackService:
    def __init__(self, timeout_seconds: float = 5.0) -> None:
        self.timeout_seconds = timeout_seconds

    def send_prediction_callback(
        self,
        callback_url: str,
        payload: PredictionCallbackPayload,
    ) -> None:
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                callback_url,
                json=payload.model_dump(mode="json"),
            )
            response.raise_for_status()