import asyncio
import aiohttp
import aiofiles
from pathlib import Path
import mimetypes
from urllib.parse import urlparse
import time


async def save_cat_async(content: bytes, file_path: str):
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    print(f"✅ Кот сохранён: {file_path}")


async def download_cat_async(session, url, save_dir, idx):
    try:
        async with session.get(url, allow_redirects=True) as response:
            if response.status != 200:
                print(f"❌ [Асинх {idx}] Ошибка {url}: статус {response.status}")
                return None

            content = await response.read()

            content_type = response.headers.get('content-type', '')
            ext = mimetypes.guess_extension(content_type.split(';')[0]) or '.jpg'

            parsed = urlparse(str(response.url))
            filename = Path(parsed.path).name
            if not filename or '.' not in filename:
                filename = f"cat_{idx}"

            file_path = Path(save_dir) / f"{filename}{ext}"

            await save_cat_async(content, file_path)
            return file_path

    except Exception as e:
        print(f"❌ [Асинх {idx}] Ошибка при загрузке {url}: {e}")
        return None


async def download_cats_async_main(urls, save_dir):
    Path(save_dir).mkdir(exist_ok=True)

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [download_cat_async(session, url, save_dir, i)
                 for i, url in enumerate(urls)]
        results = await asyncio.gather(*tasks)

    elapsed_time = time.time() - start_time
    successful = sum(1 for r in results if r is not None)

    return {
        'time': elapsed_time,
        'successful': successful,
        'total': len(urls),
        'results': results
    }


def download_cats_async(urls, save_dir):
    return asyncio.run(download_cats_async_main(urls, save_dir))


if __name__ == "__main__":
    test_urls = [
        "https://cataas.com/cat",
        "https://http.cat/200",
        "https://http.cat/404"
    ]
    result = download_cats_async(test_urls, "test_async")
    print(f"Загружено {result['successful']} из {result['total']} за {result['time']:.2f} сек")