import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


x_labels = [1, 3, 5, 10, 15, 30]
x_pos = np.arange(len(x_labels)) 

fig, ax = plt.subplots(layout='constrained')

offset = 0.13
widths = 0.25

data_best = [np.nan, 163, 163, 163, 163, 163]
label='best'
positions = [x - offset for x in x_pos]
# ax.boxplot(data_best, positions=positions, label=label, widths=widths)
# ax.scatter(positions, data_best, label=label)
ax.bar(positions, data_best, label=label, width=widths)

data_all = [np.nan, 169, 169, 169, 169, 169]
label='all'
positions = [x + offset for x in x_pos]
# ax.boxplot(data_all, positions=positions, label=label, widths=widths)
# ax.scatter(positions, data_all, label=label)
ax.bar(positions, data_all, label=label, width=widths)

ax.set_title("Metrics with human constraints (rover10)")
ax.set_xlabel("Timeout (s)")
ax.set_ylabel("Metric")

x_padding = 0.5
ax.set_xlim(x_pos[0]-x_padding, x_pos[-1]+x_padding)

ax.legend(loc='upper left')

plt.xticks(ticks=x_pos, labels=x_labels)
plt.tight_layout()
plt.show()

#############

# TO3:    best(AC-CD-ACD)=  163      ABCD=  169
# TO5:    best(AC-CD-ACD)=  163      ABCD=  169
# TO10:   best(AC-CD-ACD)=  163      ABCD=  169
# TO15:   best(AC-CD-ACD)=  163      ABCD=  169
# TO30:   best(AC-CD-ACD)=  163      ABCD=  169
