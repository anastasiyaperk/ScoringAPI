import functools
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


def cases(cases_list):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases_list:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                try:
                    f(*new_args)
                except Exception:
                    logging.error(f"Failed in {f.__name__} with case: {c}")
                    raise
        return wrapper
    return decorator
