# Minimal Python image
FROM python:3.10-slim

# Tizimni yangilash va kerakli kutubxonalarni o‘rnatish
RUN apt-get update && apt-get install -y \
    libreoffice \
    fonts-dejavu \
    libxext6 \
    libxrender1 \
    libglib2.0-0 \
    libsm6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ishchi katalog
WORKDIR /app

# Python kutubxonalarni o‘rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha fayllarni ko‘chirish
COPY . .

# Port
EXPOSE 8000

# Flask appni ishga tushirish
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
