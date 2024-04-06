from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title=settings.app_title)


@app.get("/")
async def root():
    return {"message": "Проверка сервера"}
