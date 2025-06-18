from pathlib import Path
import json
import sys
import click
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

@click.command()
@click.argument('filename')
def main_cli(filename):
    extract_result_with_constraint(filename)
    
def extract_result_with_constraint(filename):
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

def extract_result_without_constraint(filename):
    print(f'File: {filename}')
    with open(filename, 'r') as f:
        raw_data = json.loads(f.read())
    
    data = {}
    
    # EXTRACTION
    tests = raw_data['tests']
    successful = []
    timeout = []
    unsolvable = []
    for t in tests:
        if t['result']=='success':
            successful.append(t)
        elif t['reason']=='Timeout':
            timeout.append(t)
        elif t['reason']=='Unsolvable Problem':
            unsolvable.append(t)
            
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
        
    elapsed = raw_data['elapsed'] if 'elapsed' in raw_data else 'Interrupted'
    
    # SAVE extracted
    data['timeout'] = raw_data['timeout']
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
    
    print('Success = ' + '{:.1f}'.format(data['success']['ratio']) + '%')
    print('\tTimeout = ' + '{:.1f}'.format(data['success']['Timeout']) + ' %')
    print('\tUnsolvable = ' + '{:.1f}'.format(data['success']['Unsolvable']) + '%')
    if successful!=[]:
        print('Metric = ' + '{:.1f}'.format(data['metrics']['mean']) + '+-' + '{:.1f}'.format(data['metrics']['std']))
        print('Best = ' + '{:.1f}'.format(data['metrics']['best']))
    print('Elasped = ' + data['elapsed'])
    
    return data

def get_two_level_folder_dict(base_path):
    base_path = Path(base_path)
    folder_dict = {}

    for category in base_path.iterdir():
        if category.is_dir():
            sub_dict = {}
            for subcategory in category.iterdir():
                if subcategory.is_dir():
                    files = [str(Path(subcategory, f.name)) for f in subcategory.iterdir() if f.is_file()]
                    sub_dict[subcategory.name] = files
            folder_dict[category.name] = sub_dict

    return folder_dict

labels = []
def add_label(violin, label):
    color = violin["bodies"][0].get_facecolor().flatten()
    labels.append((mpatches.Patch(color=color), label))

def several():
    
    all_files = get_two_level_folder_dict('results_constraints')
    
    problem_name = 'zenotravel13'
    with_constraints_folder = 'seed6671597656599831408'
    without_constraints_folder = 'WO10'
    
    datas = []
    for f in all_files[problem_name][with_constraints_folder]:
        datas.append(extract_result_with_constraint(f))
        
    datas_wo = []
    for f in all_files[problem_name][without_constraints_folder]:
        datas_wo.append(extract_result_without_constraint(f))
        
    seed = datas[-1]['seed']
    unsolvable = datas[-1]['success']['Unsolvable']
    # x_labels = [int(d['timeout']) for d in datas]
    x_labels = [1, 3, 5, 10, 15, 30]
    x_pos = np.arange(len(x_labels)) 
    
    # With constraints data
    box_data = []
    box_pos = []
    for i,d in enumerate(datas):
        if 'metrics' in d:
            box_data.append(d['metrics']['all'])
            # box_pos.append(i)
            for j in range(len(x_labels)):
                if d['timeout']==x_labels[j]:
                    box_pos.append(j)
                    break
            
    # Without constraints data
    # box_wo_data = [[10000,20000,30000,40000,50000],[10000,20000,30000,40000,50000],[10000,20000,30000,40000,50000],[10000,20000,30000,40000,50000]]
    # box_wo_pos = [0, 1, 2, 3]
    box_wo_data = []
    box_wo_pos = []
    for i,d in enumerate(datas_wo):
        if 'metrics' in d:
            box_wo_data.append(d['metrics']['all'])
            for j in range(len(x_labels)):
                if d['timeout']==x_labels[j]:
                    box_wo_pos.append(j)
                    break
    
    
    # Success ratio data with
    line_data = []
    line_pos = []
    for i in range(len(x_labels)):
        for d in datas:
            if d['timeout']==x_labels[i]:
                line_data.append(d['success']['ratio'])
                line_pos.append(i)
                break
    
    # Success ratio data without
    line_wo_data = []
    line_wo_pos = []
    for i in range(len(x_labels)):
        for d in datas_wo:
            if d['timeout']==x_labels[i]:
                line_wo_data.append(d['success']['ratio'])
                line_wo_pos.append(i)
                break
        
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
    
    VIOLIN = True
    
    offset = 0.15
    if VIOLIN:
        v = axs[0].violinplot(box_data,
                positions=[x - offset for x in box_pos],
                widths=0.25,
                showmeans=False,
                showmedians=True,
            )
        add_label(v, "with constraints")
    else:
        axs[0].boxplot(box_data, positions=[x - offset for x in box_pos], label='with constraints',
                patch_artist=True,
                widths=0.25,
                showmeans=False, 
                # showfliers=False,
                medianprops={"color": "white", "linewidth": 0.5},
                boxprops={"facecolor": "C0", "edgecolor": "white", "linewidth": 0.5},
                whiskerprops={"color": "C0", "linewidth": 1.5},
                capprops={"color": "C0", "linewidth": 1.5}
            )
    axs[0].set_ylabel("Metric values")
    axs[0].set_title(problem_name + " seed" + str(seed) + ' metric and success rate (Unsolvable=' + '{:.1f}'.format(unsolvable) + '%)')
    axs[0].tick_params(labelbottom=True)  # <-- Show x labels on top plot
    # axs[0].set_ylim(ymax=90000)
    # axs[0].set_ylim(ymin=20000)
    # axs[0].yaxis.grid(True)
    
    # WO
    if VIOLIN:
        v = axs[0].violinplot(box_wo_data,
                positions=[x + offset for x in box_wo_pos],
                widths=0.25,
                showmeans=False,
                showmedians=True,
            )
        add_label(v, "without constraints")
    else:
        axs[0].boxplot(box_wo_data, positions=[x + offset for x in box_wo_pos], label='without constraints',
                patch_artist=True,
                widths=0.25,
                showmeans=False, 
                # showfliers=False,
                medianprops={"color": "white", "linewidth": 0.5},
                boxprops={"facecolor": "lightcoral", "edgecolor": "white", "linewidth": 0.5},
                whiskerprops={"color": "lightcoral", "linewidth": 1.5},
                capprops={"color": "lightcoral", "linewidth": 1.5}
            )
    if VIOLIN:
        axs[0].legend(*zip(*labels), loc='upper left', ncols=3)
    else:
        axs[0].legend(loc='upper left', ncols=3)
    
    #############################
    
    # WITH
    axs[1].plot(line_pos, line_data, marker='o', label='with constraints')
    axs[1].axhline(y=100-unsolvable, color="black", linestyle="--", label='solvable with constraints')
    axs[1].set(ylim=(0, 110))
    axs[1].set_ylabel("Success ratio (%)")
    axs[1].set_xlabel("Timeout (s)")
    
    # WO
    axs[1].plot(line_wo_pos, line_wo_data, marker='o', label='without constraints')
    # axs[1].axhline(y=100-unsolvable, color="black", linestyle="--")
    # axs[1].set(ylim=(0, 100))
    # axs[1].set_ylabel("Success ratio (%)")
    # axs[1].set_xlabel("Timeout (s)")
    axs[1].legend(loc='upper left', ncols=3)
    
    
    plt.xticks(ticks=x_pos, labels=x_labels)
    
    plt.tight_layout()
    plt.show()
    exit()
    
if __name__=='__main__':
    
    # Example usage
    # folder_dict = get_two_level_folder_dict('results_constraints')
    # print(json.dumps(folder_dict, indent=4))
    # exit()

    # sys.argv += ['50-200-TO5_06-16-2025_10:07:57.json']
    # main_cli()
    
    several()