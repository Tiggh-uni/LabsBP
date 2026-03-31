import itertools
def f1(s):
    c=0
    for i in itertools.product("КАТЕР", repeat=6):
        if i[0]=="Р" and i[-1]=="К":
            print(i)
            c+=1
    print(f"Всего {c} слов")
def f2(ch):
    c=0
    nch=""
    while ch!=0:
        nch += str(ch%6)
        ch = ch//6
    nch = nch[::-1]
    print(nch)
    for _ in range(10):
        if str(_) in nch:
            c+=1
    print(c)
def f3():
    for i in range(123450000,10**9+1):
        s = str(i)
        if s[0:5]=="12345" and s[6]=="7" and s[8]=="8" and i%23==0:
            print(f"{i} | {i//23}")
print("№1")
f1("КАТЕР")
print("№2")
f2(216**6+216**4+36**6-6**14-24)
print("№3")
f3()
