# Используйте официальный образ Python
FROM python:3.9-slim

# Установите рабочую директорию
WORKDIR /app

# Скопируйте файлы в контейнер
COPY . .

# Установите зависимости (если у вас есть requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Укажите команду для запуска вашего приложения
CMD ["python", "rss_processor.py"]

# Укажите порт, который ваше приложение будет использовать
EXPOSE 8080
