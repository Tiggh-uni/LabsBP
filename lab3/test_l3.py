import pytest
from l3 import lr, lnr, fr, fnr

# ------------------------------------------------------------
# Тесты для lr (рекурсивное разглаживание)
# ------------------------------------------------------------
def test_lr():
        assert lr([]) == []
        assert lr([1, 2, 3]) == [1, 2, 3]
        assert lr([1, [2, [3, 4], 5]]) == [1, 2, 3, 4, 5]
        assert lr([1, [2, [3, [4, [5]]]]]) == [1, 2, 3, 4, 5]
        assert lr([[], [1, []], 2, [[3]]]) == [1, 2, 3]

# ------------------------------------------------------------
# Тесты для lnr (нерекурсивное разглаживание)
# ------------------------------------------------------------
def test_lnr():
    assert lnr([]) == []
    assert lnr([1, 2, 3]) == [1, 2, 3]
    # lnr изменяет список на месте, передаём новый экземпляр
    input_list = [1, [2, [3, 4], 5]]
    expected = [1, 2, 3, 4, 5]
    assert lnr(input_list) == expected
    input_list = [1, [2, [3, [4, [5]]]]]
    expected = [1, 2, 3, 4, 5]
    assert lnr(input_list) == expected
    input_list = [[], [1, []], 2, [[3]]]
    expected = [1, 2, 3]
    assert lnr(input_list) == expected
    data = [1, [2, [3, 4], 5], [6, [7, [8]]]]
    assert lr(data.copy()) == lnr(data.copy())

# ------------------------------------------------------------
# Тесты для fr и fnr (рекурсивная и итеративная версии)
# ------------------------------------------------------------
def test_fr_fnr_output_consistency(capsys):
    k = 5
    # Запускаем fr
    fr(k)
    captured_fr = capsys.readouterr()
    # Запускаем fnr
    fnr(k)
    captured_fnr = capsys.readouterr()
    # Сравниваем построчно (игнорируем заголовки "Рекурсия"/"Не рекурсия")
    fr_lines = captured_fr.out.strip().split('\n')
    fnr_lines = captured_fnr.out.strip().split('\n')
    # Сравниваем только строки с a=... и b=...
    assert fr_lines[1] == fnr_lines[1]  # a=...
    assert fr_lines[2] == fnr_lines[2]  # b=...

@pytest.mark.parametrize("k, expected_a, expected_b", [
    (1, 1, 1),
    (2, 3, 3),
    (3, 9, 9),
    (4, 27, 27),   # по рекуррентности a(4)=2*b(3)+a(3)=2*9+9=27
    (5, 81, 81),
])
def test_fr_values(k, expected_a, expected_b, capsys):
    fr(k)
    out = capsys.readouterr().out
    # Извлекаем значения a и b из вывода
    lines = out.strip().split('\n')
    a_line = lines[1]   # "a=27"
    b_line = lines[2]   # "b=27"
    a_val = int(a_line.split('=')[1])
    b_val = int(b_line.split('=')[1])
    assert a_val == expected_a
    assert b_val == expected_b

def test_fnr_values(capsys):
    # Проверяем несколько значений для fnr
    test_cases = [(1, 1, 1), (2, 3, 3), (3, 9, 9), (4, 27, 27), (5, 81, 81)]
    for k, ea, eb in test_cases:
        fnr(k)
        out = capsys.readouterr().out
        lines = out.strip().split('\n')
        # Для fnr вывод: "Не рекурсия\na=...\nb=..."
        a_val = int(lines[1].split('=')[1])
        b_val = int(lines[2].split('=')[1])
        assert a_val == ea
        assert b_val == eb

# Проверка, что fnr не падает на больших k (нет рекурсии)
def test_fnr_large_k():
    fnr(1000)  # не должно вызвать RecursionError