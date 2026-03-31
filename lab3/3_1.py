import itertools
def lr(l):
    if not l:
        return l
    if type(l[0]) is list:
        return lr(l[0])+ lr(l[1:])
    return l[:1] + lr(l[1:])
def lnr(l):
    for _ in range(10):
        for i in range(len(l)):
            if type(l[i]) is list:
                for j in range(len(l[i])):
                    l.append(l[i][j])
                l.pop(i)
    return l
def fr(k):
    print("Рекурсия")
    print(f"a={a(k)}")
    print(f"b={b(k)}")
def a(k):
    if k<=1:
        return 1
    else:
        return 2*b(k-1)+a(k-1)
def b(k):
    if k<=1:
        return 1
    else:
        return 2*a(k-1)+b(k-1)
def fnr(k):
    print("Не рекурсия")
    a=1
    b=1
    for _ in range(k-1):
        a1=a
        b1=b
        a = 2*b+a
        b = 2*a1+b1
    print(f"a={a}\nb={b}")
print(lr([1, 2, [3, 4, [5, [6, []]]]]))
print(lnr([1, 2, [3, 4, [5, [6, []]]]]))
k=int(input("Print k:"))
fr(k)
fnr(k)
