FROM python:3.10-slim
WORKDIR /app
COPY pyproject.toml poetry.lock /
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false && poetry install
COPY /backend .
COPY .env .
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]