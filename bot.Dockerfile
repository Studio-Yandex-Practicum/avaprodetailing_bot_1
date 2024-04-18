FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /

RUN pip install --no-cache-dir poetry==1.8.2 && poetry config virtualenvs.create false && poetry install

COPY /bot .

CMD ["python3", "main.py"]

# CMD ["poetry", "run", "python", "-m", "telegram_bot"]
