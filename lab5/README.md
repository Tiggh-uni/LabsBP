Задание: Генератор, применяющий заданную функцию к каждому элементу последовательности N раз. Верните только те элементы, которые изменились значительно (зависит от N и типа данных).

Код:
```python
import pytest
from functools import reduce
from typing import Iterable, Callable, Any, Optional

def sig_changes(
    iterable: Iterable[Any],
    func: Callable[[Any], Any],
    n: int,
    sign_func: Optional[Callable[[Any, Any, int], bool]] = None
):
    """
    Генератор, который применяет функцию func к каждому элементу последовательности
    n раз и возвращает только те результаты, которые значительно изменились.

    iterable: исходная последовательность
    func: функция, применяемая к элементу
    n: количество применений
    sign_func: функция, определяющая значительность изменения.
                              Принимает (old_value, new_value, n) и возвращает bool.
                              Если не задана, используется встроенная логика для чисел и строк.
    """
    if sign_func is None:
        def sign_func(old: Any, new: Any, n: int) -> bool:
            
            if isinstance(old, (int, float)):
                
                return abs(new - old) > n * 1e-6
            elif isinstance(old, str):
                
                return abs(len(new) - len(old)) > n
            else:
                
                return new != old

   
    def a_n_t(x: Any) -> Any:
        return reduce(lambda val, _: func(val), range(n), x)

    
    mapped = map(lambda x: (x, a_n_t(x)), iterable)

    filtered = filter(lambda pair: sign_func(pair[0], pair[1], n), mapped)

    for _, new_value in filtered:
        yield new_value
print(list(sig_changes([10.0], lambda x: x + 1e-5, 1)))
print(list(sig_changes([1, 2, 3],lambda x: x*1.4,5,lambda old, new, _: new - old > 10)))
# ------------------- Тесты pytest -------------------

def test_numbers_significant_change():
    
    result = list(sig_changes(
        [1, 2, 3],
        lambda x: x + 1,
        1,
        lambda old, new, _: new - old > 0.5
    ))
    assert result == [2, 3, 4]


def test_numbers_insignificant_change():
    
    result = list(sig_changes(
        [1, 2, 3],
        lambda x: x + 0.1,
        1,
        lambda old, new, _: new - old > 0.5
    ))
    assert result == []


def test_multiple_applications():
    
    result = list(sig_changes(
        [1, 2, 3],
        lambda x: x * 2,
        2,
        lambda old, new, _: abs(new - old) > 2
    ))
    assert result == [4, 8, 12]


def test_strings_length_change():
    
    result = list(sig_changes(
        ["x", "ab", "xyz"],
        lambda s: s + 'a',
        3,
        lambda old, new, _: abs(len(new) - len(old)) > 2
    ))
    assert result == ["xaaa", "abaaa", "xyzaaa"]


def test_strings_no_change():
    
    result = list(sig_changes(
        ["abc", "def", "g"],
        lambda s: s[0] if s else s,
        1,
        lambda old, new, _: new != old
    ))
    assert result == ["a", "d"]


def test_default_significance_for_numbers():
    
    result = list(sig_changes([10.0], lambda x: x + 1e-5, 1))
    assert result == [10.00001]

    
    result = list(sig_changes([10.0], lambda x: x + 1e-7, 1))
    assert result == []


def test_default_significance_for_strings():
    
    result = list(sig_changes(["hello"], lambda s: s + 'aa', 2))
    assert result == ["helloaaaa"]  

    result = list(sig_changes(["hello"], lambda s: s + 'aaa', 1))
    assert result == ["helloaaa"]


def test_generator_lazyness():
    
    def gen():
        for i in range(5):
            yield i

    result_gen = sig_changes(gen(), lambda x: x + 1, 1, lambda o, n, _: n - o > 0)
    
    assert next(result_gen) == 1
    assert next(result_gen) == 2

```

Реализована генераторная функция significant_changes, которая к каждому элементу входной последовательности применяет заданную функцию n раз и возвращает только те результаты, чьё изменение признано значительным. Для многократного применения используется reduce с лямбдой, осуществляющей n последовательных вызовов func. Фильтрация выполняется через пользовательскую функцию significance_func (принимает старое значение, новое значение и n), а при её отсутствии — встроенная логика: для чисел разница сравнивается с порогом n * 1e-6, для строк — разница длин с порогом n, для остальных типов — простое неравенство. Генератор ленив: значения вычисляются и отбираются по одному, не загружая всю последовательность в память, что подтверждено тестами с пошаговым извлечением через next. Тесты pytest проверяют значимые и незначимые изменения для чисел и строк, множественные применения, ленивость и работу встроенной функции значимости по умолчанию.

Результат:

![Alt text](image.png)

Список использованной источников:

[Генераторы в Python](https://habr.com/ru/articles/866616/)

[Что такое yield в Python и как его использовать](https://thecode.media/yield-v-python/)

[Генераторы Python: что это такое и зачем они нужны](https://practicum.yandex.ru/blog/chto-takoe-generator-v-python-i-dlya-chego-nuzhen/)
