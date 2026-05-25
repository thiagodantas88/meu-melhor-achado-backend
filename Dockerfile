FROM python:3.11-slim

ENV PYTHONIOENCODING=utf-8 \
    PYTHONUTF8=1 \
    PYTHONLEGACYWINDOWSSTDIO=utf-8 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
