import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import mimetypes
from urllib.parse import urlparse
import time


def download_cat_thread(url, save_dir, idx):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        if response.status_code != 200:
            print(f"❌ [Тред {idx}] Ошибка {url}: статус {response.status_code}")
            return None

        content_type = response.headers.get('content-type', '')
        ext = mimetypes.guess_extension(content_type.split(';')[0]) or '.jpg'

        parsed = urlparse(str(response.url))
        filename = Path(parsed.path).name
        if not filename or '.' not in filename:
            filename = f"cat_{idx}"

        file_path = Path(save_dir) / f"{filename}{ext}"

        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"✅ [Тред {idx}] Кот сохранён: {file_path}")
        return file_path

    except requests.exceptions.Timeout:
        print(f"❌ [Тред {idx}] Таймаут при загрузке {url}")
        return None
    except Exception as e:
        print(f"❌ [Тред {idx}] Ошибка при загрузке {url}: {e}")
        return None


def download_cats_threads(urls, save_dir, max_workers=5):
    Path(save_dir).mkdir(exist_ok=True)

    start_time = time.time()
    results = []

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(download_cat_thread, url, save_dir, i)
                       for i, url in enumerate(urls)]

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    print(f"❌ Ошибка в треде: {e}")
                    results.append(None)

    except KeyboardInterrupt:
        print("\n⚠️ Треды прерваны пользователем")
        return {
            'time': time.time() - start_time,
            'successful': sum(1 for r in results if r is not None),
            'total': len(urls),
            'results': results
        }

    elapsed_time = time.time() - start_time
    successful = sum(1 for r in results if r is not None)

    return {
        'time': elapsed_time,
        'successful': successful,
        'total': len(urls),
        'results': results
    }


if __name__ == "__main__":
    test_urls = [
        "https://cataas.com/cat",
        "https://http.cat/200",
        "https://http.cat/404"
    ]
    result = download_cats_threads(test_urls, "test_threads")
    print(f"Загружено {result['successful']} из {result['total']} за {result['time']:.2f} сек")