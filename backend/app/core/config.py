from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from .external_functions import check_work_mode

load_dotenv()

APP_TITLE = 'Система лояльности AVA Pro Detailing'
DATABASE = check_work_mode('TEST_MODE')


class Settings(BaseSettings):
    app_title: str = APP_TITLE
    database_url: str = check_work_mode('TEST_MODE')

    class Config:
        env_file = '.env'


settings = Settings()
