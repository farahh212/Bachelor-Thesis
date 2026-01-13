# Alternative Dockerfile if you need PORT environment variable support
# Use this if Railway requires PORT to be read from environment

FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Create startup script that reads PORT from environment
RUN echo '#!/bin/sh\nPORT=${PORT:-8000}\nexec uvicorn main:app --host 0.0.0.0 --port "$PORT"' > /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]

