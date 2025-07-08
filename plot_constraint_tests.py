from pathlib import Path
import json
import sys
import click
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from defs import startWith


def extract_result_with_constraint(filename, show=False):
    print(f'File: {filename}')
    with open(filename, 'r') as f:
        raw_data = json.loads(f.read())
        
    if 'elapsed' not in raw_data:
        raise Exception(f"{filename} was interrupted!")
    
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
            
    compilation_times = np.array([t['compilation_time'] for t in tests]) if 'compilation_time' in tests[0] else np.array([-1])
    planning_times = np.array([t['planning_time'] for t in tests]) if 'planning_time' in tests[0] else np.array([-1])
            
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
    data['compilation'] = {
        'times': compilation_times,
        'mean': compilation_times.mean(),
        'std': compilation_times.std(),
        'min': compilation_times.min(),
        'max': compilation_times.max(),
    }
    data['planning'] = {
        'times': planning_times,
        'mean': planning_times.mean(),
        'std': planning_times.std(),
        'min': planning_times.min(),
        'max': planning_times.max(),
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
        print('Compilation = ' + '{:.1f}'.format(data['compilation']['mean']) + '+-' + '{:.1f} s'.format(data['compilation']['std']))
        print('Planning = ' + '{:.1f}'.format(data['planning']['mean']) + '+-' + '{:.1f} s'.format(data['planning']['std']))
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
        
    if 'elapsed' not in raw_data:
        raise Exception(f"{filename} was interrupted!")
    
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
            
    planning_times = np.array([t['planning_time'] for t in tests]) if 'planning_time' in tests[0] else np.array([-1])
            
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
    data['planning'] = {
        'times': planning_times,
        'mean': planning_times.mean(),
        'std': planning_times.std(),
        'min': planning_times.min(),
        'max': planning_times.max(),
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
        print('Planning = ' + '{:.1f}'.format(data['planning']['mean']) + '+-' + '{:.1f} s'.format(data['planning']['std']))
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
        
    if 'elapsed' not in raw_data:
        raise Exception(f"{filename} was interrupted!")
    
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
            
    compilation_times = [t['compilation_time'] if t['compilation_time']<raw_data['timeout'] else raw_data['timeout'] for t in tests]
    planning_times = [t['planning_time'] for t in tests] if 'planning_time' in tests[0] else [0]
    translation_times = [t['translation_time'] for t in tests] if 'translation_time' in tests[0] else [0]
            
    if successful!=[]:
        metrics = [t['metric'] for t in successful]
        mean = float(np.array(metrics).mean())
        std = float(np.array(metrics).std())
        min_metric = float(np.array(metrics).min())
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
    data['compilation'] = {
        'times': compilation_times,
        'mean': float(np.array(compilation_times).mean()),
        'std': float(np.array(compilation_times).std()),
        'min': float(np.array(compilation_times).min()),
        'max': float(np.array(compilation_times).max()),
    }
    data['planning'] = {
        'times': planning_times,
        'mean': float(np.array(planning_times).mean()),
        'std': float(np.array(planning_times).std()),
        'min': float(np.array(planning_times).min()),
        'max': float(np.array(planning_times).max()),
    }
    data['translation'] = {
        'times': translation_times,
        'mean': float(np.array(translation_times).mean()),
        'std': float(np.array(translation_times).std()),
        'min': float(np.array(translation_times).min()),
        'max': float(np.array(translation_times).max()),
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
        print('Compilation = ' + '{:.1f}'.format(data['compilation']['mean']) + '+-' + '{:.1f} s'.format(data['compilation']['std']))
        print('Planning = ' + '{:.1f}'.format(data['planning']['mean']) + '+-' + '{:.1f} s'.format(data['planning']['std']))
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
        compilation_times = np.array([t['compilation_time'] if t['compilation_time']<timeout else timeout for t in all_data[timeout]['tests']])
        all_data[timeout]['compilation_time_mean'] = float(compilation_times.mean())
        all_data[timeout]['compilation_time_std'] = float(compilation_times.std())
        all_data[timeout]['planning_time_mean'] = float(np.array([t['planning_time'] for t in all_data[timeout]['tests'] if t['reason']!='Unsolvable Problem']).mean())
        all_data[timeout]['planning_time_std'] = float(np.array([t['planning_time'] for t in all_data[timeout]['tests'] if t['reason']!='Unsolvable Problem']).std())
        if all_data[timeout]['successful']!=[]:
            all_data[timeout]['metrics'] = [t['metric'] for t in all_data[timeout]['successful']]
            all_data[timeout]['mean'] = float(np.array(all_data[timeout]['metrics']).mean())
            all_data[timeout]['std'] = float(np.array(all_data[timeout]['metrics']).std())
            all_data[timeout]['min_metric'] = float(np.array(all_data[timeout]['metrics']).min())
        else:
            all_data[timeout]['metrics'] = -1
            all_data[timeout]['mean'] = -1
            all_data[timeout]['std'] = -1
            all_data[timeout]['min_metric'] = -1
            
        all_data[timeout]['elapsed_mean'] = float(np.array(all_data[timeout]['elapsed']).mean())
        all_data[timeout]['elapsed_std'] = float(np.array(all_data[timeout]['elapsed']).std())
    
    # Extract final values
    final_datas = []
    for timeout in all_data:
        N_TESTS = len(all_data[timeout]['tests'])        
        data = {'timeout': timeout}
        data['Repeated'] = 100*all_data[timeout]['repeated']/N_TESTS
        data['compilation_time_mean'] = all_data[timeout]['compilation_time_mean']
        data['compilation_time_std'] = all_data[timeout]['compilation_time_std']
        data['planning_time_mean'] = all_data[timeout]['planning_time_mean']
        data['planning_time_std'] = all_data[timeout]['planning_time_std']
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

def several(problem_name, seed, without_constraints_folder, h_folder, violin):
    
#############################################################
    ## EXTRACT DATA FROM FILES ##
    all_files = get_two_level_folder_dict('results_constraints')
   
    all_files_random = [] # Includes all TO 
    all_files_original = [] # One file per TO
    all_files_H = [] # One file per TO
    for folder in all_files[problem_name]:
        if folder[:len('seed')]=='seed':
            if seed=='all' or folder == seed:
                all_files_random += all_files[problem_name][folder]
        elif folder == without_constraints_folder:
            all_files_original += all_files[problem_name][folder]
        elif folder == h_folder:
            all_files_H += all_files[problem_name][folder]
    
    data_random = extract_all_seeds(all_files_random) 
    data_original = [extract_result_without_constraint(f) for f in all_files_original]
    data_h = [extract_result_h(f) for f in all_files_H]
    
#############################################################
    WITH_RANDOM = True
    
    ## PREPARE PLOT DATA ##
    unsolvable = data_random[-1]['success']['Unsolvable']
    timeout_values = set()
    timeout_values = timeout_values.union(set([int(d['timeout']) for d in data_random]))
    timeout_values = timeout_values.union(set([int(d['timeout']) for d in data_original]))
    timeout_values = timeout_values.union(set([int(d['timeout']) for d in data_h]))
    timeout_values = list(timeout_values)
    timeout_values.sort()
    timeout_values = [t for t in timeout_values if t<=30]
    # timeout_values = [t for t in timeout_values if t>30]
    x_pos = np.arange(len(timeout_values)) 
    
    # With random constraints data
    plot_metric_random_data = []
    plot_metric_random_pos = []
    for i,d in enumerate(data_random):
        if 'metrics' in d:
            for j in range(len(timeout_values)):
                if d['timeout']==timeout_values[j]:
                    plot_metric_random_data.append(d['metrics']['all'])
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
            for j in range(len(timeout_values)):
                if d['timeout']==timeout_values[j]:
                    plot_metric_original_data.append(d['metrics']['all'])
                    plot_metric_original_pos.append(j)
                    break
    if plot_metric_original_data==[]:
        plot_metric_original_data = [np.nan]
    if plot_metric_original_pos==[]:
        plot_metric_original_pos = [np.nan]
            
    # human data
    plot_metric_h_data = []
    plot_metric_all_h_data = []
    plot_metric_h_pos = []
    print('H constraint mins:')
    for i,d in enumerate(data_h):
        if 'metrics' in d:
            print('\tTO' + str(d['timeout']) + ':\tbest=' + str(np.array(d['metrics']['all']).min()) + '\tall=' + str(d['metrics']['all'][-1]))
            for j in range(len(timeout_values)):
                if d['timeout']==timeout_values[j]:
                    plot_metric_h_data.append(d['metrics']['all'])
                    plot_metric_all_h_data.append(d['metrics']['all'][-1])
                    plot_metric_h_pos.append(j)
                    break
    if plot_metric_h_data==[]:
        plot_metric_h_data = [np.nan]
    if plot_metric_h_pos==[]:
        plot_metric_h_pos = [np.nan]
        
    # Relevant info extraction
    # find global min and max
    minimums = []
    minimum_random = float(np.array([np.array(d).min() for d in plot_metric_random_data]).min())
    minimums.append(minimum_random)
    if all_files[problem_name][without_constraints_folder]!=[]:
        minimum_original = float(np.array([np.array(d).min() for d in plot_metric_original_data]).min())
        minimums.append(minimum_original)
    if all_files[problem_name][h_folder]!=[]:
        minimum_h = float(np.array([np.array(d).min() for d in plot_metric_h_data]).min())
        minimums.append(minimum_h)
    minimum = min(minimums)
    
    maximums = []
    maximum_random = float(np.array([np.array(d).max() for d in plot_metric_random_data]).max())
    maximums.append(maximum_random)
    if all_files[problem_name][without_constraints_folder]!=[]:
        maximum_original = float(np.array([np.array(d).max() for d in plot_metric_original_data]).max())
        maximums.append(maximum_original)
    if all_files[problem_name][h_folder]!=[]:
        maximum_h = float(np.array([np.array(d).max() for d in plot_metric_h_data]).max())
        maximums.append(maximum_h)
    maximum = max(maximums)
    print("Best plan metric: ", minimum)
    print("Worst plan metric: ", maximum)
    
    # Success ratio data random
    plot_success_random_data = []
    plot_success_random_pos = []
    for i in range(len(timeout_values)):
        for d in data_random:
            if d['timeout']==timeout_values[i]:
                plot_success_random_data.append(d['success']['ratio'])
                plot_success_random_pos.append(i)
                break
    
    # Success ratio data original
    plot_success_original_data = []
    plot_success_original_pos = []
    for i in range(len(timeout_values)):
        for d in data_original:
            if d['timeout']==timeout_values[i]:
                plot_success_original_data.append(d['success']['ratio'])
                plot_success_original_pos.append(i)
                break
    
    # Success ratio data h
    plot_success_h_data = []
    plot_success_h_pos = []
    for i in range(len(timeout_values)):
        for d in data_h:
            if d['timeout']==timeout_values[i]:
                plot_success_h_data.append(d['success']['ratio'])
                plot_success_h_pos.append(i)
                break
            
    # Durations
    durations = {
        'original':{
            'pos': [],
            'Planning': {'mean':[], 'std':[]},
        },
        'random':{
            'pos': [],
            'Compilation': {'mean':[], 'std':[]},
            'Planning': {'mean':[], 'std':[]},
        },
        'human':{
            'pos': [],
            'Translation': {'mean':[], 'std':[]},
            'Compilation': {'mean':[], 'std':[]},
            'Planning': {'mean':[], 'std':[]},
        },
    }
    for i in range(len(timeout_values)):
        for d in data_original:
            if d['timeout']==timeout_values[i]:
                durations['original']['pos'].append(i)
                durations['original']['Planning']['mean'].append(d['planning']['mean'])
                durations['original']['Planning']['std'].append(d['planning']['std'])
                break
        for d in data_random:
            if d['timeout']==timeout_values[i]:
                durations['random']['pos'].append(i)
                durations['random']['Compilation']['mean'].append(d['compilation_time_mean'])
                durations['random']['Compilation']['std'].append(d['compilation_time_std'])
                durations['random']['Planning']['mean'].append(d['planning_time_mean'])
                durations['random']['Planning']['std'].append(d['planning_time_std'])
                break
        for d in data_h:
            if d['timeout']==timeout_values[i]:
                durations['human']['pos'].append(i)
                durations['human']['Translation']['mean'].append(d['translation']['mean'])
                durations['human']['Translation']['std'].append(d['translation']['std'])
                durations['human']['Compilation']['mean'].append(d['compilation']['mean'])
                durations['human']['Compilation']['std'].append(d['compilation']['std'])
                durations['human']['Planning']['mean'].append(d['planning']['mean'])
                durations['human']['Planning']['std'].append(d['planning']['std'])
                break

#############################################################
    ###################### FIGURE PLOTS #####################
    #########################################################
    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(15, 13))
    
    ## Colors
    original_problem_color = "#f08080ff"
    random_constraints_color = "#1f76b4ff"
    random_constraints_dark_color = "#275d84ff"
    human_constraints_color = "#32cd32ff"
    human_constraints_dark_color = "#36a336ff"
    human_constraints_trans_color = "#a2ff16ff"
    
    
    ##########################################################
    ######################### Metrics ########################
    ##########################################################
    
    showfliers = False
    # offset > widths
    widths = 0.25
    multiplier = -1.0 if WITH_RANDOM else -0.5
    
    # ORIGINAL
    data = plot_metric_original_data
    offset = (widths+0.02)*multiplier
    multiplier+=1
    positions = [x + offset for x in plot_metric_original_pos]
    label = 'original problem'
    if violin:
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
                boxprops={"facecolor": original_problem_color, "edgecolor": "white", "linewidth": 0.5},
                whiskerprops={"color": original_problem_color, "linewidth": 1.5},
                capprops={"color": original_problem_color, "linewidth": 1.5}
            )
    # RANDOM
    if WITH_RANDOM:
        data = plot_metric_random_data
        offset = (widths+0.02)*multiplier
        multiplier+=1
        positions = [x + offset for x in plot_metric_random_pos]
        label = 'random constraints'
        if violin:
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
                    boxprops={"facecolor": random_constraints_color, "edgecolor": "white", "linewidth": 0.5},
                    whiskerprops={"color": random_constraints_color, "linewidth": 1.5},
                    capprops={"color": random_constraints_color, "linewidth": 1.5}
                )
    # H
    data = plot_metric_h_data
    offset = (widths+0.02)*multiplier
    multiplier+=1
    positions = [x + offset for x in plot_metric_h_pos]
    label = 'human constraints'
    if violin:
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
                boxprops={"facecolor": human_constraints_color, "edgecolor": "white", "linewidth": 0.5},
                whiskerprops={"color": human_constraints_color, "linewidth": 1.5},
                capprops={"color": human_constraints_color, "linewidth": 1.5},
                zorder=0
            )
    axs[0].scatter(positions, plot_metric_all_h_data, s=70, c='black', label='All H constraints', marker='+', zorder=10)
    
    # PARAMS
    axs[0].set_ylabel("Metric values")
    axs[0].set_xlabel("Timeout (s)")
    seeds = data_random[-1]['seeds']
    axs[0].set_title(problem_name + f"\nseeds: {seeds}")
    axs[0].tick_params(labelbottom=True)  # <-- Show x labels on top plot
    # axs[0].set_ylim(ymin=10290.0 * 0.9)
    # axs[0].set_ylim(ymax=127454.0 * 1.1)
    # axs[0].yaxis.grid(True)
    if violin:
        axs[0].legend(*zip(*labels), loc='upper left', ncols=4)
    else:
        axs[0].legend(loc='upper left', ncols=4)
    # axs[0].axhline(y=7236, color="green", linestyle="--")
        
    
    ##########################################################
    ##################### Success Ratio ######################
    ##########################################################
    
    # ORIGINAL
    axs[1].plot(plot_success_original_pos, plot_success_original_data, marker='o', color=original_problem_color, label='original problem')
    # RANDOM
    if WITH_RANDOM:
        axs[1].plot(plot_success_random_pos, plot_success_random_data, marker='o', color=random_constraints_color, label='random constraints')
    # H
    axs[1].plot(plot_success_h_pos, plot_success_h_data, marker='o', color=human_constraints_color, label='h constraints')
    # Params
    axs[1].axhline(y=100, color="green", linestyle="--")
    axs[1].axhline(y=100-unsolvable, color="black", linestyle=":", label=f'solvable random constraints ({100-unsolvable:.1f}%)')
    axs[1].set(ylim=(0, 110))
    axs[1].set_ylabel("Success ratio (%)")
    axs[1].set_xlabel("Timeout (s)")
    axs[1].legend(loc='upper left', ncols=4)
    axs[1].tick_params(labelbottom=True)  # <-- Show x labels on top plot
    
    # ##########################################################
    # ############# Compilation + Planning Times ###############
    # ##########################################################

    durations_styles = {
        'original':{
            'Planning': {'color': original_problem_color, 'hatch': '', 'label_color':"#000000FF"},
        },
        'random':{
            'Compilation': {'color': random_constraints_dark_color, 'hatch': '', 'label_color':"#000000FF"},
            'Planning': {'color': random_constraints_color, 'hatch': '', 'label_color':"#000000FF"},
        },
        'human':{
            'Translation': {'color': human_constraints_trans_color, 'hatch': '', 'label_color':"#000000FF"},
            'Compilation': {'color': human_constraints_dark_color, 'hatch': '', 'label_color':"#000000FF"},
            'Planning': {'color': human_constraints_color, 'hatch': '', 'label_color':"#000000FF"},
        },
    }

    width = 0.25
    multiplier = -1.0 if WITH_RANDOM else -0.5
    for run_type, durs in durations.items():
        if not WITH_RANDOM and run_type=='random':
            continue
        bottom = np.zeros(len(durs['pos']))
        offset = width * multiplier
        for duration_type, duration in durs.items():
            if duration_type=='pos':
                continue
            p = axs[2].bar(np.array(durs['pos'])+offset, duration['mean'], width, label=run_type+' '+duration_type, bottom=bottom,
                       yerr=duration['std'],
                       color=durations_styles[run_type][duration_type]['color'],
                       hatch=durations_styles[run_type][duration_type]['hatch'])
            bottom += duration['mean']
            axs[2].bar_label(p, fmt=duration_type[:1]+':{:.1f}', label_type='center', color=durations_styles[run_type][duration_type]['label_color'])
        multiplier+=1
            
    axs[2].legend(loc='upper left')
    axs[2].set_ylabel("Time (s)")
    axs[2].set_xlabel("Timeout (s)")
    
    ##########################################################

    
    plt.xticks(ticks=x_pos, labels=timeout_values)
    x_padding = 0.5
    plt.xlim(x_pos[0]-x_padding, x_pos[-1]+x_padding)
    
    plt.tight_layout()
    plt.show()
    exit()

##################
### MAIN + CLI ###
##################
@click.group()
def cli():
    pass

PROBLEM_NAMES = [x.name for x in Path('results_constraints').iterdir() if x.is_dir()]
PROBLEM_NAMES.sort()
@cli.command(help=f'Plot all results of a problem. {PROBLEM_NAMES}')
@click.argument('problem_name')
@click.option('--seed', 'seed', default='all')
@click.option('--wofolder', 'without_constraints_folder', default='WO')
@click.option('--hfolder', 'h_folder', default='H')
@click.option('--violin', 'violin', is_flag=True, default=False)
def several_command(problem_name, seed, without_constraints_folder, h_folder, violin):
    if problem_name not in PROBLEM_NAMES:
        click.echo('Unknown problem.\nSupported problems: ' + str(PROBLEM_NAMES))
        exit()
        
    SEEDS = ['all'] + [x.name for x in Path(Path('results_constraints'), problem_name).iterdir() if (x.is_dir() and startWith(x.name, 'seed'))]
    if seed not in SEEDS:
        click.echo('Unknown seed.\nSupported seeds: ' + str(SEEDS))
        exit()
        
    several(problem_name, seed, without_constraints_folder, h_folder, violin)
    
@cli.command(help='Plot results for a specific file with random constraints')
@click.argument('filename')
def with_command(filename: str):
    click.echo("WIP: for now no plot")
    extract_result_with_constraint(filename)
    
@cli.command(help='Plot results for a specific file with original problem')
@click.argument('filename')
def without_command(filename: str):
    click.echo("WIP: for now no plot")
    extract_result_without_constraint(filename)
    
@cli.command(help='Plot results for a specific file with human constraints')
@click.argument('filename')
def H_command(filename: str):
    click.echo("WIP: for now no plot")
    extract_result_h(filename)
    
if __name__=='__main__':
    cli()
    ## Below for debugging ##
    # several('zenotravel13', 'all', 'WO', 'H', False)