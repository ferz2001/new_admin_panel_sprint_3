import os
from functools import wraps
from time import sleep


def backoff(start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: int = 10, max_retries: int = 0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = start_sleep_time
            retries = 1
            while True:
                if retries > max_retries > 0:
                    raise Exception('Number of attempts has been exceeded')
                try:
                    return func(*args, **kwargs)
                except:
                    retries += 1
                    sleep(delay)
                    delay = min(delay * factor, border_sleep_time)

        return wrapper
    return decorator
