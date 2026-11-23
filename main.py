import requests
from bs4 import BeautifulSoup
import time

# 1. Ключевые слова (можно менять под задание)
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

def parse_habr():
    url = 'https://habr.com/ru/articles/'

    # Расширенные заголовки, чтобы выглядеть как реальный браузер
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    # Пытаемся выполнить запрос с повторными попытками
    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            print(f"Попытка {attempt + 1} из {max_retries}...")
            # Создаём сессию для сохранения cookies
            session = requests.Session()
            # Увеличиваем таймаут до 20 секунд
            response = session.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            break  # Если успешно, выходим из цикла
        except requests.exceptions.Timeout:
            print(f"❌ Таймаут при попытке {attempt + 1}. Повторяем...")
            time.sleep(2)  # Пауза перед повтором
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса: {e}")
            return

    if not response or response.status_code != 200:
        print("❌ Не удалось загрузить страницу после нескольких попыток.")
        print("Проверьте доступ к сайту в браузере. Возможно, нужен VPN.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    print("✅ Страница загружена, длина HTML:", len(response.text))

    # 2. Находим основной контейнер с классом tm-layout__wrapper
    wrapper = soup.find('div', class_='tm-layout__wrapper')
    if not wrapper:
        print("❌ Контейнер tm-layout__wrapper не найден!")
        wrapper = soup.find('div', class_='tm-articles-list')
        if wrapper:
            print("✅ Найден альтернативный контейнер: tm-articles-list")
        else:
            print("❌ Альтернативный контейнер тоже не найден. Выводим заголовок страницы для проверки:")
            print(soup.title.string if soup.title else "Тег title отсутствует")
            return
    else:
        print("✅ Контейнер tm-layout__wrapper найден.")

    # 3. Ищем все статьи внутри этого контейнера
    articles = wrapper.find_all('article')
    print(f"Найдено тегов <article> внутри контейнера: {len(articles)}")

    if not articles:
        articles = wrapper.find_all('div', class_='tm-article-snippet')
        print(f"Найдено div.tm-article-snippet: {len(articles)}")

    if not articles:
        print("❌ Статьи не найдены ни по одному селектору.")
        return

    # 4. Обрабатываем найденные статьи
    found_any = False
    for article in articles:
        title_tag = article.find('h2')
        if not title_tag:
            title_tag = article.find(['h2', 'h3', 'a'], class_=lambda c: c and 'title' in c.lower())

        if not title_tag:
            continue

        link_tag = title_tag.find('a')
        if not link_tag:
            link_tag = article.find('a', class_=lambda c: c and 'title' in c.lower()) or article.find('a')

        if not link_tag or not link_tag.get('href'):
            continue

        title = title_tag.get_text(strip=True)
        link = link_tag.get('href')
        if link and link.startswith('/'):
            link = 'https://habr.com' + link

        time_tag = article.find('time')
        date_str = time_tag.get('datetime') if time_tag else 'Дата не найдена'

        full_text = article.get_text(separator=' ', strip=True).lower()
        found = any(keyword.lower() in full_text for keyword in KEYWORDS)

        if found:
            found_any = True
            print(f"{date_str} – {title} – {link}")

    if not found_any:
        print("\nℹ️ Статьи найдены, но ни одна не содержит ключевых слов:", KEYWORDS)
        print("\n--- Отладка: первые 5 заголовков найденных статей ---")
        for i, article in enumerate(articles[:5]):
            t = article.find('h2') or article.find('h3')
            if t:
                print(f"{i+1}. {t.get_text(strip=True)}")

if __name__ == '__main__':
    parse_habr()