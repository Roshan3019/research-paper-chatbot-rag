from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import user_repository
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserRegister

def register_user(
        db:Session,
        data:UserRegister
):
    if user_repository.get_user_by_email(
        db, data.email
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed = hash_password(data.password)
    print(data.password)
    print(type(data.password))
    print(len(data.password))
    return user_repository.create_user(db, data.email, data.username, hashed)


def login_user(
        db:Session, 
        email:str,
        password:str
) -> str:
    user = user_repository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return create_access_token({"sub":user.id})