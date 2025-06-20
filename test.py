import matplotlib.pyplot as plt
import numpy as np


# x = [1, 3, 5, 10, 15, 30]
x = [1, 2, 0, 4, 5]
y = [2, 4, 5, 6, 7]

############################

x_labels = [1, 3, 5, 10, 15, 30]
x_pos = np.arange(len(x_labels)) 


# Success ratio data
# line_data = []
# line_pos = []
# for d in datas:
#     # line_data.append(d['success']['ratio'])
#     for j in range(len(x_labels)):
#         if d['timeout']==x_labels[j]:
#             # line_pos.append(j)
#             line_data.append( (d['success']['ratio'], j) )
#             break
    
fig, axs = plt.subplots(2, 1, sharex=True, figsize=(15, 10))

axs[1].plot(x, y, marker='o')
# axs[1].set(ylim=(0, 100))
axs[1].set_ylabel("Success ratio (%)")
axs[1].set_xlabel("Timeout (s)")

axs[0].boxplot([np.nan], positions=[np.nan], label='without constraints',
               patch_artist=True,
               widths=0.25,
               showmeans=False, 
               medianprops={"color": "white", "linewidth": 0.5},
               boxprops={"facecolor": "lightcoral", "edgecolor": "white", "linewidth": 0.5},
               whiskerprops={"color": "lightcoral", "linewidth": 1.5},
               capprops={"color": "lightcoral", "linewidth": 1.5}
         )


plt.xticks(ticks=x_pos, labels=x_labels)

plt.tight_layout()
plt.show()
exit()