import itertools
import functools

def lr(l):
    if not l:
        return l
    if type(l[0]) is list:
        return lr(l[0]) + lr(l[1:])
    return l[:1] + lr(l[1:])

def lnr(l):
    """Нерекурсивное разглаживание списка (изменяет исходный список)."""
    result = []
    stack = [l]
    while stack:
        elem = stack.pop()
        if isinstance(elem, list):
            stack.extend(reversed(elem))  
        else:
            result.append(elem)
    l.clear()
    l.extend(result)
    return l
def fr(k):
    print("Рекурсия")
    @functools.lru_cache()
    def a(k):
        if k <= 1:
            return 1
        return 2 * b(k-1) + a(k-1)
    @functools.lru_cache()
    def b(k):
        if k <= 1:
            return 1
        return 2 * a(k-1) + b(k-1)
    for i in range (k):
        a(i)
        b(i)
    print(f"a={a(k)}")
    print(f"b={b(k)}")

def fnr(k):
    print("Не рекурсия")
    a = 1
    b = 1
    for _ in range(k-1):
        a1, b1 = a, b
        a = 2 * b + a
        b = 2 * a1 + b1
    print(f"a={a}\nb={b}")

if __name__ == "__main__":
    print(lr([1, 2, [3, 4, [5, [6, []]]]]))
    print(lnr([1, 2, [3, 4, [5, [6, []]]]]))
    k = int(input("Print k: "))
    fr(k)
    fnr(k)import itertools
import functools

def lr(l):
    if not l:
        return l
    if type(l[0]) is list:
        return lr(l[0]) + lr(l[1:])
    return l[:1] + lr(l[1:])

def lnr(l):
    """Нерекурсивное разглаживание списка (изменяет исходный список)."""
    result = []
    stack = [l]
    while stack:
        elem = stack.pop()
        if isinstance(elem, list):
            stack.extend(reversed(elem))  
        else:
            result.append(elem)
    l.clear()
    l.extend(result)
    return l
def fr(k):
    print("Рекурсия")
    @functools.lru_cache()
    def a(k):
        if k <= 1:
            return 1
        return 2 * b(k-1) + a(k-1)
    @functools.lru_cache()
    def b(k):
        if k <= 1:
            return 1
        return 2 * a(k-1) + b(k-1)
    print(f"a={a(k)}")
    print(f"b={b(k)}")

def fnr(k):
    print("Не рекурсия")
    a = 1
    b = 1
    for _ in range(k-1):
        a1, b1 = a, b
        a = 2 * b + a
        b = 2 * a1 + b1
    print(f"a={a}\nb={b}")

if __name__ == "__main__":
    print(lr([1, 2, [3, 4, [5, [6, []]]]]))
    print(lnr([1, 2, [3, 4, [5, [6, []]]]]))
    k = int(input("Print k: "))
    fr(k)
    fnr(k)
