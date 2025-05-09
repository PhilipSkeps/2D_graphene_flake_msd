#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import pandas as pd

if ( len(sys.argv) != 2 ):
    print("Requires a filename as a argument")
    exit()

df = pd.read_csv(sys.argv[1])

plt.loglog(df[df.columns[0]], df[df.columns[1]], label = df.columns[1])
plt.loglog(df[df.columns[0]], df[df.columns[2]], label = df.columns[2])
plt.loglog(df[df.columns[0]], df[df.columns[3]], label = df.columns[3])
plt.legend(loc=2, prop={'size': 8})
plt.title("MSD")
plt.xlabel("Tau (ps)")
plt.ylabel("MSD (nm^2)")
fig = plt.gcf()
fig.set_size_inches((11, 8), forward=False)
plt.savefig(os.path.splitext(sys.argv[1])[0] + ".png", dpi = 500)
plt.show()
