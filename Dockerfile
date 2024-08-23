# Python 3.11 slim image'ını kullanıyoruz
FROM python:3.11-slim

# Çalışma dizinini ayarlıyoruz
WORKDIR /app

# Gerekli bağımlılıkları yüklemek için requirements.txt dosyasını kopyalıyoruz
COPY requirements.txt .

# Bağımlılıkları kuruyoruz
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyalıyoruz
COPY . .

# Uygulamayı başlatıyoruz
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
