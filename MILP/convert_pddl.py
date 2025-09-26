import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io import PDDLReader, PDDLWriter
from unified_planning.engines import PlanGenerationResultStatus
import itertools
from boxprint import boxprint

def load_pddl(domain_filename, problem_filename, show=False, solve=False):
    up.shortcuts.get_environment().credits_stream = None
    
    #############
    ## PARSING ##
    #############
    reader = PDDLReader()
    problem = reader.parse_problem(domain_filename, problem_filename)

    #############
    ## COMPILE ##
    #############
    with Compiler(
        problem_kind=problem.kind,
        compilation_kind=CompilationKind.GROUNDING,
    ) as compiler:
        compilation_result = compiler.compile(problem)
        problem = compilation_result.problem

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
    for f in problem.fluents:
        object_sets = []
        for s in f.signature:
            objects = [str(o) for o in problem.objects(s.type)]
            object_sets.append(objects)
        
        combinations = list(itertools.product(*object_sets))
        for comb in combinations:
            Vp.append( "_".join( [f.name]+list(comb) )  )


    #############
    ## ACTIONS ##
    #############

    actions = []
    pre_p = {}
    del_p = {}
    add_p = {}
    for a in problem.actions:
        
        pre = []
        for p in a.preconditions:
            if p.is_fluent_exp() and p.type.is_bool_type():
                p = str(p).replace('(','_').replace(', ','_').replace(')','')
                pre.append(p)
            else:
                raise Exception("fluent type not supported")
        
        add_eff = []
        del_eff = []
        for e in a.effects:
            if e.is_assignment():
                f = str(e.fluent).replace('(','_').replace(', ','_').replace(')','')
                if e.value.is_true(): # Forced by NEGATIVE_CONDITIONS_REMOVING
                    add_eff.append(f)
                else:
                    del_eff.append(f)
                    
            elif e.is_increase() or e.is_decrease():
                raise Exception("Effect type not supported...")
            
        actions.append(a.name)
        pre_p[a.name] = set(pre)
        del_p[a.name] = set(del_eff)
        add_p[a.name] = set(add_eff)
        

    #############
    ## PROBLEM ##
    #############

    # Name
    problem_name = problem.name

    # Initial State
    Ip = []
    for f, value in problem.initial_values.items():
        if f.is_fluent_exp() and f.type.is_bool_type():
            if value.is_true(): # Forced by NEGATIVE_CONDITIONS_REMOVING
                Ip.append(str(f).replace('(','_').replace(', ','_').replace(')',''))
        else:
            raise Exception("fluent type not supported")
        

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

    # Goal State
    Gp = []
    for f in flatten_goals(problem.goals):
        if f.is_fluent_exp() and f.type.is_bool_type():
            Gp.append(str(f).replace('(','_').replace(', ','_').replace(')',''))
        else:
            raise Exception("fluent type not supported")
        
    ############
    ## OUTPUT ##
    ############
    
    if show:
        boxprint(f'Problem name: {problem_name}')
        boxprint( boxprint('FLUENTS', show=False, mode='d') + '\n' + '\n'.join([f'- {gf}' for gf in Vp]))
        boxprint( boxprint('ACTIONS', show=False, mode='d') + '\n' + '\n'.join( [f'- {a}\n\tpre: {list(pre_p[a])}\n\tdel: {list(del_p[a])}\n\tadd: {list(add_p[a])}' for a in actions] ) )
        boxprint( boxprint('INIT', show=False, mode='d') + '\n' + '\n'.join( [f'\t- {p}' for p in Ip] ) )
        boxprint( boxprint('GOAL', show=False, mode='d') + '\n' + '\n'.join( [f'\t- {p}' for p in Gp] ) )
        
    return (Vp, actions, pre_p, del_p, add_p, problem_name, Ip, Gp)
    