from fastapi import FastAPI

app = FastAPI(title="F1 API Health Check")

@app.get("/")
async def root():
    return {
        "message": "F1 Driver API is Live",
        "status": "Operational",
        "version": "1.0.0"
    }
