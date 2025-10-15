from MILP.solve_milp import mainCLI as milpCLI
from MILP.solve_milp import main as milp
from MILP.solve_milp import up_solve

from MILP.boxprint import boxprint

def run_compare():
    results = {}

    filename = 'compare_results_milp.txt'

    f = open(filename, 'w')
    f.close()

    for i in range(1, 11):
        problem_name = f'problem{i}'
        boxprint(problem_name, mode='d')
        with open(filename, 'a') as f:
            f.write(f'{problem_name}:\n')

        ##################
        ## MILP SOLVING ##
        ##################
        plan_str, plan_length, duration, last_solving_duration, build_model = milp(T_min=1, T_max=100, T_user=None, sol_gap=None, sequential=True, export=False, n_problem=i)

        instance_result = {'plan': plan_str, 'plan_length': plan_length, 'duration': duration, 'last_solve': last_solving_duration, 'build_model': build_model}
        if problem_name not in results: results[problem_name] = {}
        results[problem_name]['MILP'] = instance_result
        with open(filename, 'a') as f:
            f.write(f'\n\tMILP: length={plan_length} duration={duration:.2f}s (build={build_model:.2f}s last={last_solving_duration:.2f}s => {build_model+last_solving_duration:.2f}s)\n\t{plan_str}\n\n')
        print(f'\n\tMILP: length={plan_length} duration={duration:.2f}s (build={build_model:.2f}s last={last_solving_duration:.2f}s => {build_model+last_solving_duration:.2f}s)\n\t{plan_str}\n\n')

if __name__=='__main__':
    run_compare()

