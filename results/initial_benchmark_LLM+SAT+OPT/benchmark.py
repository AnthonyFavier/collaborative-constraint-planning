
import planner as P
import time
from defs import *

planners = [
    "sat-hmrp",
    "sat-hmrph", # best sat
    "sat-hmrphj",
    "sat-hmrpff",
    
    "sat-hadd",
    "sat-hradd",
    
    "sat-aibr",
    
    # Don't work
    # "opt-hlm",
    # "opt-hlmrd",
    
    "opt-blind",
    
    "opt-hmax", # best opt
    "opt-hrmax",
    
    PlanMode.DEFAULT,
    PlanMode.ANYTIME,
    PlanMode.ANYTIMEAUTO,
    ]

timeout = None

g_txt = ""
def pprint(txt, end='\n', flush=False):
    global g_txt
    g_txt += txt + end
    print(txt, end=end, flush=flush) 

for plan_mode in planners:

    pprint("plan_mode: " + plan_mode)
    pprint("timeout: " + str(timeout))
    for i in range(0,16):
        
        pprint(f"\nzeno{i}: ", end="")
        times = []
        for j in range(2):
            t1 = time.time_ns()
            
            feedback, plan, stdout = P.planner(f"zeno{i}", plan_mode=plan_mode, hide_plan=True, timeout=timeout)
            r = stdout
            
            t = "Grounding Time: "
            i_s = r.rfind(t)+len(t)
            i_end = r.find('\n', i_s)
            ground_time = float(r[i_s:i_end])
            tot_time=ground_time
            
            # t = "Setup Time (msec): "
            # i_s = r.find(t)+len(t)
            # if i_s-len(t)!=-1:
            #     i_end = r.find('\n', i_s)
            #     setup_time = float(r[i_s:i_end])
            #     tot_time+=setup_time
            
            t = "Planning Time (msec): "
            i_s = r.rfind(t)+len(t)
            if i_s-len(t)==-1:
                pprint(f"failed ", end="", flush=True)
                continue
            i_end = r.find('\n', i_s)
            planning_time = float(r[i_s:i_end] if i_end!=-1 else r[i_s:])
            tot_time+=planning_time
            
            times.append(tot_time)
            
            t = "Metric (Search):"
            i_metric = r.rfind(t)+len(t)
            i_metric_end = r.find("\n", i_metric)
            metric = float(r[i_metric:i_metric_end])
            
            t = "Found Plan:\n"
            i_plan = r.rfind(t)+len(t)
            i_plan_end = r.find('\n\nPlan-Length', i_plan)
            plan = r[i_plan:i_plan_end]
            
            pprint(f"{tot_time}ms ", end="", flush=True)
        if times==[]:
            pprint("\n\tfailed domain...")
        else:
            # pprint(f"\n\tm={metric} average time = {sum(times)/len(times):.2f}ms")
            pprint(f"\n\tm= average time = {(time.time_ns()-t1)/1000000:.2f}ms")
            pprint(plan)

    to = timeout if timeout!=None else 0
    t = time.time()
    with open(f"benchmark/bench_results_{plan_mode}_{to}_{t}", 'w') as f:
        f.write(g_txt)
        g_txt = ""