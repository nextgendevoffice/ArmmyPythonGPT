import cachetools
import time
CACHE_SIZE = 100
cache = cachetools.LRUCache(CACHE_SIZE)

def cached_requests(func):
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in cache:
            return cache[key]
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        cache_time = end_time - start_time
        cache[key] = result
        return result
    return wrapper
