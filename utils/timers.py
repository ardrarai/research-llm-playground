import time

class Timer:
    def __init__(self):
        self.start_time = None
        self.elapsed = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.elapsed = time.time() - self.start_time
        return self.elapsed
