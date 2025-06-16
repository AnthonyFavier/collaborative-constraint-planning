import json
import sys
import click
import numpy as np
import matplotlib.pyplot as plt

@click.command()
@click.argument('filename')
def main_cli(filename):
    main(filename)
    
def main(filename):
    print(f'File: {filename}')
    with open(filename, 'r') as f:
        raw_data = json.loads(f.read())
    
    data = {}
    
    # EXTRACTION
    tests = raw_data['tests']
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
        metrics = -1
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
            
    elapsed = raw_data['elapsed'] if 'elapsed' in raw_data else 'Interrupted'
    
    # SAVE extracted
    data['seed'] = raw_data['seed']
    data['timeout'] = raw_data['timeout']
    data['Repeated'] = 100*repeated/len(tests)
    data['Type_repartition'] = {
        'SIMPLE': 100*len(simple)/len(tests),
        'AND2': 100*len(and2)/len(tests),
        'AND3': 100*len(and3)/len(tests),
        'OR2': 100*len(or2)/len(tests),
        'OR3': 100*len(or3)/len(tests),
    }
    data['success'] = {
            'ratio': 100*len(successful)/len(tests),
            'Timeout': 100*len(timeout)/len(tests),
            'Unsolvable': 100*len(unsolvable)/len(tests),
    }
    if successful!=[]:
        data['metrics'] = {
            'all': metrics,
            'mean': mean,
            'std': std,
            'best': min_metric
        }
    data['elapsed'] = elapsed
    
    # PRINT
    
    print(f"Repeated = {data['Repeated']:.1f}%")
    print('Constraint types:')
    print('\tSIMPLE: ' + '{:.1f}'.format(data['Type_repartition']['SIMPLE']) + '%')
    print('\tAND2: ' + '{:.1f}'.format(data['Type_repartition']['AND2']) + '%')
    print('\tAND3: ' + '{:.1f}'.format(data['Type_repartition']['AND3']) + '%')
    print('\tOR2: ' + '{:.1f}'.format(data['Type_repartition']['OR2']) + '%')
    print('\tOR3: ' + '{:.1f}'.format(data['Type_repartition']['OR3']) + '%')
    print('Success = ' + '{:.1f}'.format(data['success']['ratio']) + '%')
    print('\tTimeout = ' + '{:.1f}'.format(data['success']['Timeout']) + ' %')
    print('\tUnsolvable = ' + '{:.1f}'.format(data['success']['Unsolvable']) + '%')
    if successful!=[]:
        print('Metric = ' + '{:.1f}'.format(data['metrics']['mean']) + '+-' + '{:.1f}'.format(data['metrics']['std']))
        print('Best = ' + '{:.1f}'.format(data['metrics']['best']))
    print('Elasped = ' + data['elapsed'])
    
    return data
    
def several():
    seed0 = False
    seed6671597656599831408 = False
    
    seed0 = True
    # seed6671597656599831408 = True
    
    if seed0:
        files = [
            'results_constraints/seed0/50-200-TO1_06-16-2025_13:35:00.json',
            'results_constraints/seed0/50-200-TO3_06-16-2025_13:35:00.json',
            'results_constraints/seed0/50-200-TO5_06-16-2025_13:35:00.json',
            'results_constraints/seed0/50-200-TO10_06-16-2025_13:35:01.json',
        ]
    
    if seed6671597656599831408:
        files = [
            'results_constraints/seed6671597656599831408/50-200-TO1_06-16-2025_15:27:06.json',
            'results_constraints/seed6671597656599831408/50-200-TO3_06-16-2025_15:27:06.json',
            'results_constraints/seed6671597656599831408/50-200-TO5_06-16-2025_15:27:07.json',
            'results_constraints/seed6671597656599831408/50-200-TO10_06-16-2025_15:27:07.json',
        ]
    
    datas = []
    for f in files:
        datas.append(main(f))
        
    seed = datas[-1]['seed']
    unsolvable = datas[-1]['success']['Unsolvable']
    x_labels = [int(d['timeout']) for d in datas]
    x_pos = np.arange(len(x_labels)) 
    
    box_data = []
    box_pos = []
    for i,d in enumerate(datas):
        if 'metrics' in d:
            box_data.append(d['metrics']['all'])
            box_pos.append(i)
    
    line_data = []  
    for d in datas:
        line_data.append(d['success']['ratio'])
        
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
    
    axs[0].violinplot(box_data,
            positions=box_pos,
            showmeans=False,
            showmedians=True,
        )
    # axs[0].boxplot(box_data, positions=box_pos,
    #         patch_artist=True,
    #         widths=0.8,
    #         showmeans=False, 
    #         # showfliers=False,
    #         medianprops={"color": "white", "linewidth": 0.5},
    #         boxprops={"facecolor": "C0", "edgecolor": "white", "linewidth": 0.5},
    #         whiskerprops={"color": "C0", "linewidth": 1.5},
    #         capprops={"color": "C0", "linewidth": 1.5}
    #     )
    axs[0].set_ylabel("Metric values")
    axs[0].set_title("Seed" + str(seed) + ' metric and succes rate (Unsolvable=' + '{:.1f}'.format(unsolvable) + '%)')
    axs[0].tick_params(labelbottom=True)  # <-- Show x labels on top plot
    axs[0].set_ylim(ymax=90000)
    # axs[0].yaxis.grid(True)
    
    
    axs[1].plot(x_pos, line_data, marker='o')
    axs[1].axhline(y=100-unsolvable, color="black", linestyle="--")
    axs[1].set(ylim=(0, 100))
    axs[1].set_ylabel("Success ratio (%)")
    axs[1].set_xlabel("Timeout (s)")
    
    plt.xticks(ticks=x_pos, labels=x_labels)
    
    plt.tight_layout()
    plt.show()
    exit()
    

if __name__=='__main__':
    # sys.argv += ['50-200-TO5_06-16-2025_10:07:57.json']
    # main_cli()
    
    several()