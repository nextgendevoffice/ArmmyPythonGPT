import cachetools

CACHE_SIZE = 100
cache = cachetools.LRUCache(CACHE_SIZE)

def cached_requests(func):
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in cache:
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    return wrapper
