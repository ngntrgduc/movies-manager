from time import perf_counter
from functools import wraps

def timing(func):
    """Measure and print execution time of a function."""
    @wraps(func)    
    def wrapper(*args, **kwargs):
        tic = perf_counter()
        result = func(*args, **kwargs)
        print(f'Function {func.__name__} took {(perf_counter()-tic):.5f}s')
        return result
    return wrapper