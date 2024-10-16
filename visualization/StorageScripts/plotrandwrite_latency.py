import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


sns.set_theme('paper', font_scale=1.35, style='whitegrid', rc={"axes.titlesize": 18, "axes.labelsize": 16})


x_name = 'Block Size'

x_val = ['8k', '32k', '256K', '1024K', '4m']
y_name = 'Latency (avg) - msec'


var_name = 'Test Platform'


bf2_vals = np.array([1.719067, 3.95793, 35.71001, 127.02, 441.78])
bf3_vals = np.array([0.05224, 0.14357, 1.17736, 6.39172, 18.68073])
host_vals = np.array([0.031463, 0.03655, 0.16888, 0.650357, 2.432653])
Oct_vals = np.array([5, 5, 5, 5, 5])


raw_data = pd.DataFrame.from_dict({x_name: x_val, 'BF-2': bf2_vals, 'BF-3': bf3_vals, 'Host (FarNet1)': host_vals, 'Octeon 10': Oct_vals})
data = pd.melt(raw_data, id_vars=x_name, value_name=y_name, var_name=var_name)


plt.figure(figsize=(8, 5))
ax = sns.barplot(data=data, x=x_name, y=y_name, hue=var_name, dodge=True, gap=0.12)


for p in ax.patches:
    if p.get_height() > 0:
        ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points', size=10, weight='bold')


ax.set_xticklabels(ax.get_xticklabels(), size=18)
ax.set_yticklabels(ax.get_yticklabels(), size=18, weight='bold')
ax.set_title('Latency (avg) - Random Writes (QD=1, P=1)', size=20, weight='bold', pad=20)


plt.legend(fontsize=13.8, loc='upper left')
plt.tight_layout()


plt.savefig('./latency/random-writes-latency.pdf')