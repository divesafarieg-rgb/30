import os
import sys


def get_mean_size_simple():
    files = [f for f in os.listdir('.') if os.path.isfile(f)]

    if not files:
        return 0.0

    total_size = 0
    for file in files:
        total_size += os.path.getsize(file)

    return total_size / len(files)


if __name__ == '__main__':
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        lines = data.strip().split('\n')
        sizes = []

        for line in lines:
            for part in line.split():
                try:
                    size = int(part)
                    if 1 <= size <= 10 ** 12:
                        sizes.append(size)
                except ValueError:
                    continue

        mean_size = sum(sizes) / len(sizes) if sizes else 0.0
    else:
        mean_size = get_mean_size_simple()

    print(f"Средний размер файла: {mean_size:.2f} байт")