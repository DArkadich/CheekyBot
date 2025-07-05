FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Обновление pip до последней версии
RUN pip install --upgrade pip

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей с разрешением конфликтов
RUN pip install --no-cache-dir --upgrade setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директории для логов
RUN mkdir -p logs

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash bot && \
    chown -R bot:bot /app
USER bot

# Открытие порта (если понадобится для веб-хуков)
EXPOSE 8000

# Команда запуска
CMD ["python", "main.py"] 