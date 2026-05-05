import functools

# ----- Замыкание для среднего арифметического -----
def make_averager():
    history = []

    def averager(*args):
        if args:
            history.extend(args)
        if not history:
            return 0.0
        return sum(history) / len(history)

    return averager

# ----- Декоратор с проверкой типов и диапазона -----
def validate(types=None, min_val=None, max_val=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if types is not None:
                for arg in args:
                    if not isinstance(arg, types):
                        raise TypeError(f"Argument {arg} must be of type {types}, got {type(arg)}")
            if min_val is not None or max_val is not None:
                for arg in args:
                    if not isinstance(arg, (int, float)):
                        continue
                    if min_val is not None and arg < min_val:
                        raise ValueError(f"Argument {arg} is less than {min_val}")
                    if max_val is not None and arg > max_val:
                        raise ValueError(f"Argument {arg} is greater than {max_val}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ----- Демонстрация -----
if __name__ == "__main__":
    # 1) Обычное замыкание
    avg = make_averager()
    print(avg(10, 20))      # 15.0
    print(avg(30))          # 20.0
    print(avg())            # 20.0

    # 2) Задекорированное замыкание
    avg_validated = make_averager()
    avg_validated = validate(types=(int, float), min_val=0, max_val=100)(avg_validated)
    print(avg_validated(10, 20, 30))   # 20.0
    # print(avg_validated(150))        # ValueError

    # 3) Рекурсивная функция с декоратором
    @validate(types=int, min_val=0, max_val=10)
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n-1)

    print(factorial(5))     # 120
    # print(factorial(11))  # ValueError
