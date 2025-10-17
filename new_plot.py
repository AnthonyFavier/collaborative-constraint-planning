

from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import numpy as np

import json

# filename_milp = 'dump_results_counters_milp.json'
# filename_up = 'dump_results_counters_up.json'

# filename_milp = 'dump_results_rover_milp.json'
# filename_up = 'dump_results_rover_up.json'

filename_milp = 'dump_results_zenotravel_milp.json'
filename_up = 'dump_results_zenotravel_up.json'

pairs_filenames = (
    ('dump_results_counters_milp.json', 'dump_results_counters_up.json'),
    ('dump_results_rover_milp.json', 'dump_results_rover_up.json'),
    ('dump_results_zenotravel_milp.json', 'dump_results_zenotravel_up.json'),
)

fig, axes = plt.subplots(1, len(pairs_filenames), layout='constrained')

for i, (filename_milp, filename_up) in enumerate(pairs_filenames):

    with open(filename_milp, 'r') as f:
        data_milp = json.load(f)
    with open(filename_up, 'r') as f:
        data_up = json.load(f)

    t_start_milp = data_milp['time_start']
    n_solved_milp = 0
    cumul_milp = [(0.0, n_solved_milp)]
    for k,r in data_milp['results'].items():
        r = r['MILP']
        t = r['time_solved']-t_start_milp
        n_solved_milp+=1
        cumul_milp.append((t, n_solved_milp))
        

    t_start_up = data_up['time_start']
    n_solved_up = 0
    cumul_up = [(0.0, n_solved_up)]
    for k,r in data_up['results'].items():
        r = r['UP']
        t = r['time_solved']-t_start_up
        n_solved_up+=1
        cumul_up.append((t, n_solved_up))

    # t_max = max( cumul_milp[-1][0], cumul_up[-1][0] )*1.1
    t_max = 300
    cumul_milp.append((t_max, n_solved_milp))
    cumul_up.append((t_max, n_solved_up))

    axes[i].step([x[0] for x in cumul_milp], [y[1] for y in cumul_milp], where='post', label='MILP')
    axes[i].step([x[0] for x in cumul_up], [y[1] for y in cumul_up], where='post', label='UP')

    axes[i].legend(loc='upper left', ncols=3)

    axes[i].set_xlabel('Time (s)')
    axes[i].set_ylabel('Nb Pb Solved')

    axes[i].set_title("Cumulative " + data_milp['domain_name'])

plt.show()


exit()

##########################

categories = ('Loading', 'Solving', 'Total')
x = np.arange(len(categories))  # the label locations

fig, ax = plt.subplots(layout='constrained')
width = 0.4

for i, c in enumerate(categories):
    pvalue = mannwhitneyu(times['UP'][c], times['MILP'][c], alternative='greater')[1]
    if pvalue<0.001:
        significant = '***'
    elif pvalue<0.01:
        significant = '**'
    elif pvalue<0.05:
        significant = '*'
    else:
        significant = 'ns'
    print(f'{c}: {pvalue:.5f} {significant}')

    x_m = i
    x1 = x_m-width/2
    x2 = x_m+width/2

    y = max(np.average(times['UP'][c])+np.std(times['UP'][c]), 
            np.average(times['MILP'][c])+np.std(times['MILP'][c]) )+2
    h = 0.5
    plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, color='k')
    ax.text((x1+x2)*.5, y+h, significant, ha='center', va='bottom', color='k')

data = {
    'UP': ([round(np.average(times['UP'][c]),2) for c in categories], [np.std(times['UP'][c]) for c in categories]),
    'MILP': ([round(np.average(times['MILP'][c]),2) for c in categories], [np.std(times['MILP'][c]) for c in categories]),
}

multiplier = -0.5
for attr, (values, std) in data.items() :
    offset = width * multiplier
    rects = ax.bar(x+offset, values, width, yerr=std, label=attr)
    ax.bar_label(rects, padding=3)
    multiplier += 1

ax.set_ylabel('Time (s)')

ax.set_xticks(x, categories)
ax.legend(loc='upper left', ncols=3)

# x = 3
# x1 = x-width/2
# x2 = x+width/2
# y = 22
# h = 0.5
# plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, color='k')
# ax.text((x1+x2)*.5, y+h, "ns", ha='center', va='bottom', color='k')

ax.set_ylim(0, 25)
plt.show()


# statannot.add_stat_annotation(
#     ax,
#     data=data,
#     x='categories',
#     y='time',
#     order=categories
#     box_pairs=[
#         (("Biscoe", "Male"), ("Torgersen", "Female")),
#         (("Dream", "Male"), ("Dream", "Female")),
#     ],
#     test="Mann-Whitney-gt",
#     text_format="star",
#     # loc="outside",
# )