# scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class ScraperError(Exception):
    """Базовое исключение для ошибок скрейпинга."""
    pass


class NetworkError(ScraperError):
    """Ошибка сети / недоступность сайта."""
    pass


class ParsingError(ScraperError):
    """Ошибка при разборе HTML-структуры."""
    pass


class InvalidURLError(ScraperError):
    """Некорректный URL."""
    pass


class NewsScraper:
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _validate_url(self):
        """Проверяет корректность URL."""
        parsed = urlparse(self.url)
        if not parsed.scheme or not parsed.netloc:
            raise InvalidURLError(f"Некорректный URL: {self.url}")

    def fetch_headlines(self, limit=20):
        """
        Извлекает заголовки новостей.
        Возвращает список словарей: {'title': str, 'link': str}
        """
        self._validate_url()

        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Ошибка сети: {e}")

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            headlines = []

            # Адаптированные селекторы для BBC News
            candidates = soup.select('h2[class*="title"], h3[class*="title"], '
                                    'h2[class*="headline"], h3[class*="headline"], '
                                    '[data-testid="card-headline"], .gs-c-promo-heading')

            if not candidates:
                candidates = soup.select('article h2, article h3, .gs-u-mt h3')

            for tag in candidates[:limit]:
                title = tag.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                link_tag = tag.find_parent('a')
                if not link_tag:
                    link_tag = tag.find('a')
                link = link_tag.get('href') if link_tag else ''
                if link and not link.startswith('http'):
                    link = f"https://www.bbc.com{link}"

                headlines.append({
                    'title': title,
                    'link': link if link else '#'
                })

            if not headlines:
                raise ParsingError("Не удалось найти заголовки. Возможно, структура сайта изменилась.")

            return headlines

        except Exception as e:
            raise ParsingError(f"Ошибка парсинга: {e}") 