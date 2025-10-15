from MILP.solve_milp import mainCLI as milpCLI
from MILP.solve_milp import main as milp
from MILP.solve_milp import up_solve

from MILP.boxprint import boxprint

def run_compare():
    results = {}

    filename = 'compare_results_up.txt'

    f = open(filename, 'w')
    f.close()

    for i in range(1, 11):
        problem_name = f'problem{i}'
        boxprint(problem_name, mode='d')
        with open(filename, 'a') as f:
            f.write(f'{problem_name}:\n')

        ################
        ## UP SOLVING ##
        ################
        plan_str, plan_length, duration = up_solve(i)

        instance_result = {'plan': plan_str, 'plan_length': plan_length, 'duration': duration}
        if problem_name not in results: results[problem_name] = {}
        results[problem_name]['UP'] = instance_result
        with open(filename, 'a') as f:
            f.write(f'\tUP  : length={plan_length} duration={duration:.2f}s\n\t{plan_str}\n')
        print(f'\tUP  : length={plan_length} duration={duration:.2f}s\n\t{plan_str}\n')


if __name__=='__main__':
    run_compare()

