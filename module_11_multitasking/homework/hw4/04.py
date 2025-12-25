import time
from queue import PriorityQueue
from threading import Thread


class Producer(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        print("Producer: Running")
        tasks_data = [
            (0, 0.019658567230089852),
            (0, 0.8260261640443046),
            (1, 0.5049788914608555),
            (1, 0.9939451305978486),
            (2, 0.6217303299399963),
            (2, 0.7283236739267553),
            (3, 0.13090364153051426),
            (3, 0.21140406953974167),
            (4, 0.8426715099235477),
            (6, 0.43248434769420785)
        ]

        for priority, delay in tasks_data:
            self.queue.put((priority, delay))

        self.queue.join()
        print("Producer: Done")


class Consumer(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        print("Consumer: Running")

        while True:
            priority, delay = self.queue.get()

            if priority is None and delay is None:
                self.queue.task_done()
                break

            time.sleep(delay)
            print(f">running Task(priority={priority}).\t sleep({delay})")

            self.queue.task_done()

        print("Consumer: Done")


if __name__ == "__main__":
    q = PriorityQueue()

    p = Producer(q)
    c = Consumer(q)

    p.start()
    c.start()

    p.join()

    q.put((None, None))

    c.join()