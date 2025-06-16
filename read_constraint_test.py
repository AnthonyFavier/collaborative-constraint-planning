import json
import sys
import click
import numpy as np
import matplotlib.pyplot as plt

@click.command()
@click.argument('filename')
def main(filename):
    with open(filename, 'r') as f:
        data = json.loads(f.read())
        
    # print(data)
    
    # Get best metric
    tests = data['tests']
    
    successful = []
    timeout = []
    unsolvable = []
    simple = []
    and2 = []
    and3 = []
    or2 = []
    or3 = []
    for t in tests:
        if t['result']=='success':
            successful.append(t)
        elif t['reason']=='Timeout':
            timeout.append(t)
        elif t['reason']=='Unsolvable Problem':
            unsolvable.append(t)
            
        if t['constraint_type']=="SIMPLE":
            simple.append(t)
        elif t['constraint_type']=="AND2":
            and2.append(t)
        elif t['constraint_type']=="AND3":
            and3.append(t)
        elif t['constraint_type']=="OR2":
            or2.append(t)
        elif t['constraint_type']=="OR3":
            or3.append(t)
    
    if successful!=[]:
        metrics = np.array([t['metric'] for t in successful])
        mean = metrics.mean()
        std = metrics.std()
        min_metric = metrics.min()
    else:
        mean = -1
        std = -1
        min_metric = -1
    
    constraints = [t['constraint'] for t in tests]
    my_dict = {x:constraints.count(x) for x in constraints}
    repeated = 0
    for k,n in my_dict.items():
        if n>1:
            print(f'\t{n}: {k}')
            repeated+=1
    
    print(f"Repeated = {100*repeated/len(tests):.1f}%")
    print('Constraint types:')
    print(f'\tSIMPLE: {100*len(simple)/len(tests):.1f}%')
    print(f'\tAND2: {100*len(and2)/len(tests):.1f}%')
    print(f'\tAND3: {100*len(and3)/len(tests):.1f}%')
    print(f'\tOR2: {100*len(or2)/len(tests):.1f}%')
    print(f'\tOR3: {100*len(or3)/len(tests):.1f}%')
    
    print(f"Success = {100*len(successful)/len(tests):.1f}%")
    print(f"\tTimeout = {100*len(timeout)/len(tests):.1f}%")
    print(f"\tUnsolvable = {100*len(unsolvable)/len(tests):.1f}%")
    print(f"Metric = {mean:.1f} +- {std:.1f}")
    print(f"Best = {min_metric:.1f}")
    
    if 'elapsed' not in data:
        print('Elapsed= Interrupted')
    else:
        print('Elapsed= ', data['elapsed'])
    
    
    if successful!=[]:
        fig, ax = plt.subplots()
        x_to = [10]
        y_metric = [metrics]
        VP = ax.boxplot(metrics, positions=[10], widths=1.5, patch_artist=True,
                    showmeans=False, showfliers=False,
                    medianprops={"color": "white", "linewidth": 0.5},
                    boxprops={"facecolor": "C0", "edgecolor": "white",
                            "linewidth": 0.5},
                    whiskerprops={"color": "C0", "linewidth": 1.5},
                    capprops={"color": "C0", "linewidth": 1.5})

        # ax.set(xlim=(0, 8), xticks=np.arange(1, 8), ylim=(0, 8), yticks=np.arange(1, 8))    
        # ax.set(xlim=(0, 12), xticks=np.arange(1, 12))

        plt.show()
    


if __name__=='__main__':
    # sys.argv += ['50-200-TO5_06-16-2025_10:07:57.json']
    main()