from pathlib import Path
import json
import sys
import click
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

@click.command()
@click.argument('mode', default='several')
@click.argument('filename', nargs=-1)
def main_cli(mode: str, filename: tuple[str,...]):
    if mode=='several':
        several()
    elif mode=='analyze_with':
        extract_result_with_constraint(filename[0])
    elif mode=='analyze_without':
        extract_result_without_constraint(filename[0])
    
def extract_result_with_constraint(filename, show=False):
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
    data['seeds'] = [raw_data['seed']]
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
    if show:
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

def extract_result_without_constraint(filename, show=False):
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
    if show:
        print('Success = ' + '{:.1f}'.format(data['success']['ratio']) + '%')
        print('\tTimeout = ' + '{:.1f}'.format(data['success']['Timeout']) + ' %')
        print('\tUnsolvable = ' + '{:.1f}'.format(data['success']['Unsolvable']) + '%')
        if successful!=[]:
            print('Metric = ' + '{:.1f}'.format(data['metrics']['mean']) + '+-' + '{:.1f}'.format(data['metrics']['std']))
            print('Best = ' + '{:.1f}'.format(data['metrics']['best']))
        print('Elasped = ' + data['elapsed'])
    
    return data

def extract_result_h(filename, show=False):
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
    ands = []
    for t in tests:
        if t['result']=='success':
            successful.append(t)
        elif t['reason']=='Timeout':
            timeout.append(t)
        elif t['reason']=='Unsolvable Problem':
            unsolvable.append(t)
            
        if t['constraint_type']=="SIMPLE":
            simple.append(t)
        elif t['constraint_type']=="AND":
            ands.append(t)
            
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
    data['seeds'] = [raw_data['seed']]
    data['timeout'] = raw_data['timeout']
    data['Repeated'] = 100*repeated/len(tests)
    data['Type_repartition'] = {
        'SIMPLE': 100*len(simple)/len(tests),
        'AND': 100*len(ands)/len(tests),
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
    if show:
        print("Repeated = " + '{:.1f}'.format(data['Repeated']) + '%')
        print('Constraint types:')
        print('\tSIMPLE: ' + '{:.1f}'.format(data['Type_repartition']['SIMPLE']) + '%')
        print('\tAND: ' + '{:.1f}'.format(data['Type_repartition']['AND']) + '%')
        print('Success = ' + '{:.1f}'.format(data['success']['ratio']) + '%')
        print('\tTimeout = ' + '{:.1f}'.format(data['success']['Timeout']) + ' %')
        print('\tUnsolvable = ' + '{:.1f}'.format(data['success']['Unsolvable']) + '%')
        if successful!=[]:
            print('Metric = ' + '{:.1f}'.format(data['metrics']['mean']) + '+-' + '{:.1f}'.format(data['metrics']['std']))
            print('Best = ' + '{:.1f}'.format(data['metrics']['best']))
        print('Elasped = ' + data['elapsed'])
    
    return data

def extract_all_seeds(filenames, show=False):
    
    all_data = {}
    
    # Extract data from all files, sorted by timeout
    for filename in filenames:
        print(f'File: {filename}')
        with open(filename, 'r') as f:
            raw_data = json.loads(f.read())
            
        if 'elapsed' not in raw_data:
            raise Exception(f"{filename} was interrupted!")
            
        timeout = raw_data['timeout']
        if timeout not in all_data:
            all_data[timeout] = {
                'tests': [],
                'successful': [],
                'reason_timeout': [],
                'reason_unsolvable': [],
                'elapsed': [],
                'repeated': 0,
                'seeds': [],
            }
            
        seed = raw_data['seed']
        if seed not in all_data[timeout]['seeds']:
            all_data[timeout]['seeds'].append(seed)
            
        # Check if not already in all_data[timeout] tests
        for t in raw_data['tests']:
            constraints_already_present = [t['constraint'] for t in all_data[timeout]['tests']]
            if t['constraint'] not in constraints_already_present:
                all_data[timeout]['tests'].append(t)
                if t['result']=='success':
                    all_data[timeout]['successful'].append(t)
                elif t['reason']=='Timeout':
                    all_data[timeout]['reason_timeout'].append(t)
                elif t['reason']=='Unsolvable Problem':
                    all_data[timeout]['reason_unsolvable'].append(t)
            else:
                all_data[timeout]['repeated']+=1
        
        h,m,s = [int(x) for x in raw_data['elapsed'].split(':')]
        elapsed_seconds = h*3600 + m*60 + s
        all_data[timeout]['elapsed'].append(elapsed_seconds)
                
    # for each timeout value, compute values
    for timeout in all_data:
        if all_data[timeout]['successful']!=[]:
            all_data[timeout]['metrics'] = np.array([t['metric'] for t in all_data[timeout]['successful']])
            all_data[timeout]['mean'] = all_data[timeout]['metrics'].mean()
            all_data[timeout]['std'] = all_data[timeout]['metrics'].std()
            all_data[timeout]['min_metric'] = all_data[timeout]['metrics'].min()
        else:
            all_data[timeout]['metrics'] = -1
            all_data[timeout]['mean'] = -1
            all_data[timeout]['std'] = -1
            all_data[timeout]['min_metric'] = -1
            
        all_data[timeout]['elapsed_mean'] = np.array(all_data[timeout]['elapsed']).mean()
        all_data[timeout]['elapsed_std'] = np.array(all_data[timeout]['elapsed']).std()
    
    # Extract final values
    final_datas = []
    for timeout in all_data:
        N_TESTS = len(all_data[timeout]['tests'])        
        data = {'timeout': timeout}
        data['Repeated'] = 100*all_data[timeout]['repeated']/N_TESTS
        data['success'] = {
                'ratio': 100*len(all_data[timeout]['successful'])/N_TESTS,
                'Timeout': 100*len(all_data[timeout]['reason_timeout'])/N_TESTS,
                'Unsolvable': 100*len(all_data[timeout]['reason_unsolvable'])/N_TESTS,
        }
        if all_data[timeout]['successful']!=[]:
            data['metrics'] = {
                'all': all_data[timeout]['metrics'],
                'mean': all_data[timeout]['mean'],
                'std': all_data[timeout]['std'],
                'best': all_data[timeout]['min_metric']
            }
        data['elapsed_mean'] = all_data[timeout]['elapsed_mean']
        data['elapsed_std'] = all_data[timeout]['elapsed_std']
        data['seeds'] = all_data[timeout]['seeds']
        
        final_datas.append(data)
        
        # PRINT
        if show:
            print(f'\nTimeout = ' + str(data['timeout']))
            print("Repeated = " + '{:.1f}'.format(data['Repeated']) + '%')
            print('Success = ' + '{:.1f}'.format(data['success']['ratio']) + '%')
            print('\tTimeout = ' + '{:.1f}'.format(data['success']['Timeout']) + ' %')
            print('\tUnsolvable = ' + '{:.1f}'.format(data['success']['Unsolvable']) + '%')
            if all_data[timeout]['successful']!=[]:
                print('Metric = ' + '{:.1f}'.format(data['metrics']['mean']) + '+-' + '{:.1f}'.format(data['metrics']['std']))
                print('Best = ' + '{:.1f}'.format(data['metrics']['best']))
            print('Elasped mean = ' + '{:.1f}'.format(data['elapsed_mean']))
            print('Elasped std = ' + '{:.1f}'.format(data['elapsed_std']))
    
    return final_datas

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
    
    problem_name = 'zenotravel13' # 'zenotravel13', 'rover13', 'rover8_n'
    with_constraints_folder = 'seed0' # 'seed0', 'seed2902480765646109827', 'seed6671597656599831408'
    without_constraints_folder = 'WO10' # 'WO10'
    h_folder = 'H'
    
    VIOLIN = True
    
#############################################################
    ## EXTRACT DATA FROM FILES ##
    all_files = get_two_level_folder_dict('results_constraints')
    
    all_with_files = all_files[problem_name]['seed0']+all_files[problem_name]['seed2902480765646109827']+all_files[problem_name]['seed6671597656599831408']
    data_random_all_seeds = extract_all_seeds(all_with_files)
    
    data_random = []
    for f in all_files[problem_name][with_constraints_folder]:
        data_random.append(extract_result_with_constraint(f))
    
    data_original = []
    for f in all_files[problem_name][without_constraints_folder]:
        data_original.append(extract_result_without_constraint(f))
        
    data_h = []
    for f in all_files[problem_name][h_folder]:
        data_h.append(extract_result_h(f))
    
    
#############################################################
    ## PREPARE PLOT DATA ##
    unsolvable = data_random_all_seeds[-1]['success']['Unsolvable']
    # x_labels = [int(d['timeout']) for d in data_random_all_seeds].sort() # Might be missing some...
    x_labels = [1, 3, 5, 10, 15, 30]
    x_pos = np.arange(len(x_labels)) 
    
    # With random constraints data
    plot_metric_random_data = []
    plot_metric_random_pos = []
    for i,d in enumerate(data_random_all_seeds):
        if 'metrics' in d:
            plot_metric_random_data.append(d['metrics']['all'])
            for j in range(len(x_labels)):
                if d['timeout']==x_labels[j]:
                    plot_metric_random_pos.append(j)
                    break
    if plot_metric_random_data==[]:
        plot_metric_random_data = [np.nan]
    if plot_metric_random_pos==[]:
        plot_metric_random_pos = [np.nan]
            
    # original problem data
    plot_metric_original_data = []
    plot_metric_original_pos = []
    for i,d in enumerate(data_original):
        if 'metrics' in d:
            plot_metric_original_data.append(d['metrics']['all'])
            for j in range(len(x_labels)):
                if d['timeout']==x_labels[j]:
                    plot_metric_original_pos.append(j)
                    break
    if plot_metric_original_data==[]:
        plot_metric_original_data = [np.nan]
    if plot_metric_original_pos==[]:
        plot_metric_original_pos = [np.nan]
            
    # human data
    plot_metric_h_data = []
    plot_metric_h_pos = []
    for i,d in enumerate(data_h):
        if 'metrics' in d:
            plot_metric_h_data.append(d['metrics']['all'])
            for j in range(len(x_labels)):
                if d['timeout']==x_labels[j]:
                    plot_metric_h_pos.append(j)
                    break
    if plot_metric_h_data==[]:
        plot_metric_h_data = [np.nan]
    if plot_metric_h_pos==[]:
        plot_metric_h_pos = [np.nan]
        
    # Relevant info extraction
    # find global min and max
    minimum_random = float(np.array([d.min() for d in plot_metric_random_data]).min())
    minimum_original = float(np.array([d.min() for d in plot_metric_original_data]).min())
    minimum_h = float(np.array([d.min() for d in plot_metric_h_data]).min())
    minimum = min(minimum_random, minimum_original, minimum_h)
    maximum_random = float(np.array([d.max() for d in plot_metric_random_data]).max())
    maximum_original = float(np.array([d.max() for d in plot_metric_original_data]).max())
    maximum_h = float(np.array([d.max() for d in plot_metric_h_data]).max())
    maximum = max(maximum_random, maximum_original, maximum_h)
    print("Best plan metric: ", minimum)
    print("Worst plan metric: ", maximum)
    
    # Success ratio data random
    plot_success_random_data = []
    plot_success_random_pos = []
    for i in range(len(x_labels)):
        for d in data_random:
            if d['timeout']==x_labels[i]:
                plot_success_random_data.append(d['success']['ratio'])
                plot_success_random_pos.append(i)
                break
    
    # Success ratio data original
    plot_success_original_data = []
    plot_success_original_pos = []
    for i in range(len(x_labels)):
        for d in data_original:
            if d['timeout']==x_labels[i]:
                plot_success_original_data.append(d['success']['ratio'])
                plot_success_original_pos.append(i)
                break
    
    # Success ratio data h
    plot_success_h_data = []
    plot_success_h_pos = []
    for i in range(len(x_labels)):
        for d in data_h:
            if d['timeout']==x_labels[i]:
                plot_success_h_data.append(d['success']['ratio'])
                plot_success_h_pos.append(i)
                break
    
#############################################################
    ## FIGURE PLOTS ##
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
    
    showfliers = False
    # offset > widths
    offset = 0.27
    widths = 0.25
    
    # ORIGINAL
    data = plot_metric_original_data
    positions = [x - offset for x in plot_metric_original_pos]
    label = 'original problem'
    if VIOLIN:
        v = axs[0].violinplot(data,
                positions=positions,
                widths=widths,
                showmeans=False,
                showmedians=True,
            )
        add_label(v, label)
    else:
        axs[0].boxplot(data, positions=positions, label=label,
                patch_artist=True,
                widths=widths,
                showmeans=False, 
                showfliers=showfliers,
                medianprops={"color": "white", "linewidth": 0.5},
                boxprops={"facecolor": "limegreen", "edgecolor": "white", "linewidth": 0.5},
                whiskerprops={"color": "limegreen", "linewidth": 1.5},
                capprops={"color": "limegreen", "linewidth": 1.5}
            )
    # RANDOM
    data = plot_metric_random_data
    positions = [x for x in plot_metric_random_pos]
    label = 'random constraints'
    if VIOLIN:
        v = axs[0].violinplot(data,
                positions=positions,
                widths=widths,
                showmeans=False,
                showmedians=True,
            )
        add_label(v, label)
    else:
        axs[0].boxplot(data, positions=positions, label=label,
                patch_artist=True,
                widths=widths,
                showmeans=False, 
                showfliers=showfliers,
                medianprops={"color": "white", "linewidth": 0.5},
                boxprops={"facecolor": "C0", "edgecolor": "white", "linewidth": 0.5},
                whiskerprops={"color": "C0", "linewidth": 1.5},
                capprops={"color": "C0", "linewidth": 1.5}
            )
    # H
    data = plot_metric_h_data
    positions = [x + offset for x in plot_metric_h_pos]
    label = 'human constraints'
    if VIOLIN:
        v = axs[0].violinplot(data,
                positions=positions,
                widths=widths,
                showmeans=False,
                showmedians=True,
            )
        add_label(v, label)
    else:
        axs[0].boxplot(data, positions=positions, label=label,
                patch_artist=True,
                widths=widths,
                showmeans=False, 
                showfliers=showfliers,
                medianprops={"color": "white", "linewidth": 0.5},
                boxprops={"facecolor": "lightcoral", "edgecolor": "white", "linewidth": 0.5},
                whiskerprops={"color": "lightcoral", "linewidth": 1.5},
                capprops={"color": "lightcoral", "linewidth": 1.5}
            )
    # PARAMS
    axs[0].set_ylabel("Metric values")
    seeds = data_random_all_seeds[-1]['seeds']
    axs[0].set_title(problem_name + f"\nseeds: {seeds}")
    axs[0].tick_params(labelbottom=True)  # <-- Show x labels on top plot
    # axs[0].set_ylim(ymin=10290.0 * 0.9)
    # axs[0].set_ylim(ymax=127454.0 * 1.1)
    # axs[0].yaxis.grid(True)
    if VIOLIN:
        axs[0].legend(*zip(*labels), loc='upper left', ncols=3)
    else:
        axs[0].legend(loc='upper left', ncols=3)
    
    ##########################################################
    
    # ORIGINAL
    axs[1].plot(plot_success_original_pos, plot_success_original_data, marker='o', label='original problem')
    # RANDOM
    axs[1].plot(plot_success_random_pos, plot_success_random_data, marker='o', label='random constraints')
    # H
    axs[1].plot(plot_success_h_pos, plot_success_h_data, marker='o', label='h constraints')
    # Params
    axs[1].axhline(y=100, color="green", linestyle="--")
    axs[1].axhline(y=100-unsolvable, color="black", linestyle=":", label=f'solvable random constraints ({100-unsolvable:.1f}%)')
    axs[1].set(ylim=(0, 110))
    axs[1].set_ylabel("Success ratio (%)")
    axs[1].set_xlabel("Timeout (s)")
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
    main_cli()
    
    # several()