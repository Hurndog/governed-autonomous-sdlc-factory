FROM python:3.12-slim
WORKDIR /app
COPY apps/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api/ ./apps/api/
COPY packages/ ./packages/
EXPOSE 8000
CMD ["uvicorn", "apps.api.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
