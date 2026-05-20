# debug_parser.py - скрипт для анализа структуры сайта
import requests
from bs4 import BeautifulSoup
import json

def analyze_website(url):
    """Анализирует структуру сайта и помогает найти селекторы для новостей"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Ищем потенциальные контейнеры с новостями
    possible_containers = [
        'article', 'div.news-item', 'div.news', 'div.article',
        'div.post', 'div.preview', 'li.news-item', '.item'
    ]
    
    results = {}
    for selector in possible_containers:
        elements = soup.select(selector)
        if elements:
            results[selector] = len(elements)
            # Сохраняем пример первого элемента
            if elements:
                first_item = elements[0]
                # Ищем заголовки внутри
                titles = first_item.select('h1, h2, h3, h4, .title, .headline')
                if titles:
                    print(f"\nСелектор: {selector}")
                    print(f"Найдено элементов: {len(elements)}")
                    print(f"Пример заголовка: {titles[0].get_text(strip=True)[:100]}")
                    print(f"Ссылка: {first_item.find('a').get('href') if first_item.find('a') else 'не найдена'}")
    
    return results

if __name__ == "__main__":
    url = input("Введите URL сайта для анализа: ")
    analyze_website(url)