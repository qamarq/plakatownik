FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY themes ./themes
COPY fonts ./fonts

ENV CACHE_DIR=/app/data/cache \
    POSTERS_DIR=/app/data/posters \
    THEMES_DIR=/app/themes \
    FONTS_DIR=/app/fonts \
    MPLBACKEND=Agg

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
