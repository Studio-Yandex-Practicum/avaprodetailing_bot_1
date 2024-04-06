from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from fastapi.staticfiles import StaticFiles

app = FastAPI(title=settings.app_title)
staticfiles = StaticFiles(directory="static")
app.mount("/static", staticfiles, name="static")

app.include_router(main_router)
