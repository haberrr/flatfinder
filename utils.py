import time
from functools import wraps
from typing import Tuple, Type

from requests import HTTPError


def retry(n: int = 3,
          delay: int = 5,
          delay_increase: float = 2,
          max_delay: int = 30,
          exceptions: Tuple[Type[Exception]] = (HTTPError,),
          ):
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
                        time.sleep(min(delay * delay_increase ** i, max_delay))

        return wrapper

    return decorator
