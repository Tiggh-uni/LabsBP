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
    :yield: изменённые элементы, прошедшие фильтр значительности
    """
    if sign_func is None:
        def significance_func(old: Any, new: Any, n: int) -> bool:
            
            if isinstance(old, (int, float)):
                
                return abs(new - old) > n * 1e-6
            elif isinstance(old, str):
                
                return abs(len(new) - len(old)) > n
            else:
                
                return new != old

   
    def apply_n_times(x: Any) -> Any:
        return reduce(lambda val, _: func(val), range(n), x)

    
    mapped = map(lambda x: (x, apply_n_times(x)), iterable)

    filtered = filter(lambda pair: significance_func(pair[0], pair[1], n), mapped)

    for _, new_value in filtered:
        yield new_value
print(list(sig_changes([10.0], lambda x: x + 1e-5, 1)))
# ------------------- Тесты pytest -------------------

def test_numbers_significant_change():
    
    result = list(sig_changes(
        [1, 2, 3],
        1,
        lambda x: x + 1,
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

    result_gen = significant_changes(gen(), lambda x: x + 1, 1, lambda o, n, _: n - o > 0)
    
    assert next(result_gen) == 1
    assert next(result_gen) == 2
