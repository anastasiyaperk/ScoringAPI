import functools
import time

import pymemcache


def retry(exception=Exception, retries=3, backoff_in_seconds=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, retries+1):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    print(f'Retrying {func.__name__}: {i}/{retries}')
                    time.sleep(backoff_in_seconds * 2 ** i)
                    if i == retries:
                        raise e
        return wrapper
    return decorator


class MemcacheClient:
    def __init__(self, timeout: float = 5.):
        self.__client = pymemcache.client.base.Client(('localhost', 11211), timeout=timeout)

    @retry(ConnectionRefusedError)
    def cache_get(self, key):
        return self.__client.get(key, None)

    @retry(ConnectionRefusedError)
    def get(self, key):
        return self.__client.get(key, None)

    @retry(ConnectionRefusedError)
    def cache_set(self, key, value, expire_time: int = 60):
        return self.__client.set(key, value, expire_time)



