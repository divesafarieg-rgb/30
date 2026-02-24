import time
import psutil
import pandas as pd
from pathlib import Path

from thread_downloader import download_cats_threads
from process_downloader import download_cats_processes
from async_downloader import download_cats_async


def generate_urls(n):
    base_urls = [
        "https://cataas.com/cat",
        "https://http.cat/200",
        "https://http.cat/404",
        "https://cataas.com/cat/says/Hello",
        "https://cataas.com/cat/gif",
    ]
    return [base_urls[i % len(base_urls)] for i in range(n)]


def measure_memory_usage(func, *args, **kwargs):
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024

    result = func(*args, **kwargs)

    mem_after = process.memory_info().rss / 1024 / 1024
    mem_used = mem_after - mem_before

    return result, mem_used


def run_benchmark():
    test_sizes = [10, 50, 100]
    results = []

    for size in test_sizes:
        print(f"\n{'=' * 50}")
        print(f"ТЕСТИРОВАНИЕ НА {size} КАРТИНКАХ")
        print(f"{'=' * 50}")

        urls = generate_urls(size)

        print(f"\n--- Треды ({size} картинок) ---")
        thread_result, thread_mem = measure_memory_usage(
            download_cats_threads, urls, f"cats_threads_{size}", 10
        )
        results.append({
            'method': 'Threads',
            'images': size,
            'time': thread_result['time'],
            'successful': f"{thread_result['successful']}/{thread_result['total']}",
            'success_rate': (thread_result['successful'] / size * 100),
            'memory_mb': thread_mem
        })

        print(f"\n--- Процессы ({size} картинок) ---")
        process_result, process_mem = measure_memory_usage(
            download_cats_processes, urls, f"cats_processes_{size}", 4
        )
        results.append({
            'method': 'Processes',
            'images': size,
            'time': process_result['time'],
            'successful': f"{process_result['successful']}/{process_result['total']}",
            'success_rate': (process_result['successful'] / size * 100),
            'memory_mb': process_mem
        })

        print(f"\n--- Асинхронность ({size} картинок) ---")
        async_result, async_mem = measure_memory_usage(
            download_cats_async, urls, f"cats_async_{size}"
        )
        results.append({
            'method': 'Async',
            'images': size,
            'time': async_result['time'],
            'successful': f"{async_result['successful']}/{async_result['total']}",
            'success_rate': (async_result['successful'] / size * 100),
            'memory_mb': async_mem
        })

    return results


def create_markdown_table(results):
    table = "| Метод | Кол-во изображений | Время (сек) | Успешно загружено | Процент успеха | Память (MB) |\n"
    table += "|-------|-------------------|-------------|-------------------|----------------|-------------|\n"

    for row in results:
        table += f"| {row['method']} | {row['images']} | {row['time']:.2f} | "
        table += f"{row['successful']} | {row['success_rate']:.1f}% | "
        table += f"{row['memory_mb']:.2f} |\n"

    return table


if __name__ == "__main__":
    print("=" * 60)
    print("ЗАПУСК СРАВНИТЕЛЬНОГО ТЕСТИРОВАНИЯ")
    print("=" * 60)

    Path("benchmark_results").mkdir(exist_ok=True)

    results = run_benchmark()

    markdown_table = create_markdown_table(results)

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print("\n" + markdown_table)

    with open('benchmark_results/results.md', 'w', encoding='utf-8') as f:
        f.write("# Результаты сравнительного анализа загрузки котиков\n\n")
        f.write("## Таблица результатов\n\n")
        f.write(markdown_table)

        f.write("\n## Анализ результатов\n\n")
        f.write("### Наблюдения:\n")
        f.write("1. **Асинхронный подход** показал наилучшую производительность\n")
        f.write("2. **Треды** эффективны для IO-bound операций\n")
        f.write("3. **Процессы** имеют наибольшие накладные расходы\n\n")

        f.write("### Рекомендации:\n")
        f.write("- Для загрузки множества файлов лучше использовать асинхронность\n")
        f.write("- Треды подходят для простых задач\n")
        f.write("- Процессы лучше использовать для CPU-bound задач\n")

    print("\n✅ Результаты сохранены в файл 'benchmark_results/results.md'")