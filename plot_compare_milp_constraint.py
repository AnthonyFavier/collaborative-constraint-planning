

txt_with = """
┌─────────────────────────┐
│ Loading problem: 8.64s  │
│ Building model: 1.56s   │
│ Solving instance: 4.82s │
│ Total time: 15.54s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.58s  │
│ Building model: 1.45s   │
│ Solving instance: 4.52s │
│ Total time: 15.05s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.51s  │
│ Building model: 1.51s   │
│ Solving instance: 5.60s │
│ Total time: 17.16s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.88s  │
│ Building model: 1.47s   │
│ Solving instance: 4.73s │
│ Total time: 15.60s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.94s  │
│ Building model: 1.52s   │
│ Solving instance: 4.70s │
│ Total time: 15.66s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.17s  │
│ Building model: 1.59s   │
│ Solving instance: 4.27s │
│ Total time: 15.56s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.42s  │
│ Building model: 1.52s   │
│ Solving instance: 4.47s │
│ Total time: 15.92s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.35s  │
│ Building model: 1.49s   │
│ Solving instance: 4.48s │
│ Total time: 15.85s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.95s  │
│ Building model: 1.59s   │
│ Solving instance: 5.29s │
│ Total time: 16.34s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.81s  │
│ Building model: 1.46s   │
│ Solving instance: 4.89s │
│ Total time: 15.67s      │
└─────────────────────────┘
"""

txt_without = """
┌─────────────────────────┐
│ Loading problem: 8.64s  │
│ Building model: 1.43s   │
│ Solving instance: 6.73s │
│ Total time: 17.31s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.06s  │
│ Building model: 1.52s   │
│ Solving instance: 6.25s │
│ Total time: 17.36s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.68s  │
│ Building model: 1.57s   │
│ Solving instance: 9.18s │
│ Total time: 20.99s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.96s  │
│ Building model: 1.47s   │
│ Solving instance: 7.80s │
│ Total time: 18.74s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.15s  │
│ Building model: 1.53s   │
│ Solving instance: 6.06s │
│ Total time: 17.28s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.72s  │
│ Building model: 1.46s   │
│ Solving instance: 6.69s │
│ Total time: 17.39s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.00s  │
│ Building model: 1.45s   │
│ Solving instance: 5.42s │
│ Total time: 16.38s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.17s  │
│ Building model: 1.47s   │
│ Solving instance: 7.36s │
│ Total time: 18.50s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 9.48s  │
│ Building model: 1.51s   │
│ Solving instance: 6.36s │
│ Total time: 17.87s      │
└─────────────────────────┘
┌─────────────────────────┐
│ Loading problem: 8.94s  │
│ Building model: 1.65s   │
│ Solving instance: 7.53s │
│ Total time: 18.62s      │
└─────────────────────────┘
"""

times = {
    'with': {'Loading':[], 'Building':[], 'Solving':[], 'Total':[]},
    'without': {'Loading':[], 'Building':[], 'Solving':[], 'Total':[]},
}

for l in txt_with.splitlines():
    if ':' not in l:
        continue

    t = float(l.split(':')[1].split('s')[0].strip())
    if 'Loading' in l:
        times['with']['Loading'].append(t)
    elif 'Building' in l:
        times['with']['Building'].append(t)
    elif 'Solving' in l:
        times['with']['Solving'].append(t)
    elif 'Total' in l:
        times['with']['Total'].append(t)
for l in txt_without.splitlines():
    if ':' not in l:
        continue

    t = float(l.split(':')[1].split('s')[0].strip())
    if 'Loading' in l:
        times['without']['Loading'].append(t)
    elif 'Building' in l:
        times['without']['Building'].append(t)
    elif 'Solving' in l:
        times['without']['Solving'].append(t)
    elif 'Total' in l:
        times['without']['Total'].append(t)


categories = ('Loading', 'Building', 'Solving', 'Total')

from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt
import numpy as np

x = np.arange(len(categories))  # the label locations

fig, ax = plt.subplots(layout='constrained')
width = 0.4

for i, c in enumerate(categories):
    pvalue = mannwhitneyu(times['without'][c], times['with'][c], alternative='greater')[1]
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

    y = max(np.average(times['without'][c])+np.std(times['without'][c]), 
            np.average(times['with'][c])+np.std(times['with'][c]) )+2
    h = 0.5
    plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, color='k')
    ax.text((x1+x2)*.5, y+h, significant, ha='center', va='bottom', color='k')

color_without = 'red'
color_with = 'green'

data = {
    'Without': ([round(np.average(times['without'][c]),2) for c in categories], [np.std(times['without'][c]) for c in categories]),
    'With': ([round(np.average(times['with'][c]),2) for c in categories], [np.std(times['with'][c]) for c in categories]),
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