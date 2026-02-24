import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleCrawler:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.visited_urls = set()
        self.external_links = set()
        self.base_domain = None

    def is_external(self, url, base_url):
        if not url:
            return False

        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)

        if not parsed_url.netloc:
            return False

        return parsed_url.netloc != parsed_base.netloc

    def normalize_url(self, url, base_url):
        if not urlparse(url).netloc:
            return urljoin(base_url, url)
        return url

    async def fetch_page(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            logger.error(f"Ошибка загрузки {url}: {e}")
        return None

    def extract_links(self, html, base_url):
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for tag in soup.find_all('a', href=True):
            url = self.normalize_url(tag['href'], base_url)
            if url and url.startswith(('http://', 'https://')):
                links.append(url)

        return links

    async def crawl(self, session, url, depth):
        if depth > self.max_depth or url in self.visited_urls:
            return

        logger.info(f"Глубина {depth}: {url}")
        self.visited_urls.add(url)

        html = await self.fetch_page(session, url)
        if not html:
            return

        links = self.extract_links(html, url)

        for link in links:
            if self.is_external(link, url):
                self.external_links.add(link)

        tasks = []
        for link in links:
            if not self.is_external(link, url) and link not in self.visited_urls:
                tasks.append(self.crawl(session, link, depth + 1))

        if tasks:
            await asyncio.gather(*tasks)

    async def start(self, start_urls):
        if isinstance(start_urls, str):
            start_urls = [start_urls]

        self.base_domain = urlparse(start_urls[0]).netloc

        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl(session, url, 1) for url in start_urls]
            await asyncio.gather(*tasks)

        self.save_results()

    def save_results(self, filename="external_links.txt"):
        with open(filename, 'w', encoding='utf-8') as f:
            for link in sorted(self.external_links):
                f.write(link + '\n')

        logger.info(f"Найдено {len(self.external_links)} внешних ссылок")
        logger.info(f"Результаты сохранены в {filename}")


async def main():
    depth = 3

    crawler = SimpleCrawler(max_depth=depth)
    await crawler.start(["https://python.org", "https://docs.python.org"])


if __name__ == "__main__":
    asyncio.run(main())