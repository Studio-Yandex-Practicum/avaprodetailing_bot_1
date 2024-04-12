FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /

RUN pip install --no-cache-dir poetry==1.8.2 && poetry config virtualenvs.create false && poetry install

COPY /backend .

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh", "/app/entrypoint.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips='*'"]
