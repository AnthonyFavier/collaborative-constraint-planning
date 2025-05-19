pddl_init="""
    (located plane1 city1)
	(= (capacity plane1) 2990)
	(= (fuel plane1) 174)
	(= (slow-burn plane1) 1)
	(= (fast-burn plane1) 3)
	(= (onboard plane1) 0)
	(= (zoom-limit plane1) 3)
	(located plane2 city2)
	(= (capacity plane2) 4839)
	(= (fuel plane2) 1617)
	(= (slow-burn plane2) 2)
	(= (fast-burn plane2) 5)
	(= (onboard plane2) 0)
	(= (zoom-limit plane2) 5)
	(located person1 city3)
	(located person2 city0)
	(located person3 city0)
	(located person4 city1)
	(= (distance city0 city0) 0)
	(= (distance city0 city1) 569)
	(= (distance city0 city2) 607)
	(= (distance city0 city3) 754)
	(= (distance city1 city0) 569)
	(= (distance city1 city1) 0)
	(= (distance city1 city2) 504)
	(= (distance city1 city3) 557)
	(= (distance city2 city0) 607)
	(= (distance city2 city1) 504)
	(= (distance city2 city2) 0)
	(= (distance city2 city3) 660)
	(= (distance city3 city0) 754)
	(= (distance city3 city1) 557)
	(= (distance city3 city2) 660)
	(= (distance city3 city3) 0)
	(= (total-fuel-used) 0)
"""

pddl_init_lines = pddl_init.splitlines()

output = ''
for l in pddl_init_lines:
    l = l.replace('(','').replace(')','').replace('=','')
    l = l.split()
    
    if l==[]:
        continue
    
    fluentName = l[0]
    if fluentName=='total-fuel-used':
        contentCase = '2'
        valueSymbol = '0'
        parameters = '[]'
    elif fluentName=='located':
        contentCase = '4'
        valueSymbol = 'True'
        parameters = f'\n    - {l[1]}\n    - {l[2]}'
    else:
        contentCase = '2'
        valueSymbol = l[-1]
        parameters = '\n'+ ''.join([ f'    - {x}\n' for x in l[1:-1]])
        
    value = f"""
  - value:
      contentCase: {contentCase}
      valueSymbol: {valueSymbol}
    fluentName: {fluentName}
    parameters: {parameters}
"""[1:-1]
    
    output += value
    
    
print(output)