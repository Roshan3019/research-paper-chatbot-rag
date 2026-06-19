from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import health

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.include_router(health.router, tags=["health"])

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True
    )