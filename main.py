from fastapi import FastAPI
from database import Base, engine
import models
from auth.routes import router as auth_router

# Создание таблиц в БД (создаёт все поля, которые есть в models.py)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "🚀 FastAPI сервер запущен!"}