import pytest
from functools import reduce
from typing import Iterable, Callable, Any, Optional

def significant_changes(
    iterable: Iterable[Any],
    func: Callable[[Any], Any],
    n: int,
    significance_func: Optional[Callable[[Any, Any, int], bool]] = None
):
    """
    Генератор, который применяет функцию func к каждому элементу последовательности
    n раз и возвращает только те результаты, которые значительно изменились.

    :param iterable: исходная последовательность
    :param func: функция, применяемая к элементу
    :param n: количество применений
    :param significance_func: функция, определяющая значительность изменения.
                              Принимает (old_value, new_value, n) и возвращает bool.
                              Если не задана, используется встроенная логика для чисел и строк.
    :yield: изменённые элементы, прошедшие фильтр значительности
    """
    if significance_func is None:
        def significance_func(old: Any, new: Any, n: int) -> bool:
            # Логика по умолчанию
            if isinstance(old, (int, float)):
                # Абсолютное изменение > n * 1e-6
                return abs(new - old) > n * 1e-6
            elif isinstance(old, str):
                # Значительное изменение длины строки: разница > n
                return abs(len(new) - len(old)) > n
            else:
                # Для остальных типов считаем значительным любое изменение
                return new != old

    # Применяем func n раз с помощью reduce
    def apply_n_times(x: Any) -> Any:
        return reduce(lambda val, _: func(val), range(n), x)

    # Создаём пары (исходное, преобразованное) через map
    mapped = map(lambda x: (x, apply_n_times(x)), iterable)

    # Фильтруем по значимости
    filtered = filter(lambda pair: significance_func(pair[0], pair[1], n), mapped)

    # Возвращаем только преобразованные элементы
    for _, new_value in filtered:
        yield new_value


# ------------------- Тесты pytest -------------------

def test_numbers_significant_change():
    # f(x)=x+1, n=1, значимость: изменение > 0.5
    result = list(significant_changes(
        [1, 2, 3],
        lambda x: x + 1,
        1,
        lambda old, new, _: new - old > 0.5
    ))
    assert result == [2, 3, 4]


def test_numbers_insignificant_change():
    # f(x)=x+0.1, n=1, значимость: изменение > 0.5 → нет значимых
    result = list(significant_changes(
        [1, 2, 3],
        lambda x: x + 0.1,
        1,
        lambda old, new, _: new - old > 0.5
    ))
    assert result == []


def test_multiple_applications():
    # f(x)=x*2, n=2, значимость: изменение > 2
    # 1 -> 4 (изм 3>2), 2 -> 8 (6>2), 3 -> 12 (9>2) → все
    result = list(significant_changes(
        [1, 2, 3],
        lambda x: x * 2,
        2,
        lambda old, new, _: abs(new - old) > 2
    ))
    assert result == [4, 8, 12]


def test_strings_length_change():
    # f(s)=s+'a', n=3, значимость: изменение длины > 2
    # Каждая строка удлиняется на 3, что >2 → все возвращаются
    result = list(significant_changes(
        ["x", "ab", "xyz"],
        lambda s: s + 'a',
        3,
        lambda old, new, _: abs(len(new) - len(old)) > 2
    ))
    assert result == ["xaaa", "abaaa", "xyzaaa"]


def test_strings_no_change():
    # f(s)=s[0] if s else s, n=1, значимость: new != old
    # "abc" -> "a" (изменилась), "def" -> "d" (изменилась), "g" -> "g" (не изменилась)
    result = list(significant_changes(
        ["abc", "def", "g"],
        lambda s: s[0] if s else s,
        1,
        lambda old, new, _: new != old
    ))
    assert result == ["a", "d"]


def test_default_significance_for_numbers():
    # По умолчанию: изменение > n * 1e-6
    # f(x)=x+1e-5, n=1 → изменение 1e-5 > 1e-6 → значительное
    result = list(significant_changes([10.0], lambda x: x + 1e-5, 1))
    assert result == [10.00001]

    # f(x)=x+1e-7, n=1 → изменение 1e-7 < 1e-6 → незначительное
    result = list(significant_changes([10.0], lambda x: x + 1e-7, 1))
    assert result == []


def test_default_significance_for_strings():
    # По умолчанию для строк: разница длин > n
    # f(s)=s+'a', n=2 → длина увеличивается на 2, что не >2 → незначительно
    result = list(significant_changes(["hello"], lambda s: s + 'aa', 2))
    assert result == []  # изменение длины = 2, не строго больше n

    # f(s)=s+'aaa', n=2 → длина увеличивается на 3 >2 → значительное
    result = list(significant_changes(["hello"], lambda s: s + 'aaa', 2))
    assert result == ["helloaaa"]


def test_generator_lazyness():
    # Проверка, что генератор не вычисляет всё сразу
    def gen():
        for i in range(5):
            yield i

    result_gen = significant_changes(gen(), lambda x: x + 1, 1, lambda o, n, _: n - o > 0)
    # Вычисляем только первые два элемента
    assert next(result_gen) == 1
    assert next(result_gen) == 2
    # Остальные не вычислены, но это нормально
