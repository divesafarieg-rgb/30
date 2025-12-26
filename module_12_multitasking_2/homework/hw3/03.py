from threading import Semaphore, Thread, Event
import time
import signal
import sys

sem: Semaphore = Semaphore()
stop_event = Event()


def fun1():
    while not stop_event.is_set():
        sem.acquire()
        print(1)
        sem.release()
        time.sleep(0.25)


def fun2():
    while not stop_event.is_set():
        sem.acquire()
        print(2)
        sem.release()
        time.sleep(0.25)


t1: Thread = Thread(target=fun1)
t2: Thread = Thread(target=fun2)


def sigint_handler(sig, frame):
    print('\n=== SIGINT (Ctrl+C) получен! ===')
    stop_event.set()
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)

print("Программа запущена. Нажмите Ctrl+C для остановки...")

try:
    t1.start()
    t2.start()

    while True:
        time.sleep(3600)

except KeyboardInterrupt:
    print('\n=== KeyboardInterrupt через except ===')
    stop_event.set()
finally:
    print("Завершаем потоки...")
    t1.join(timeout=1)
    t2.join(timeout=1)
    print("Программа завершена.")