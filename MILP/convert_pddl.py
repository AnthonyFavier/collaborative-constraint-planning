import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.engines import PlanGenerationResultStatus
import itertools

import time

from MILP.boxprint import boxprint

from sympy import expand, simplify
from sympy.parsing.sympy_parser import parse_expr

# used to convert strict inequalities into regular ones
# i.e. ax+b > 0 becomes ax+b-epsilon>=0
epsilon = 1e-5

def normalize_equation(expr_str):
    exp = parse_expr(expr_str, evaluate=False)

    if exp.is_Relational:
        op = exp.rel_op

        if op == '!=':
            raise Exception('!= operator found, unsupported')

        # Move everything to the left side
        exp = expand(exp.lhs - exp.rhs)
        
        # Convert <, <= into >, >= by flipping sign
        if op == '<':
            exp = -exp
            op = '>'
        elif op == '<=':
            exp = -exp
            op = '>='

        # Transform strict operator
        if op == '>':
            exp -= epsilon
            op = '>='

        exp = expand(exp)
        exp_str = str(exp) + ' ' + op + ' 0'

    else:
        exp = expand(exp)
        exp_str = str(exp)

    return exp_str

def load_pddl(domain_filename, problem_filename, show=False, solve=False):
    up.shortcuts.get_environment().credits_stream = None
    
    #############
    ## PARSING ##
    #############
    reader = PDDLReader()
    problem = reader.parse_problem(domain_filename, problem_filename)

    ###############
    ## GROUNDING ##
    ###############

    t1 = time.time()
    print('\tGrounding ... ', end='', flush=True)
    if problem.kind.has_general_numeric_planning() or problem.kind.has_simple_numeric_planning():
        compiler_name = 'up_grounder'
    else:
        compiler_name = 'fast-downward-grounder'
    with Compiler(name=compiler_name) as compiler:
        compilation_result = compiler.compile(problem, CompilationKind.GROUNDING)
        problem = compilation_result.problem
    print(f'Ok [{time.time()-t1:.2f}s]')

    #############################################
    ## REPLACE CONSTANT NUM FLUENT WITH VALUE ##
    #############################################
    t1 = time.time()
    print('\tReplacing constant fluents ... ', end='', flush=True)
    # Collect fluents that appear as effects (i.e., modified)
    modified_fluents = set()
    for action in problem.actions:
        for eff in action.effects:
            if eff.fluent.type.is_real_type():
                modified_fluents.add(eff.fluent)

    # Collect grounded fluents (i.e. all)
    initial_Vn = set()
    for f in problem.fluents:
        object_sets = []
        for s in f.signature:
            objects = [str(o) for o in problem.objects(s.type)]
            object_sets.append(objects)
        combinations = list(itertools.product(*object_sets))
        for comb in combinations:
            if f.type.is_real_type(): # Numeric
                exp = f(*[problem.object(c) for c in comb])
                initial_Vn.add(exp)

    # Set difference to obtained modified grounded fluents
    constant_numeric_fluents = initial_Vn - modified_fluents

    # Save them in a disctionary with pddl str as key and initial value
    constant_with_values = {}
    for f in constant_numeric_fluents:
        txt = str(f).replace('(', ' ').replace(')', ' ').replace(',', '')
        txt = "(" + " ".join(txt.split()) + ")"
        constant_with_values[txt] = problem.initial_value(f)

    # Write grounded problem and domain in PDDL (easier but slower by writing file..)
    grounded_domain_filename = 'tmp/grounded_domain.pddl'
    grounded_problem_filename = 'tmp/grounded_problem.pddl'
    writter = PDDLWriter(problem)
    writter.write_domain(grounded_domain_filename)
    writter.write_problem(grounded_problem_filename)

    # Read grounded domain file
    with open(grounded_domain_filename, 'r') as domain_file:
        domain_str = domain_file.read()
    # Remove fluent declaration in domain
        # identify functions declaration start and end
    i1 = i2 = domain_str.find('(:functions')
    if i1!=-1:
        n = 1
        i2 += 1
        while n!=0:
            if domain_str[i2]=='(':
                n+=1
            elif domain_str[i2]==')':
                n-=1
            i2 += 1
    for f_str, initial_value in constant_with_values.items():
        fluent_name = f_str.replace('(','').replace(')','').split()[0]
        i_def = domain_str.find(f'({fluent_name}', i1, i2)
        if i_def!=-1:
            i_end = domain_str.find(')', i_def, i2)+1
            domain_str = domain_str[:i_def] + domain_str[i_end:]
    # Replace constrant fluent with initial values in domain 
    for f_str, initial_value in constant_with_values.items():
        domain_str = domain_str.replace(f_str, str(initial_value))
    # Overwrite grounded domain file
    with open(grounded_domain_filename, 'w') as domain_file:
        domain_file.write(domain_str)

    # Read grounded problem file
    with open(grounded_problem_filename, 'r') as problem_file:
        problem_str = problem_file.read()
    # Delete each constant fluent assignment
        # find f_str, delete from '(=' to next ')
    for f_str, initial_value in constant_with_values.items():
        i_f = problem_str.find(f_str)
        i1 = problem_str.rfind('(=', 0, i_f)
        i2 = problem_str.find(')',  problem_str.find(')', i_f)+1)+1
        problem_str = problem_str[:i1] + problem_str[i2:]
    # Overwrite grounded problem file
    with open(grounded_problem_filename, 'w') as problem_file:
        problem_file.write(problem_str)

    # TODO: Might need to replace in metric also... But currently not considered in milp formulation..

    # Load new problem
    reader = PDDLReader()
    problem = reader.parse_problem(grounded_domain_filename, grounded_problem_filename)

    print(f'Ok [{time.time()-t1:.2f}s]')

    #############
    ## COMPILE ##
    #############

    t1 = time.time()
    print('\tCompiles ... ', end='', flush=True)

    with Compiler(
        problem_kind=problem.kind,
        compilation_kind=CompilationKind.DISJUNCTIVE_CONDITIONS_REMOVING,
    ) as compiler:
        compilation_result = compiler.compile(problem)
        problem = compilation_result.problem

    with Compiler(
        problem_kind=problem.kind,
        compilation_kind=CompilationKind.NEGATIVE_CONDITIONS_REMOVING,
    ) as compiler:
        compilation_result = compiler.compile(problem)
        problem = compilation_result.problem
    print(f'Ok [{time.time()-t1:.2f}s]')

    # boxprint('PROBLEM')
    # print(problem)

    # with OneshotPlanner(problem_kind=problem.kind) as planner:
    if solve:
        t1=time.time()
        with OneshotPlanner(problem_kind=problem.kind, 
                optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY
        ) as planner:
            result = planner.solve(problem)
            print("%s returned: %s" % (planner.name, result.plan))
            print('plan length= ', len(result.plan.actions))
        print(f"elapsed: {time.time()-t1:.2f}s")

    #############
    ## FLUENTS ##
    #############

    t1 = time.time()
    print('\tData extraction ... ', end='', flush=True)

    Vp = []
    Vn = []
    for f in problem.fluents:
        object_sets = []
        for s in f.signature:
            objects = [str(o) for o in problem.objects(s.type)]
            object_sets.append(objects)
        combinations = list(itertools.product(*object_sets))
        for comb in combinations:
            if f.type.is_bool_type(): # Propositional
                Vp.append( "_".join( [f.name]+list(comb) )  )
            if f.type.is_real_type(): # Numeric
                Vn.append( "_".join( [f.name]+list(comb) )  )

    #############
    ## ACTIONS ##
    #############

    def contains_fluent(x):
        for f in Vn:
            if f in x:
                return True
        return False
    
    # declare k parameters from effects
    k_v_a = {}
    k_v_a_w = {}
    for f in Vn:
        k_v_a[f] = {}
        k_v_a_w[f] = {}
        for a in problem.actions:
            k_v_a[f][a.name] = 0
            k_v_a_w[f][a.name] = {}
            for w in Vn:
                k_v_a_w[f][a.name][w] = 0

    # declare w parameters from goal and preconditions
    w_c_v = {}
    w_0_c = {}

    actions = {}
    for a in problem.actions:
        actions[a.name] = {
            'pre_p':set(),
            'pre_n':set(),
            'del':set(),
            'add':set(),
            'num':set(),
        }


        ## PRECONDITIONS ##
        for p in a.preconditions:
            if p.is_fluent_exp():
                if p.type.is_bool_type():
                    p = str(p).replace('(','_').replace(', ','_').replace(')','')
                    actions[a.name]['pre_p'].add(p)
            else:
                c = normalize_equation(str(p))
                c = str(c).replace('(','_').replace(', ','_').replace(')','').replace('- ', '+ -')
                actions[a.name]['pre_n'].add(c)
                
                # Init w_c_v and w_0_c
                w_0_c[c] = 0
                w_c_v[c] = {}
                for f in Vn:
                    w_c_v[c][f] = 0

                # Extract w_c_v and w_0_c
                left_side = c.replace(' ', '').split('==')[0].split('>=')[0].split('>')[0]
                for x in left_side.split('+'):
                    if contains_fluent(x):
                        if '*' in x:
                            w_value = float(x.split('*')[0])
                            v = x.split('*')[1]
                        else:
                            w_value = 1
                            v = x
                        w_c_v[c][v] = w_value

                    else:
                        w_value = float(x)
                        w_0_c[c] = w_value

        
        ## EFFECTS ##
        for e in a.effects:
            f = str(e.fluent).replace('(','_').replace(', ','_').replace(')','')

            # Propositional effect
            if e.fluent.type.is_bool_type():
                assert e.is_assignment()
                if e.value.is_true():
                    actions[a.name]['add'].add(f)
                else:
                    actions[a.name]['del'].add(f)
                    
            # Numeric effect
            elif e.fluent.type.is_real_type():
                value = str(e.value)
                if e.is_increase():
                    value = str(e.fluent) + ' + ' + value
                elif e.is_decrease():
                    value = str(e.fluent) + ' - ' + value
            
                exp = normalize_equation(str(value))
                exp = str(exp).replace('(','_').replace(', ','_').replace(')','').replace('- ', '+ -')
                actions[a.name]['num'].add(f + ' := ' + exp)

                # Extract k values
                for x in exp.replace(' ', '').split('+'):
                    if contains_fluent(x):
                        if '*' in x:
                            k_value = float(x.split('*')[0])
                            v = x.split('*')[1]
                        else:
                            k_value = 1
                            v = x
                        
                        k_v_a_w[f][a.name][v] = k_value

                    else:
                        k_value = float(x)
                        k_v_a[f][a.name] = k_value


    #############
    ## PROBLEM ##
    #############

    # Name
    problem_name = problem.name

    # Initial State
    I = {}
    for f, initial_value in problem.initial_values.items():
        f_str = str(f).replace('(','_').replace(', ','_').replace(')','')
        if f.is_fluent_exp() and f.type.is_bool_type():
            I[f_str] = 1 if initial_value.is_true() else 0
        else:
            I[f_str] = float(str(initial_value))
        
    # Goal State
    def flatten_conjunction(expr: FNode):
        """Recursively flatten a goal FNode into a list of conjuncts."""
        if expr.is_and():
            result = []
            for child in expr.args:
                result.extend(flatten_conjunction(child))
            return result
        else:
            return [expr]
    def flatten_goals(goals):
        flat_goal = []
        for g in goals:
            flat_goal += flatten_conjunction(g)
        return flat_goal
    Gp = set()
    Gn = set()
    for f in flatten_goals(problem.goals):
        if f.is_fluent_exp() and f.type.is_bool_type():
            Gp.add(str(f).replace('(','_').replace(', ','_').replace(')',''))
        else:
            c = normalize_equation(str(f))
            c = str(c).replace('(','_').replace(', ','_').replace(')','').replace('- ', '+ -')
            Gn.add(c)
            
            # Init w_c_v and w_0_c
            w_c_v[c] = {}
            for f in Vn:
                w_c_v[c][f] = 0

            # Extract w_c_v and w_0_c
            left_side = c.replace(' ', '').split('==')[0].split('>=')[0].split('>')[0]
            for x in left_side.split('+'):
                if contains_fluent(x):
                    if '*' in x:
                        w_value = float(x.split('*')[0])
                        v = x.split('*')[1]
                    else:
                        w_value = 1
                        v = x
                    w_c_v[c][v] = w_value

                else:
                    w_value = float(x)
                    w_0_c[c] = w_value
    print(f'Ok [{time.time()-t1:.2f}s]')

        
    ############
    ## OUTPUT ##
    ############
    
    if show:
        boxprint(f'Problem name: {problem_name}')
        boxprint( boxprint('FLUENTS PROPOSITIONNAL (Vp)', show=False, mode='d') + '\n' + '\n'.join([f'- {f}' for f in Vp]))
        boxprint( boxprint('FLUENTS NUMERIC (Vn)', show=False, mode='d') + '\n' + '\n'.join([f'- {f}' for f in Vn]))
        boxprint( 
            boxprint('ACTIONS', show=False, mode='d') + '\n' + '\n'.join( ['- ' + str(a) + 
                '\n\tpre_p: ' + str(list(actions[a]['pre_p'])) + 
                '\n\tpre_n: ' + str(list(actions[a]['pre_n'])) + 
                '\n\tdel: ' + str(list(actions[a]['del'])) + 
                '\n\tadd: ' + str(list(actions[a]['add'])) +
                '\n\tnum: ' + str(list(actions[a]['num'])) 
            for a in actions] ) 
        )
        boxprint( boxprint('INIT', show=False, mode='d') + 
                 '\n' + '\n'.join( [f'- {p}' for p,v in I.items() if p in Vp and v==1] ) + 
                 '\n' + '\n'.join( [f'- {f} = {v}' for f,v in I.items() if f in Vn] ) 
                )
        boxprint( boxprint('GOAL', show=False, mode='d') + 
                 '\n' + '\n'.join( [f'- {p}' for p in Gp] ) + 
                 '\n' + '\n'.join( [f'- {c}' for c in Gn] )
                )
        
    return (problem_name, (Vp, Vn), actions, I, (Gp, Gn), (w_c_v, w_0_c, k_v_a_w, k_v_a))
    