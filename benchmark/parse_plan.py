import pyperclip

txt="""
0.0: (board person8 plane3 city5)
1.0: (refuel plane2)
2.0: (board person7 plane3 city5)
3.0: (board person6 plane1 city2)
4.0: (refuel plane1)
5.0: (refuel plane3)
6.0: (flyfast plane2 city3 city3)
7.0: (flyslow plane3 city5 city0)
8.0: (flyslow plane3 city0 city4)
9.0: (debark person6 plane1 city2)
10.0: (flyslow plane1 city2 city2)
11.0: (debark person8 plane3 city4)
12.0: (board person1 plane3 city4)
13.0: (board person2 plane3 city4)
14.0: (refuel plane3)
15.0: (flyslow plane3 city4 city1)
16.0: (board person5 plane3 city1)
17.0: (debark person2 plane3 city1)
18.0: (flyslow plane3 city1 city4)
19.0: (refuel plane3)
20.0: (debark person5 plane3 city4)
21.0: (flyslow plane3 city4 city2)
22.0: (board person6 plane3 city2)
23.0: (debark person1 plane3 city2)
24.0: (flyslow plane3 city2 city0)
25.0: (board person3 plane3 city0)
26.0: (flyslow plane3 city0 city3)
27.0: (refuel plane3)
28.0: (debark person7 plane3 city3)
29.0: (flyslow plane3 city3 city1)
30.0: (debark person3 plane3 city1)
31.0: (debark person6 plane3 city1)
"""[1:-1]

plan = ''
for l in txt.splitlines():
    t = '0: ('
    i = l.find(t)+len(t)
    i2 = l.find(')', i)
    
    x = l[i:i2].split()
    
    action = x[0]
    params = x[1:]

    new_params = []
    
    for p in params:
        i=0
        for i in range(len(p)):
            if not p[i].isalpha():
                break
        new_params.append(f"{p[:i]}[{p[i:]}]")
    
    # print(f"a={action} p={new_params}")
    
    ai = f"ActionInstance({action}, ("
    for i,p in enumerate(new_params):
        if i!=len(new_params)-1:
            ai+=f"{p}, "
        else:
            ai+=f"{p})),"

    # print(ai)
    plan += ai + '\n'
    
# print(plan)
pyperclip.copy(plan[:-1])


