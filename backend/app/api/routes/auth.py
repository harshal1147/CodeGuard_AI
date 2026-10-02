from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> dict:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return {
        "success": True,
        "data": {
            "user": UserResponse(id=user.id, name=user.name, email=user.email).model_dump(),
            "token": token,
        },
    }


@router.post("/login", response_model=dict)
def login_user(payload: UserLogin, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token(user.id)
    return {
        "success": True,
        "data": {
            "user": UserResponse(id=user.id, name=user.name, email=user.email).model_dump(),
            "token": token,
        },
    }


@router.get("/me", response_model=dict)
def get_current_user_profile(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "success": True,
        "data": UserResponse(id=current_user.id, name=current_user.name, email=current_user.email).model_dump(),
    }
