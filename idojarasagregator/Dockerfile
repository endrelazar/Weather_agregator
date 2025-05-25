# Alap image: Python 3.9
FROM python:3.9-slim

# Munkakönyvtár beállítása a konténeren belül
WORKDIR /app

# Másold át a függőségeket tartalmazó fájlt
COPY requirements.txt .

# Telepítsd a függőségeket
RUN pip install --no-cache-dir -r requirements.txt

# Másold át az alkalmazás fájljait
COPY . .

# Port kitevése (dokumentációs célból)
EXPOSE 8000

# Az alkalmazás futtatása
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]