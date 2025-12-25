import logging
import random
import threading
import time

TOTAL_TICKETS = 10
MAX_SEATS = 30
PRINT_THRESHOLD = 3
TICKETS_TO_ADD = 6

SOLD_TICKETS = 0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Seller(threading.Thread):
    def __init__(self, semaphore: threading.Semaphore, stop_event: threading.Event):
        super().__init__()
        self.sem = semaphore
        self.stop_event = stop_event
        self.tickets_sold = 0
        logger.info(f'Seller {self.name} started work')

    def run(self):
        global TOTAL_TICKETS, SOLD_TICKETS

        while not self.stop_event.is_set():
            self.random_sleep()

            with self.sem:
                if TOTAL_TICKETS <= 0 or SOLD_TICKETS >= MAX_SEATS:
                    continue

                self.tickets_sold += 1
                SOLD_TICKETS += 1
                TOTAL_TICKETS -= 1

                logger.info(f'{self.name} sold one; Left: {TOTAL_TICKETS}, Sold: {SOLD_TICKETS}/{MAX_SEATS}')

                if SOLD_TICKETS >= MAX_SEATS:
                    self.stop_event.set()
                    break

        logger.info(f'Seller {self.name} sold {self.tickets_sold} tickets')

    def random_sleep(self):
        time.sleep(random.randint(0, 1) / 10)


class Director(threading.Thread):
    def __init__(self, semaphore: threading.Semaphore, stop_event: threading.Event):
        super().__init__()
        self.sem = semaphore
        self.stop_event = stop_event
        logger.info('Director started work')

    def run(self):
        global TOTAL_TICKETS, SOLD_TICKETS

        while not self.stop_event.is_set():
            time.sleep(0.1)

            with self.sem:
                need_more_tickets = (
                        TOTAL_TICKETS <= PRINT_THRESHOLD and
                        SOLD_TICKETS + TOTAL_TICKETS < MAX_SEATS
                )

                if need_more_tickets:
                    available_seats = MAX_SEATS - (SOLD_TICKETS + TOTAL_TICKETS)
                    tickets_to_add = min(TICKETS_TO_ADD, available_seats)

                    if tickets_to_add > 0:
                        TOTAL_TICKETS += tickets_to_add
                        logger.info(
                            f'=== Director added {tickets_to_add} tickets. Available: {TOTAL_TICKETS}, Sold: {SOLD_TICKETS}/{MAX_SEATS} ===')

            if SOLD_TICKETS >= MAX_SEATS:
                self.stop_event.set()
                break


def main():
    semaphore = threading.Semaphore()
    stop_event = threading.Event()

    director = Director(semaphore, stop_event)
    director.start()

    sellers = []
    for i in range(3):
        seller = Seller(semaphore, stop_event)
        seller.start()
        sellers.append(seller)

    director.join()

    time.sleep(0.5)

    stop_event.set()
    for seller in sellers:
        seller.join()

    logger.info('=' * 50)
    logger.info('PROGRAM FINISHED')
    logger.info(f'Total seats in cinema: {MAX_SEATS}')
    logger.info(f'Tickets sold: {SOLD_TICKETS}')
    logger.info(f'Tickets available: {TOTAL_TICKETS}')
    logger.info(f'Total processed: {SOLD_TICKETS + TOTAL_TICKETS}')

    total_sold_by_sellers = 0
    for seller in sellers:
        total_sold_by_sellers += seller.tickets_sold

    logger.info(f'Total sold by all sellers: {total_sold_by_sellers}')
    logger.info('=' * 50)


if __name__ == '__main__':
    main()