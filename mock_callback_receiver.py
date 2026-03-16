from fastapi import FastAPI

app = FastAPI()


@app.post("/api/internal/v1/mock/callbacks/predictions")
async def receive_callback(payload: dict):
    print("CALLBACK RECEIVED:")
    print(payload)
    return {"status": "ok"}