from functools import wraps
def check(types= None, mi_v = None, ma_v=None):
    def chec_d(func: callable)-> callable:
        @wraps(func)
        def wraper(*args,**kwargs):
            if types is not None:
                for arg in args:
                    if not isinstance(arg,types):
                       raise TypeError(f"Argument {arg} must be of type {types}, got {type(arg)}")
            if mi_v is not None or ma_v is not None:
                for arg in args:
                    if not isinstance(arg, (int, float)):
                        continue
                    if mi_v is not None and arg < mi_v:
                        raise ValueError(f"Argument {arg} is less than {mi_v}")
                    if ma_v is not None and arg > ma_v:
                        raise ValueError(f"Argument {arg} is greater than {ma_v}")
            return func(*args, **kwargs)
        return wraper
    return chec_d
@check(types = (int, float),mi_v=0, ma_v=600)
def summa(*args):
    def wraper(*args):
        s=0
        k=0
        for i in  args:
            s+=i
            k+=1
        print(f'Среднее арефмитическое параметров: {s/k}\n Сумма чисел:{su}')

    su=0
    for i in args:
        su+=i
    return  wraper(*args)
summa(1,34,432,543,324,124)
summa(1,34,432,543,324,124,"hp")