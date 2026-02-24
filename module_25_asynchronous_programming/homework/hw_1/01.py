import asyncio
import aiohttp
from pathlib import Path
import mimetypes
from urllib.parse import urlparse

def save_cat_sync(content: bytes, file_path: str):
    with open(file_path, 'wb') as f:
        f.write(content)
    print(f"✅ Кот сохранён: {file_path}")

async def download_cat(session, url, save_dir):
    try:
        async with session.get(url, allow_redirects=True) as response:
            if response.status != 200:
                print(f"❌ Ошибка {url}: статус {response.status}")
                return None

            content = await response.read()

            content_type = response.headers.get('content-type', '')
            ext = mimetypes.guess_extension(content_type.split(';')[0]) or '.jpg'

            parsed = urlparse(str(response.url))
            filename = Path(parsed.path).name
            if not filename or '.' not in filename:
                filename = f"cat_{hash(url)}"

            file_path = Path(save_dir) / f"{filename}{ext}"

            await asyncio.to_thread(save_cat_sync, content, file_path)
            return file_path

    except Exception as e:
        print(f"❌ Ошибка при загрузке {url}: {e}")
        return None

async def main():
    urls = [
        "https://cataas.com/cat",
        "https://http.cat/200",
        "https://http.cat/404",
        "https://cataas.com/cat/says/Hello%20World",
        "https://cataas.com/cat/gif",
    ]

    save_dir = "downloaded_cats"
    Path(save_dir).mkdir(exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = [download_cat(session, url, save_dir) for url in urls]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r is not None)
        print(f"\n📊 Загружено {successful} из {len(urls)} котов")

if __name__ == "__main__":
    asyncio.run(main())