FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy everything including start.sh in ONE step
COPY . .

RUN mkdir -p data/uploads

RUN chmod +x start.sh

# Don't hardcode 5000 — Railway injects PORT dynamically
EXPOSE 8080

# Shell form — properly expands $PORT at runtime
CMD ["sh", "-c", "./start.sh"]