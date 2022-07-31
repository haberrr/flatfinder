import time
from functools import wraps
from typing import Tuple, Type

from requests import HTTPError


def retry(n: int = 3,
          delay: int = 5,
          backoff_factor: float = 2,
          max_delay: int = 30,
          exceptions: Tuple[Type[Exception]] = (HTTPError,),
          ):
    """Retry decorated function according to the specification.

    :param n: number of times to retry decorated function.
    :param delay: start delay between consecutive retries.
    :param backoff_factor: multiply delay by this factor after each retry.
    :param max_delay: maximum delay between retries.
    :param exceptions: exceptions to retry, other exceptions won't be caught.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(n + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == n:
                        raise e
                    else:
                        time.sleep(min(delay * backoff_factor ** i, max_delay))

        return wrapper

    return decorator
