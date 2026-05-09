FROM python:3.11-slim

WORKDIR /app

COPY dettrace_platform/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY dettrace_platform /app

EXPOSE 8010

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
