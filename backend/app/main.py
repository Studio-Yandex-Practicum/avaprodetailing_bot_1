from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from fastapi.staticfiles import StaticFiles


app = FastAPI(title=settings.app_title)


@app.get("/")
async def root():
    return {"message": "Проверка сервера"}

app.include_router(main_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
