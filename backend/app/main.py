from fastapi import FastAPI

app = FastAPI(title="Stock Tracker and Planner API")


@app.get("/health")
def health_check():
    return {"status": "ok"}
