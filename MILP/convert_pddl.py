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


all_equations = []
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

    all_equations.append((expr_str, exp_str))

    return exp_str

def parse_and_remove_dashes(domain_filename, problem_filename):
    """
    Our framework grounds the PDDL problem.
    The unified_planning replace '-' by '_' when generating PDDL.
    This is conflicting with the format used for the MILP formulation.
    Thus, the '-' are removed from the start from fluent, action, and object names.
    """

    t1 = time.time()
    print('\tParsing ... ', end='', flush=True)

    # Initial parsing from files
    reader = PDDLReader()
    problem = reader.parse_problem(domain_filename, problem_filename)

    # Clear quality metrics
    problem.clear_quality_metrics()

    dashes = ['-', '_']
    elements_to_check = problem.fluents + problem.actions + problem.all_objects

    # Stop here if no dash in fluent name nor action name nor object name
    if all(d not in x.name 
           for x in elements_to_check
           for d in dashes):
        print(f'Ok [{time.time()-t1:.2f}s]')
        return problem
    
    print(f'Ok [{time.time()-t1:.2f}s]')
    
    print('\tRemoving dashes ... ', end='', flush=True)

    # get domain and problem as string 
    writter = PDDLWriter(problem)
    domain_str = writter.get_domain() # This changes '-' to '_'
    problem_str = writter.get_problem() # This changes '-' to '_'

    # remove dashes 
    for d in dashes:
        for x in elements_to_check:
            if d in x.name:
                # print(x.name + ' -> ' + x.name.replace(d, '_') + ' -> ' + x.name.replace(d, ''))
                domain_str = domain_str.replace(x.name.replace(d, '_'), x.name.replace(d, ''))
                problem_str = problem_str.replace(x.name.replace(d, '_'), x.name.replace(d, ''))

    # parse updated string problem
    problem = reader.parse_problem_string(domain_str, problem_str)
    
    print(f'Ok [{time.time()-t1:.2f}s]')

    return problem

def grounding(problem):
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
    return problem

def replace_constant_n_fluent(problem):
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

    # Stop here if nothing to remove
    if constant_numeric_fluents == set():
        return problem

    # Save them in a disctionary with pddl str as key and initial value
    constant_with_values = {}
    for f in constant_numeric_fluents:
        txt = str(f).replace('(', ' ').replace(')', ' ').replace(',', '')
        txt = "(" + " ".join(txt.split()) + ")"
        constant_with_values[txt] = problem.initial_value(f)

    # Get domain and problem as string
    writter = PDDLWriter(problem)
    domain_str = writter.get_domain()
    problem_str = writter.get_problem()

    ## DOMAIN ##

    # Remove fluent declaration in domain
        # Check if has to be removed, if (f o1) and (f o2) are constant, maybe (f o3) isn't and thus f declaration should be kept
    constant_functions  = set( str(f).split('(')[0] for f in constant_numeric_fluents)
    modified_functions = set( str(f).split('(')[0] for f in modified_fluents)
    functions_to_remove = constant_functions - modified_functions
    if functions_to_remove:
        # identify functions declaration start and end
        i_function_decla_1 = i_function_decla_2 = domain_str.find('(:functions'); assert i_function_decla_1!=-1
        n = 1
        i_function_decla_2 += 1
        while n!=0:
            if domain_str[i_function_decla_2]=='(': n+=1
            elif domain_str[i_function_decla_2]==')': n-=1
            i_function_decla_2 += 1

        # Remove constant fluent from function declaration
        for function in functions_to_remove:
            i1 = domain_str.find(f' ({function}', i_function_decla_1, i_function_decla_2); assert i1!=-1
            i2 = domain_str.find(')', i1, i_function_decla_2)+1; assert i2!=-1
            domain_str = domain_str[:i1] + domain_str[i2:]
            i_function_decla_2 -= i2-i1

    # Replace constrant fluent with initial values in domain 
    for f_str, initial_value in constant_with_values.items():
        domain_str = domain_str.replace(f_str, str(initial_value))

    ## PROBLEM ##

    # Delete each constant fluent assignment in problem
        # find f_str, delete from '(=' to next ')
    for f_str, initial_value in constant_with_values.items():
        i_f = problem_str.find(f_str); assert i_f!=-1
        i1 = problem_str.rfind('(=', 0, i_f); assert i1!=-1
        i2 = problem_str.find(')',  problem_str.find(')', i_f)+1)+1; assert i2!=-1
        problem_str = problem_str[:i1] + problem_str[i2:]

    # Replace constant fluent with initial values in problem (should only concern metric)
    for f_str, initial_value in constant_with_values.items():
        problem_str = problem_str.replace(f_str, str(initial_value))

    # Parse updated string problem
    problem = PDDLReader().parse_problem_string(domain_str, problem_str)

    print(f'Ok [{time.time()-t1:.2f}s]')
    return problem

def addition_compilations(problem, compilation_kinds):

    t1 = time.time()
    print('\tCompiles ... ', end='', flush=True)

    for kind in compilation_kinds:
        with Compiler(
            problem_kind=problem.kind,
            compilation_kind=kind,
        ) as compiler:
            compilation_result = compiler.compile(problem)
            problem = compilation_result.problem

    print(f'Ok [{time.time()-t1:.2f}s]')

    return problem

def export_preprocessed_problem(problem):
    w = PDDLWriter(problem)
    w.write_domain('tmp/pre_dom.pddl')
    w.write_problem('tmp/pre_pb.pddl')

def solve_up(problem):
    # with OneshotPlanner(problem_kind=problem.kind) as planner:
    t1=time.time()
    with OneshotPlanner(problem_kind=problem.kind, 
            optimality_guarantee=PlanGenerationResultStatus.SOLVED_OPTIMALLY
    ) as planner:
        result = planner.solve(problem)
        print("%s returned: %s" % (planner.name, result.plan))
        print('plan length= ', len(result.plan.actions))
    print(f"Elapsed: {time.time()-t1:.2f}s")

def extract_fluents(problem):
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

    return Vp, Vn 

def contains_fluent(x: str, V):
    for f in V:
        if f in x:
            return True
    return False

def extract_actions(problem, Vp, Vn):
    
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
                    assert p in Vp
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
                    if contains_fluent(x, Vn):
                        if '*' in x:
                            w_value = float(x.split('*')[0])
                            v = x.split('*')[1]
                        else:
                            if x[0]=='-':
                                w_value = -1
                                v = x[1:]
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
                assert f in Vp
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
                    if contains_fluent(x, Vn):
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

    return actions, w_c_v, w_0_c, k_v_a, k_v_a_w

def extract_actions_affecting_fluents(actions, Vp, Vn, k_v_a_w):
    
    # PROPOSITIONAL
    def generateSetF(attr, actions, Vp):
        actions_with_v = {}
        for f in Vp:
            actions_with_v[f] = set()
            for a in actions:
                if f in actions[a][attr]:
                    actions_with_v[f] = actions_with_v[f].union({a})
        return actions_with_v
    pref = generateSetF('pre_p', actions, Vp) # actions with p in preconditions
    addf = generateSetF('add', actions, Vp) # actions with p in add effects
    delf = generateSetF('del', actions, Vp) # actions with p in del effects
    
    # NUMERICAL
    se = {} # actions with constant numeric effects affecting v, i.e. v := v + k^{v,a} in num(a)
    le = {} # actions with linear numeric effects affecting v, i.e. v := sum_{w in Vn} k^{v,a}_w * w + k^{v,a} in num(a), a not in se(v)
    for v in Vn:
        se[v] = set()
        le[v] = set()
        for a in actions:
            # check if affecting v
            affecting_v = False
            for e in actions[a]['num']:
                fluent_affected = e.split(':=')[0].strip()
                if fluent_affected == v:
                    affecting_v = True
                    break
            if not affecting_v:
                continue

            # check if constant effects
            has_constant_effects = True
            for w in Vn:
                if (w==v and k_v_a_w[v][a][v] != 1)\
                or (w!=v and k_v_a_w[v][a][w] != 0):
                    has_constant_effects = False
                    break
                
            if has_constant_effects:
                se[v].add(a)
            else:
                le[v].add(a)

    return pref, addf, delf, se, le

def extract_initial_state(problem):
    I = {}
    for f, initial_value in problem.initial_values.items():
        f_str = str(f).replace('(','_').replace(', ','_').replace(')','')
        if f.is_fluent_exp() and f.type.is_bool_type():
            I[f_str] = 1 if initial_value.is_true() else 0
        else:
            I[f_str] = float(str(initial_value))
    return I

def extract_goal(problem, Vp, Vn):

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
    w_0_c = {}
    w_c_v = {}
    for f in flatten_goals(problem.goals):
        if f.is_fluent_exp() and f.type.is_bool_type():
            f = str(f).replace('(','_').replace(', ','_').replace(')','')
            assert f in Vp
            Gp.add(str(f).replace('(','_').replace(', ','_').replace(')',''))
        else:
            c = normalize_equation(str(f))
            c = str(c).replace('(','_').replace(', ','_').replace(')','').replace('- ', '+ -')
            Gn.add(c)
            
            # Init w_c_v and w_0_c
            w_0_c[c] = 0
            w_c_v[c] = {}
            for f in Vn:
                w_c_v[c][f] = 0

            # Extract w_c_v and w_0_c
            left_side = c.replace(' ', '').split('==')[0].split('>=')[0].split('>')[0]
            for x in left_side.split('+'):
                if contains_fluent(x, Vn):
                    if '*' in x:
                        w_value = float(x.split('*')[0])
                        v = x.split('*')[1]
                    else:
                        if x[0]=='-':
                            w_value = -1
                            v = x[1:]
                        else:
                            w_value = 1
                            v = x
                    w_c_v[c][v] = w_value

                else:
                    w_value = float(x)
                    w_0_c[c] = w_value
    
    return Gp, Gn, w_c_v, w_0_c # not necessary to return w variable since they are mutable, but adds clarity

def print_info(problem_name, Vp, Vn, actions, I, Gp, Gn):
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

##############################

def load_pddl(domain_filename, problem_filename, no_data_extraction=False):
    global g_loading_problem_time

    t_begin = time.time()
    boxprint('Loading problem')

    print('domain_filename=', domain_filename)
    print('problem_filename=', problem_filename)

    up.shortcuts.get_environment().credits_stream = None
    
    ###################
    ## PREPROCESSING ##
    ###################

    ## PARSE and REMOVE DASHES in names ##
    problem = parse_and_remove_dashes(domain_filename, problem_filename)

    ## GROUNDING ##
    problem = grounding(problem)

    ## REPLACE CONSTANT NUM FLUENT WITH VALUE ##
    problem = replace_constant_n_fluent(problem)

    ## COMPILE ##
    problem = addition_compilations(problem, [
        CompilationKind.DISJUNCTIVE_CONDITIONS_REMOVING,
        CompilationKind.NEGATIVE_CONDITIONS_REMOVING,
    ])

    ## Export preprocessed problem
    export_preprocessed_problem(problem)

    if no_data_extraction:
        g_loading_problem_time = time.time()-t_begin
        print(f"[Loading Problem: {g_loading_problem_time:.2f}s]")
        return (problem.name, problem, None)

    #####################
    ## DATA EXTRACTION ##
    #####################

    t1 = time.time()
    print('\tData extraction ... ', end='', flush=True)

    #### DOMAIN RELATED ####
    
    ## FLUENTS ##
    Vp, Vn = extract_fluents(problem)

    ## ACTIONS ##
    actions, w_c_v_pre, w_0_c_pre, k_v_a, k_v_a_w = extract_actions(problem, Vp, Vn)
   
    ## ACTION SETS AFFECTING FLUENT ##

    pref, addf, delf, se, le = extract_actions_affecting_fluents(actions, Vp, Vn, k_v_a_w)

    #### PROBLEM RELATED ####

    ## PROBLEM NAME ##
    problem_name = problem.name

    ## INITIAL STATE ##
    I = extract_initial_state(problem)
        
    ## GOAL ##
    Gp, Gn, w_c_v_goal, w_0_c_goal = extract_goal(problem, Vp, Vn)

    # Merge preconditions and goal w_c_v and w_0_c
    w_c_v = w_c_v_pre | w_c_v_goal
    w_0_c = w_0_c_pre | w_0_c_goal

    print(f'Ok [{time.time()-t1:.2f}s]')


    g_loading_problem_time = time.time()-t_begin
    print(f"[Loading Problem: {g_loading_problem_time:.2f}s]")

    return (problem_name, problem, ((Vp, Vn), actions, I, (Gp, Gn), (w_c_v, w_0_c, k_v_a_w, k_v_a), (pref, addf, delf, se, le)))

    