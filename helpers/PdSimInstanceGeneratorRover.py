pddl_init="""
    (visible waypoint0 waypoint1)
	(visible waypoint1 waypoint0)
	(visible waypoint1 waypoint2)
	(visible waypoint2 waypoint1)
	(visible waypoint1 waypoint3)
	(visible waypoint3 waypoint1)
	(visible waypoint2 waypoint0)
	(visible waypoint0 waypoint2)
	(visible waypoint2 waypoint3)
	(visible waypoint3 waypoint2)
	(visible waypoint3 waypoint0)
	(visible waypoint0 waypoint3)
	(at_soil_sample waypoint0)
	(at_rock_sample waypoint0)
	(at_lander general waypoint1)
	(channel_free general)
	(at rover0 waypoint1)
	(available rover0)
	(store_of rover0store rover0)
	(empty rover0store)
	(equipped_for_soil_analysis rover0)
	(equipped_for_rock_analysis rover0)
	(equipped_for_imaging rover0)
	(can_traverse rover0 waypoint0 waypoint1)
	(can_traverse rover0 waypoint1 waypoint0)
	(can_traverse rover0 waypoint0 waypoint2)
	(can_traverse rover0 waypoint2 waypoint0)
	(can_traverse rover0 waypoint0 waypoint3)
	(can_traverse rover0 waypoint3 waypoint0)
	(on_board camera0 rover0)
	(calibration_target camera0 objective0)
	(supports camera0 colour)
	(supports camera0 high_res)
	(supports camera0 low_res)
	(on_board camera1 rover0)
	(calibration_target camera1 objective1)
	(supports camera1 high_res)
	(visible_from objective0 waypoint0)
	(visible_from objective1 waypoint0)
	(visible_from objective1 waypoint1)
	(visible_from objective1 waypoint2)
"""

pddl_init_lines = pddl_init.splitlines()

output = ''
for l in pddl_init_lines:
    l = l.replace('(','').replace(')','').replace('=','')
    l = l.split()
    
    if l==[]:
        continue
    
    fluentName = l[0]
    contentCase = '4'
    valueSymbol = 'True'
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