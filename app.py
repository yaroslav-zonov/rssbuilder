from flask import Flask, Response, render_template_string
import feedparser
from bs4 import BeautifulSoup
import schedule
import time
import threading
from datetime import datetime

app = Flask(__name__)
new_entries = []
last_updated = None  # Переменная для хранения времени последнего обновления

def process_rss_feed(url):
    feed = feedparser.parse(url)
    processed_items = []

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        
        # Парсим описание с помощью BeautifulSoup
        description_html = entry.description
        soup = BeautifulSoup(description_html, 'html.parser')

        # Убираем изображение в начале description
        img_tag = soup.find('img')
        if img_tag:
            img_src = img_tag['src'] if 'src' in img_tag.attrs else ''
            img_tag.decompose()  # Удаляем тег <img>

            # Находим новое изображение и заменяем scale_avatar на scale_large
            if 'scale_avatar' in img_src:
                new_img_url = img_src.replace('scale_avatar', 'scale_large')
            else:
                new_img_url = img_src
        else:
            new_img_url = ''

        # Создаем новый формат записи
        processed_item = {
            'title': title,
            'link': link,
            'description': str(soup),
            'media_thumbnail': new_img_url
        }
        processed_items.append(processed_item)

    return processed_items

def update_rss_feed():
    global new_entries, last_updated
    url = 'http://example.com/rss'  # Замените на ваш RSS URL
    new_entries = process_rss_feed(url)
    last_updated = datetime.now()  # Обновляем время последнего изменения

@app.route('/')
def home():
    return render_template_string('''
        <h1>Главная страница</h1>
        <p>Время последнего обновления: {{ last_updated }}</p>
        <p><a href="/rss">Ссылка на RSS поток</a></p>
    ''', last_updated=last_updated)

@app.route('/rss')
def rss_feed():
    # Формирование нового RSS потока
    rss_content = '<?xml version="1.0" encoding="UTF-8"?>'
    rss_content += '<rss version="2.0"><channel><title>My RSS Feed</title><link>http://example.com</link><description>This is a custom RSS feed</description>'
    
    for entry in new_entries:
        rss_content += f'<item><title>{entry["title"]}</title><link>{entry["link"]}</link><description>{entry["description"]}</description><media:thumbnail url="{entry["media_thumbnail"]}"/></item>'
    
    rss_content += '</channel></rss>'
    return Response(rss_content, mimetype='application/rss+xml')

def run_schedule():
    schedule.every(30).minutes.do(update_rss_feed)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запускаем фоновую задачу в отдельном потоке
threading.Thread(target=run_schedule, daemon=True).start()

if __name__ == '__main__':
    update_rss_feed()  # Начальное обновление RSS потока
    app.run(debug=True)
