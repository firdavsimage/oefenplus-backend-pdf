FROM python:3.10-slim

# LibreOffice va boshqa zarur paketlarni o'rnatish
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu \
    locales \
    && apt-get clean

# Ishchi katalog
WORKDIR /app

# Python kutubxonalarini o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyihani ichkariga nusxalash
COPY . .

# Port ochish
EXPOSE 8000

# Flask ilovasini ishga tushirish
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
