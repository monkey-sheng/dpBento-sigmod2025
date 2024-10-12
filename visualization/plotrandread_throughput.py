import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


sns.set_theme('paper', font_scale=1.35, style='whitegrid', rc={"axes.titlesize": 18, "axes.labelsize": 16})


x_name = 'Block Size'
x_val = ['8k', '32k', '256K', '1024K', '4m']
y_name = 'Throughput - MB/s'


var_name = 'Test Platform'


bf2_vals = np.array([9.369792, 28.06667, 41.9, 42.9, 42.6])
bf3_vals = np.array([283.4, 770.6, 1565.2, 1554.8, 1543.4])
host_vals = np.array([2037.333, 3115.667, 4362.667, 5372.333, 5177.667])
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
ax.set_title('Throughput - Random Reads', size=20, weight='bold', pad=20)

plt.legend(fontsize=13.8, loc='upper left')
plt.tight_layout()

plt.savefig('./throughput/random-reads-throughput.pdf')
