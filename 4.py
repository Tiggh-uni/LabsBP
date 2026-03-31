from functools import wraps
def dec(func: callable)-> callable:
    @wraps(func)
    def wraper(*args,**kwargs):
        s=0
        k=0
        for i in *args,*kwargs:
            s+=i
            k+=1
        print(f'Среднее арефмитическое параметров: {s/k}')
        r= func(*args,**kwargs)
        return r
    return wraper
def check(func: callable)-> callable:
    @wraps(func)
    def wraper(*args,**kwargs):
        if isinstance(*args,(int,float)):
            r = func(*args,**kwargs)
            return r
    return wraper
@dec
def summa(*args):
    su=0
    for i in args:
        su+=i
    return su
print(summa(1,34,432,543,324,1324))
