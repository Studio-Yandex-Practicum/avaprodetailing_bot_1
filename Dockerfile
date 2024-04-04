# https://fastapi.tiangolo.com/deployment/docker/#build-a-docker-image-for-fastapi

FROM python:3.11 as requirements-stage

WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python -

RUN export PATH="/tmp/.local/bin:$PATH"

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

WORKDIR /app

FROM python:3.11

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY backend .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
