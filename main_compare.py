from run_compare_milp import run_compare as run_milp
from run_compare_up import run_compare as run_up
from MILP.start_with_timer import start_with_timer
import time

if __name__=='__main__':

    domains = ['counters', 'zenotravel', 'rover']
    domains = ['airport', 'blocks', 'childsnack']
    domains = ['childsnack']
    timeout = 300
    wait_between = 3
    for d in domains:
        start_with_timer(timeout, run_milp, d, i_start=1, i_last=20, classical=True)
        time.sleep(wait_between)
        start_with_timer(timeout, run_up, d, i_start=1, i_last=20, classical=True)
        time.sleep(wait_between)


# taskset -c 0 runsolver -C 1800 -M 4096 python3 myplanner.py domain.pddl problem.pddl
