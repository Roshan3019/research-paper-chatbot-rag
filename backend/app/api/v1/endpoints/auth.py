from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, Token
from app.services import auth_service
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    return auth_service.register_user(db, data)

@router.post("/login", response_model=Token)
def login(
    data:UserLogin,
    db: Session = Depends(get_db)
):
    token = auth_service.login_user(
        db, data.email, data.password
    )
    return {
        "access_token": token
    }

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

