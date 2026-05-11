Цель: Замыкание для поиска среднего в аргументах. Декоратор для проверки аргументов функции на тип и диапазон значений.
Замыкание для записи всех значений в файл.

Код:

```python
  
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
    h = []
    @check(types = (int, float),mi_v=0, ma_v=600)
    def wraper(*args):
        if args:
            h.extend(args)
            sc = sum(args)
            sh = sum(h)
        
        print(f'Среднее арефмитическое параметров: {sh/len(h)}\n Сумма чисел:{sc}')

    su=sum(args)
    if args:
        print(su)
    return  wraper
summa(1,34,432,543,324,124)
#summa(1,34,432,543,324,124,"hp")

a = summa()
a(7,8,8)
a(5,3,65,43)
#a(45,23,342,342432)

```

Реализована функция summa, возвращающая замыкание wraper для накопления переданных аргументов и вычисления их среднего арифметического. Внутренняя функция сохраняет все аргументы в список h и при каждом вызове выводит текущую сумму переданных аргументов и среднее арифметическое по всем накопленным значениям. Первый вызов summa с аргументами сразу выводит их сумму, а последующие обращения к возвращённому замыканию продолжают накопление. Механизм замыкания обеспечивает сохранение состояния между вызовами без использования глобальных переменных. 
Создан параметризованный декоратор check, принимающий типы (types), минимальное (mi_v) и максимальное (ma_v) допустимые значения. Декоратор оборачивает целевую функцию, проверяя каждый позиционный аргумент: если задан types — аргумент должен быть экземпляром указанного типа, иначе возбуждается TypeError; если заданы границы и аргумент является числом — проверяется попадание в диапазон, при нарушении возбуждается ValueError.

Без декоратора:

![Изображение с декоратором](image.png)

С декоратором:

![Изображение с декоратором](image-1.png)

 Список использованных источников:

 [Замыкания и декораторы в Python: часть 1 — замыкания](https://habr.com/ru/articles/781866/)
 
 [Замыкания и Декораторы](https://pyhub.ru/python-advanced/lecture-10-33-71/)
 
 [Декораторы Python: пошаговое руководство](https://habr.com/ru/companies/otus/articles/727590/)
 
