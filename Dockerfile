# https://fastapi.tiangolo.com/deployment/docker/#build-a-docker-image-for-fastapi

FROM python:3.11 as requirements-stage

WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python -

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN /root/.local/bin/poetry export -f requirements.txt --output requirements.txt --without-hashes

WORKDIR /app

FROM python:3.11

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY backend .

CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
