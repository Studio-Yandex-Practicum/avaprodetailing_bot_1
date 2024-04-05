import os
from distutils.util import strtobool


def check_work_mode(mode: str) -> str:
    return (
        os.getenv('SQLITE_DATABASE_URL')
        if bool(strtobool(os.getenv(mode, 'True')))
        else (
            f'postgresql://{os.getenv("POSTGRESQL_DATABASE_USER")}:'
            f'{os.getenv("POSTGRESQL_DATABASE_PASSWORD")}'
            f'@{os.getenv("POSTGRESQL_DATABASE_HOST")}'
            f'/{os.getenv("POSTGRESQL_DATABASE_NAME")}'
        )
    )
