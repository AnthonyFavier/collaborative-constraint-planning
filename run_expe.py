import solving
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
from datetime import datetime

# job function
def job(problem, mode, time_budget, id, max_id):
    job_name = f"Job:{id}/{max_id} " + "-".join([problem, mode, str(time_budget)])
    t0 = time.time()
    
    time_formatted = '[' + datetime.now().strftime("%H:%M:%S") + ']'
    print(time_formatted + " Start - " + job_name)
    
    try:
        solving.cli([mode, '-p', problem, str(time_budget), '--hideprogressbar'])
    except SystemExit as err:
        if err.code:
            raise
    # time.sleep(time_budget)
    
    t1 = time.time()
    time_formatted = '[' + datetime.now().strftime("%H:%M:%S") + ']'
    print(time_formatted + " Completed - " + job_name + f" [{t1-t0:.1f}s]")
    return None

# Create job list
modes = ['original', 'randomc', 'h-translation']
problems = ['Rover10_n_t']
time_budgets = [60, 90, 120, 200, 300, 400]
# time_budgets = [1, 2, 3, 4]
max_id = len(modes)*len(problems)*len(time_budgets)

job_list = []
id = 0
for problem in problems:
    for mode in modes:
        for tb in time_budgets:
            job_list.append([problem, mode, tb, id, max_id])
            id+=1
for problem in problems:
    solving.init_global_constraints(problem)

# Use a thread pool with max 6 workers
max_workers = 6
with ProcessPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(job, *job_params) for job_params in job_list]
    remaining = len(job_list)
    for future in as_completed(futures):
        remaining -= 1
        time_formatted = '[' + datetime.now().strftime("%H:%M:%S") + ']'
        print(time_formatted + "\t> " + str(remaining) + " jobs remaining")