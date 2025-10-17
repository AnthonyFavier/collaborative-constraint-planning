from run_compare_milp import run_compare as run_milp
from run_compare_up import run_compare as run_up
from MILP.start_with_timer import start_with_timer
import time

if __name__=='__main__':

    domains = ['counters', 'zenotravel', 'rover']
    timeout = 300
    for d in domains:
        start_with_timer(timeout, run_milp, d, i_start=1, i_last=20)
        time.sleep(1)
        start_with_timer(timeout, run_up, d, i_start=1, i_last=20)
        time.sleep(1)