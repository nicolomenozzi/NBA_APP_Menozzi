FROM python:3.12-slim

# Cartella di lavoro dentro il container
WORKDIR /app

# Copia requirements.txt e installa Tornado
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutti i file del progetto
COPY . .

# Porta su cui gira Tornado
EXPOSE 8888

# Comando per avviare il server
CMD ["python", "serverMatches.py"]
