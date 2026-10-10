FROM python:3.12-slim

WORKDIR /app

# Abhaengigkeiten zuerst kopieren -> Layer-Cache bleibt bei Code-Aenderungen erhalten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Restlichen Code kopieren
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
