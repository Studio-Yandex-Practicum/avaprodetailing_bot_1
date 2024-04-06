from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from app.core.external_functions import check_work_mode

load_dotenv()

APP_TITLE = 'Система лояльности AVA Pro Detailing'

ALLOWED_CHARS = 'АВЕКМНОРСТУХ'

MIN_LENGTH_BRAND_MODEL_ERROR = 'Поле не может быть пустым.'
MAX_LENGTH_BRAND_MODEL_ERROR = 'Название не может быть более 50 символов.'
MIN_LENGTH_STR = 1
MAX_LENGTH_BRAND_MODEL = 50
MIN_LENGTH_NUMBER_PLATE = 8
MAX_LENGTH_NUMBER_PLATE = 9
MAX_LENGTH_USER_STRING = 100

LENGTH_NUMBER_PLATE_ERROR = 'Длина номера автомобиля должна быть 8-9 символов.'
NUMBER_PLATE_FORMAT_ERROR = (
    'Неверный формат номера. '
    'Номер нужно вводить в формате А000АА00 или А000АА000. '
    'Пожалуйста, используйте кириллицу.'
)


class Settings(BaseSettings):
    app_title: str = APP_TITLE
    database_url: str = check_work_mode('TEST_MODE')

    class Config:
        env_file = '.env'


settings = Settings()
