from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI(title=settings.app_title)
app.add_middleware(HTTPSRedirectMiddleware)


@app.get("/")
async def root():
    return {"message": "Проверка сервера"}
