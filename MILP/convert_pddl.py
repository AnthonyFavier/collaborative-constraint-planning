import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.engines import PlanGenerationResultStatus
import itertools

from MILP.boxprint import boxprint

from sympy import expand, simplify
from sympy.parsing.sympy_parser import parse_expr

def normalize_equation(expr_str):
    rel_ops = ['<=', '>=', '<', '>', '==', '!=']

    expr_str = str(simplify(expr_str))
    
    for op in rel_ops:
        if op in expr_str:
            lhs_str, rhs_str = expr_str.split(op, 1)
            lhs = parse_expr(lhs_str, evaluate=False)
            rhs = parse_expr(rhs_str, evaluate=False)
            
            expr = expand(lhs - rhs)
            
            # Convert <, <= into >, >= by flipping sign
            if op == '<':
                expr = -expr
                op = '>'
            elif op == '<=':
                expr = -expr
                op = '>='
            
            # Expand and simplify
            expr = simplify(expand(expr)).evalf()
            
            return f"{expr} {op} 0"
    
    # If no relational operator, just expand
    return str(simplify(expand(parse_expr(expr_str, evaluate=False))))

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
    # with Compiler(name="fast-downward-grounder") as compiler:
    with Compiler(name="up_grounder") as compiler:
        compilation_result = compiler.compile(problem, CompilationKind.GROUNDING)
        problem = compilation_result.problem

    #############################################
    ## REPLACE CONSTRANT NUM FLUENT WITH VALUE ##
    #############################################
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
    grounded_domain_filename = 'grounded_domain.pddl'
    grounded_problem_filename = 'grounded_problem.pddl'
    writter = PDDLWriter(problem)
    writter.write_domain(grounded_domain_filename)
    writter.write_problem(grounded_problem_filename)

    # Read grounded domain file
    with open(grounded_domain_filename, 'r') as domain_file:
        domain_str = domain_file.read()
    # Replace constrant fluent with initial values in domain 
    for f_str, initial_value in constant_with_values.items():
        domain_str = domain_str.replace(f_str, str(initial_value))
    # Remove fluent declaration in domain
    for f_str, initial_value in constant_with_values.items():
        fluent_name = f_str.replace('(','').replace(')','').split()[0]
        i_def = domain_str.find(f'({fluent_name}')
        if i_def!=-1:
            i_end = domain_str.find(')', i_def)+1
            domain_str = domain_str[:i_def] + domain_str[i_end:]
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


    #############
    ## COMPILE ##
    #############

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

    # boxprint('PROBLEM')
    # print(problem)

    # with OneshotPlanner(problem_kind=problem.kind) as planner:
    if solve:
        import time
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
    k = {}
    k_w = {}
    for f in Vn:
        k[f] = {}
        k_w[f] = {}
        for a in problem.actions:
            k[f][a.name] = 0
            k_w[f][a.name] = {}
            for w in Vn:
                k_w[f][a.name][w] = 0

    # declare w parameters from goal and preconditions
    w = {}
    w_0 = {}

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
                
                # Init w and w_0
                w[c] = {}
                for f in Vn:
                    w[c][f] = 0

                # Extract w and w_0
                left_side = c.replace(' ', '').split('==')[0].split('>=')[0].split('>')[0]
                for x in left_side.split('+'):
                    if contains_fluent(x):
                        if '*' in x:
                            w_value = float(x.split('*')[0])
                            v = x.split('*')[1]
                        else:
                            w_value = 1
                            v = x
                        w[c][v] = w_value

                    else:
                        w_value = float(x)
                        w_0[c] = w_value

        
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
                        
                        k_w[f][a.name][v] = k_value

                    else:
                        k_value = float(x)
                        k[f][a.name] = k_value


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
            I[f_str] = initial_value
        
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
            
            # Init w and w_0
            w[c] = {}
            for f in Vn:
                w[c][f] = 0

            # Extract w and w_0
            left_side = c.replace(' ', '').split('==')[0].split('>=')[0].split('>')[0]
            for x in left_side.split('+'):
                if contains_fluent(x):
                    if '*' in x:
                        w_value = float(x.split('*')[0])
                        v = x.split('*')[1]
                    else:
                        w_value = 1
                        v = x
                    w[c][v] = w_value

                else:
                    w_value = float(x)
                    w_0[c] = w_value

        
    ############
    ## OUTPUT ##
    ############
    
    if show:
        boxprint(f'Problem name: {problem_name}')
        boxprint( boxprint('FLUENTS', show=False, mode='d') + '\n' + '\n'.join([f'- {gf}' for gf in Vp]))
        list_prep_p = list(actions[a]['prep_p'])
        list_del_p = list(actions[a]['del_p'])
        list_add_p = list(actions[a]['add_p'])
        boxprint( 
            boxprint('ACTIONS', show=False, mode='d') + 
            '\n' + '\n'.join( [f'- {a}\n\tpre: {list_prep_p}\n\tdel: {list_del_p}\n\tadd: {list_add_p}' for a in actions] ) 
        )
        boxprint( boxprint('INIT', show=False, mode='d') + '\n' + '\n'.join( [f'\t- {p}' for p in Ip] ) )
        boxprint( boxprint('GOAL', show=False, mode='d') + '\n' + '\n'.join( [f'\t- {p}' for p in Gp] ) )
        
    return (problem_name, (Vp, Vn), actions, I, (Gp, Gn), (w, w_0, k_w, k))
    