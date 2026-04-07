from functools import wraps
def check(func: callable)-> callable:
    @wraps(func)
    def wraper(*args,**kwargs):
        if isinstance(*args,(int,float)):
            r = func(*args,**kwargs)
            return r
    return wraper
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
summa(1,34,432,543,324,1324)
