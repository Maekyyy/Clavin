# Używamy nowszego, szybszego Pythona
FROM python:3.11-slim

WORKDIR /app

# Instalacja zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu
COPY . .

# Ważne: W Cloud Run Serverless używamy gunicorn, nie python bot.py
# main:app oznacza: plik main.py, obiekt app
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app