import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class APITester:
    def __init__(self, base_url, use_session=False, use_threading=False):
        self.base_url = base_url
        self.use_session = use_session
        self.use_threading = use_threading
        self.session = requests.Session() if use_session else None

    def make_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        try:
            if self.session:
                response = self.session.get(url, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            return response
        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def run_tests(self, endpoint, num_requests):
        if self.use_threading:
            return self._run_threaded(endpoint, num_requests)
        else:
            return self._run_sequential(endpoint, num_requests)

    def _run_sequential(self, endpoint, num_requests):
        start = time.time()
        for _ in range(num_requests):
            self.make_request(endpoint)
        end = time.time()
        return end - start

    def _run_threaded(self, endpoint, num_requests):
        start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.make_request, endpoint)
                      for _ in range(num_requests)]
            for future in as_completed(futures):
                future.result()
        end = time.time()
        return end - start