FROM python:3.11-slim

# system deps for playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates gnupg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libasound2 libxshmfence1 \
    fonts-liberation libgbm1 libpangocairo-1.0-0 libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright browsers
RUN playwright install --with-deps chromium

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
