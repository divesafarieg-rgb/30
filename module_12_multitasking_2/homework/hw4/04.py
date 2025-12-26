import threading
import time
import queue
import requests
from datetime import datetime


class LoggerThread(threading.Thread):
    def __init__(self, thread_id, log_queue, stop_event):
        super().__init__()
        self.thread_id = thread_id
        self.log_queue = log_queue
        self.stop_event = stop_event

    def run(self):
        start_time = time.time()
        while time.time() - start_time < 20 and not self.stop_event.is_set():
            current_timestamp = int(time.time())

            try:
                url = f"http://127.0.0.1:8080/timestamp/{current_timestamp}"
                response = requests.get(url)

                if response.status_code == 200:
                    self.log_queue.put((current_timestamp, response.text.strip()))
                else:
                    print(f"Ошибка запроса: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"Ошибка соединения: {e}")
                time.sleep(1)
                continue

            time.sleep(1)


def writer_thread(log_queue, stop_event, filename="logs.txt"):
    while not stop_event.is_set() or not log_queue.empty():
        try:
            timestamp, log_entry = log_queue.get(timeout=1)

            with open(filename, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} {log_entry}\n")

            log_queue.task_done()

        except queue.Empty:
            continue
        except Exception as e:
            print(f"Ошибка записи: {e}")


def main():
    log_queue = queue.Queue()
    stop_event = threading.Event()

    writer = threading.Thread(target=writer_thread, args=(log_queue, stop_event))
    writer.start()

    threads = []

    for i in range(10):
        thread = LoggerThread(i, log_queue, stop_event)
        thread.start()
        threads.append(thread)
        time.sleep(1)

    for thread in threads:
        thread.join()

    time.sleep(2)

    stop_event.set()
    writer.join()

    sort_logs()


def sort_logs(filename="logs.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    log_entries = []
    for line in lines:
        parts = line.strip().split(" ", 1)
        if len(parts) == 2:
            timestamp = int(parts[0])
            log_entries.append((timestamp, parts[1]))

    log_entries.sort(key=lambda x: x[0])

    with open("sorted_logs.txt", "w", encoding="utf-8") as f:
        for timestamp, entry in log_entries:
            f.write(f"{timestamp} {entry}\n")

    print(f"Записи отсортированы и сохранены в sorted_logs.txt")


if __name__ == "__main__":
    main()