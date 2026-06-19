from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import health, auth

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router)
if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True
    )