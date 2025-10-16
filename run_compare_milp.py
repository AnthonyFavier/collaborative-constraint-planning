from MILP.solve_milp import main as milp
from MILP.solve_milp import get_problem_filenames

from MILP.boxprint import boxprint
import time
import json



def run_compare(domain_name, i_start=1, i_last=10, classical=False):
    results = {}
    data = {
        'domain_name': domain_name,
        'classical': classical,
        'time_start': time.time(),
        'results': results,
    }

    json_filename = 'dump_results_milp.json'

    for i in range(i_start, i_last):
        problem_name = f'problem{i}'
        boxprint(problem_name, mode='d')

        domain_filename, problem_filename = get_problem_filenames(domain_name, i, classical=classical)

        if problem_name not in results: results[problem_name] = {}
        results[problem_name]['MILP'] = {
            'domain_filename': domain_filename,
            'problem_filename': problem_filename,
        }

        ##################
        ## MILP SOLVING ##
        ##################
        plan_str, plan_length, durations = milp(T_min=1, T_max=200, T_user=None, sol_gap=None, sequential=True, domain_name=None, i_instance=None, domain_filename=domain_filename, problem_filename=problem_filename)
        loading_time, last_building_model, last_solving_time, total_solving_time = durations

        plan = [a.split(': ')[1] for a in plan_str.split(' | ')]

        instance_result = {
            'time_solved': time.time(),
            'plan': plan,
            'plan_length': plan_length,
            'loading_time': loading_time,
            'last_building_model': last_building_model,
            'last_solving_time': last_solving_time,
            'total_last':loading_time+last_building_model+last_solving_time,
            'total_solving_time': total_solving_time,
        }
        
        results[problem_name]['MILP'].update(instance_result)
        with open(json_filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f'\tMILP: length={plan_length} total time={total_solving_time:.2f}s (load={loading_time:.2f}s last_build={last_building_model:.2f}s last_solve={last_solving_time:.2f}s => {loading_time+last_building_model+last_solving_time:.2f}s)\n\t{plan_str}\n')



from MILP.start_with_timer import start_with_timer
if __name__ == "__main__":
    start_with_timer(300, run_compare, 'counters', i_start=1, i_last=5)
