#!/usr/bin/python

import sys
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

if (len(sys.argv) != 2):
    print("A file must be given to the program")

with open(sys.argv[1]) as CoMXVG:
    lines = CoMXVG.readlines()

linedata = []
for line in lines:
    if not re.match("#|@", line):
        data = line.split()
        linedata.append(data)

df = pd.DataFrame(linedata, columns=['Time', 'X', 'Y', 'Z'])
df.to_csv(os.path.splitext(sys.argv[1])[0] + ".csv", index=False)

points = np.array([df['X'], df['Y']]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

fig, ax = plt.subplots()
lc = LineCollection(segments, cmap='viridis')
lc.set_array(df['Time'].astype(int))
lc.set_linewidth(2)
line = ax.add_collection(lc)
fig.colorbar(line,ax=ax)
ax.autoscale_view(True,True,True)
plt.savefig(os.path.splitext(sys.argv[1])[0] + ".png", dpi = 500)
plt.show()

