# Minimal Python image
FROM python:3.10-slim

# LibreOffice va kerakli paketlarni o'rnatish
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu \
    && apt-get clean

# Ishchi papka
WORKDIR /app

# Fayllarni ko‘chirish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Port
EXPOSE 8000

# Flask appni ishga tushirish
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
