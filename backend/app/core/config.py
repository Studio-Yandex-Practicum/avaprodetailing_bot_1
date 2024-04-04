from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from app.core.external_functions import check_work_mode

load_dotenv()

APP_TITLE = 'Система лояльности AVA Pro Detailing'


class Settings(BaseSettings):
    app_title: str = APP_TITLE
    database_url: str = check_work_mode('TEST_MODE')

    class Config:
        env_file = '.env'


settings = Settings()
