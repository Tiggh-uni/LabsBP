from functools import wraps
def check(types= None, mi_v = None, ma_v=None):
    def chec_d(func: callable)-> callable:
        def wraper(*args,**kwargs):
            if types is not None:
                for arg in args:
                    if not isinstance(arg,types):
                       raise TypeError(f"Аргумент {arg} должен быть {types}, а не {type(arg)}")
            if mi_v is not None or ma_v is not None:
                for arg in args:
                    if not isinstance(arg, (int, float)):
                        continue
                    if mi_v is not None and arg < mi_v:
                        raise ValueError(f"Аргумент {arg} меньше чем {mi_v}")
                    if ma_v is not None and arg > ma_v:
                        raise ValueError(f"Аргумент {arg} больше чем {ma_v}")
            return func(*args, **kwargs)
        return wraper
    return chec_d
@check(types = (int, float),mi_v=0, ma_v=600)
def summa(*args):
    h = []
    @check(types = (int, float),mi_v=0, ma_v=600)
    def wraper(*args):
        if args:
            h.extend(args)
            sc = sum(args)
            sh = sum(h)
        
        print(f'Среднее арефмитическое параметров: {sh/len(h)}\n Сумма чисел:{sc}')

    return  wraper
summa(1,34,432,543,324,124)
summa(1,34,432,543,324,124,"hp")

a = summa()
a(7,8,8)
a(5,3,65,43)
#a(45,23,342,6434)