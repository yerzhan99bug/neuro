from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserOut, UserLogin
from utils import hash_password, verify_password, create_access_token
from database import SessionLocal

router = APIRouter()

# 📦 Зависимость для подключения к БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔐 РЕГИСТРАЦИЯ
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")

    hashed = hash_password(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed,
        name=user.name,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.from_orm(new_user)
    }

# 🔑 ВХОД
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserOut.from_orm(db_user)
    }