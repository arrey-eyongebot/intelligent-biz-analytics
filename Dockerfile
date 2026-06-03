# Change WORKDIR to point directly to backend
WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/uploads

CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app