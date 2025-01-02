import feedparser
from bs4 import BeautifulSoup
import schedule
import time
import os

# URL RSS-канала (замените на реальный URL)
rss_url = 'https://comicsdb.ru/rss'  # Замените на реальный RSS URL
output_rss_file = 'cbdbrss.xml'  # Имя выходного файла

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

def generate_modified_rss(processed_items):
    rss_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss_content += '<rss version="2.0">\n'
    rss_content += '<channel>\n'
    rss_content += '<title>Translation DB</title>\n'
    rss_content += '<link>http://example.com/modified_feed</link>\n'
    rss_content += '<description>База переводов комиксов.</description>\n'

    for item in processed_items:
        rss_content += '<item>\n'
        rss_content += f'<title>{item["title"]}</title>\n'
        rss_content += f'<link>{item["link"]}</link>\n'
        rss_content += f'<description>{item["description"]}</description>\n'
        rss_content += f'<media_thumbnail>{item["media_thumbnail"]}</media_thumbnail>\n'
        rss_content += '</item>\n'

    rss_content += '</channel>\n'
    rss_content += '</rss>'

    # Сохранение измененного RSS в файл
    with open(output_rss_file, 'w', encoding='utf-8') as f:
        f.write(rss_content)

    return os.path.abspath(output_rss_file)  # Возвращаем полный путь к файлу

def job():
    print("Запуск обработки RSS-канала...")
    items = process_rss_feed(rss_url)
    modified_rss_path = generate_modified_rss(items)
    
    # Выводим URL к измененному RSS-файлу
    print(f"Измененный RSS доступен по адресу: file://{modified_rss_path}")

# Запланировать выполнение задачи каждые 30 минут
schedule.every(30).minutes.do(job)

if __name__ == '__main__':
    job()  # Выполнить сразу при запуске
    while True:
        schedule.run_pending()
        time.sleep(1)