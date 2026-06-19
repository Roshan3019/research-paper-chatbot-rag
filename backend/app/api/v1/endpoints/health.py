from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "Healthy",
        "service": "research-paper-chatbot-api"
    }