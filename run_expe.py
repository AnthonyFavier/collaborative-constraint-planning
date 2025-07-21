import solving
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
from datetime import datetime

# job function
def job(problem, mode, time_budget, id):
    time.sleep(0.1)
    job_name = f"Job:{id}/{len(job_list)} " + "-".join([problem, mode, str(time_budget)])
    t0 = time.time()
    
    time_formatted = '[' + datetime.now().strftime("%H:%M:%S") + ']'
    print(time_formatted + " Start - " + job_name)
    
    try:
        solving.cli([mode, '-p', problem, str(time_budget), '--hideprogressbar'])
    except SystemExit as err:
        if err.code:
            raise
    
    t1 = time.time()
    time_formatted = '[' + datetime.now().strftime("%H:%M:%S") + ']'
    print(time_formatted + " Completed - " + job_name + f" [{t1-t0:.1f}s]")
    return None

# Create job list
job_list = []
id = 1

modes = ['original', 'randomc', 'h-translation']
problems = ['ZenoTravel13', 'Rover10_n_t']
time_budgets = [60, 90, 120, 200, 300, 400]
for problem in problems:
    for mode in modes:
        for tb in time_budgets:
            job_list.append([problem, mode, tb, id])
            id+=1
            
# Init global constraints
all_problems = set()
for j in job_list:
    if j[0] not in all_problems:
        all_problems.union(set([j[0]]))
for problem in all_problems:
    solving.init_global_constraints(problem)

# Use a process pool with max 10 workers
max_workers = 10
with ProcessPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(job, *job_params) for job_params in job_list]
    remaining = len(job_list)
    for future in as_completed(futures):
        remaining -= 1
        time_formatted = '[' + datetime.now().strftime("%H:%M:%S") + ']'
        print(time_formatted + "\t> " + str(remaining) + " jobs remaining")