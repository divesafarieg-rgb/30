import requests
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import mimetypes
from urllib.parse import urlparse
import time
import multiprocessing


def download_cat_process(url, save_dir, idx):
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        if response.status_code != 200:
            print(f"❌ [Процесс {idx}] Ошибка {url}: статус {response.status_code}")
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

        print(f"✅ [Процесс {idx}] Кот сохранён: {file_path}")
        return file_path

    except requests.exceptions.Timeout:
        print(f"❌ [Процесс {idx}] Таймаут при загрузке {url}")
        return None
    except Exception as e:
        print(f"❌ [Процесс {idx}] Ошибка при загрузке {url}: {e}")
        return None


def download_cats_processes(urls, save_dir, max_workers=None):
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()

    if max_workers > 4:
        max_workers = 4

    Path(save_dir).mkdir(exist_ok=True)

    start_time = time.time()
    results = []

    try:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(download_cat_process, url, save_dir, i)
                       for i, url in enumerate(urls)]

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    results.append(result)
                except Exception as e:
                    print(f"❌ Ошибка при получении результата: {e}")
                    results.append(None)

    except KeyboardInterrupt:
        print("\n⚠️ Процессы прерваны пользователем")
        return {
            'time': time.time() - start_time,
            'successful': sum(1 for r in results if r is not None),
            'total': len(urls),
            'results': results
        }
    except Exception as e:
        print(f"❌ Ошибка в ProcessPoolExecutor: {e}")

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
    result = download_cats_processes(test_urls, "test_processes")
    print(f"Загружено {result['successful']} из {result['total']} за {result['time']:.2f} сек")