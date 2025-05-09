#!/usr/bin/python

# compute diffusivities for all files provided and store in a csv file
# save a image of a boxwhisker plot

# something may be screwy talk to samaniuk

import sys
import os
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

def calcDiffStats(csvfile, start, end):
    table = []
    dfcsv = pd.read_csv(csvfile)
    flake = re.search(r'_([0-9]*)\.csv$', csvfile).group(1)
    dfselrows = dfcsv.loc[(dfcsv['tau (ps)'] >= int(start)) & (dfcsv['tau (ps)'] <= int(end))]
    for Column in dfselrows.columns[1:]:
        Diff = (dfselrows[Column].iloc[0] - dfselrows[Column].iloc[-1]) / (dfselrows['tau (ps)'].iloc[0] - dfselrows['tau (ps)'].iloc[-1] ) / 4 * (10 ** 6)
        table.append((flake, Column, Diff))
    return table

if (len(sys.argv) < 2):
    print("Requires a filename as a argument")
    exit()

start = sys.argv[1]
end = sys.argv[2]

if start > end:
    print("Start must be less than end")
    exit()

df = pd.DataFrame()

for file in sys.argv[3:]:
    if os.path.isfile(file) and os.path.splitext(file)[1] == ".csv" and "CoM" not in file:
        df = pd.concat([df, pd.DataFrame(calcDiffStats(file, start, end))], ignore_index = True)

df = df.set_axis(["flake", "file", "Diff (um^2 / s)"], axis='columns',copy=False)
df.to_csv("DiffusivityTable" + start + "-" + end + ".csv", index=False)

# plot box whisker
# hardcoded for now

ApLDataScat = []
ApLData = []
ApL = []

# retrive unique values in place

for x in range(0,df.shape[0] - 29,30):
    tempdf = df.loc[ x:x + 29, :]

    ApL += tempdf[tempdf.file.str.contains("[0-9]xy.xvg$", regex=True)]['file'].to_list()
    ApL += tempdf[tempdf.file.str.contains("[0-9]x.xvg$", regex=True)]['file'].to_list()
    ApL += tempdf[tempdf.file.str.contains("[0-9]y.xvg$", regex=True)]['file'].to_list()

    ApLDataScat.append(tempdf[tempdf.file.str.contains("[0-9]xy.xvg$", regex=True)]["Diff (um^2 / s)"].to_list())
    ApLDataScat.append(tempdf[tempdf.file.str.contains("[0-9]x.xvg$", regex=True)]["Diff (um^2 / s)"].to_list())
    ApLDataScat.append(tempdf[tempdf.file.str.contains("[0-9]y.xvg$", regex=True)]["Diff (um^2 / s)"].to_list())

    ApLData.append(tempdf[ ~tempdf.file.str.contains("[0-9]xy.xvg$", regex=True)]["Diff (um^2 / s)"].to_list())

ApL = pd.unique([''.join(re.search(r"(.*_)[0-9]([x-y]*.xvg$)", x).group(1,2)) for x in ApL])

ApLData = np.asarray(ApLData, dtype="float")
ApLDataScat = np.asarray(ApLDataScat, dtype="float")

ApLy = [[i] * len(ApLDataScat[0]) for i in range(1, len(ApLData) + 1) for d in range(3)]

BoxListXY = []
BoxListXYLabel = []


y = None
x = None
for i, file in enumerate(ApL):
    if re.search(r"_xy.xvg$", file):
        BoxListXY.append(ApLDataScat[i])
        BoxListXYLabel.append(file)
    elif re.search(r"_y.xvg$", file):
        y = plt.scatter(ApLDataScat[i], ApLy[i], color=["red"])
    else:
        x = plt.scatter(ApLDataScat[i], ApLy[i], color=["green"])

ApL = [''.join(re.search(r"(^.*)_[x|y]\.xvg$", x).group(1)) for x in ApL if re.search(r"(^.*)_[x|y]\.xvg$", x) != None]
ApL = pd.unique(ApL)

plt.boxplot(ApLData.T, vert=False)
plt.xlabel("Diff (um^2 / s)")
plt.xscale("log")
plt.yticks(range(1,len(ApLData) + 1), ApL)
plt.ylabel("file")
plt.title("Box Whisker Plot of ApL Diff 1D")
plt.legend([y, x], ['y', 'x'] * 3)
fig = plt.gcf()
fig.set_size_inches((15, 11), forward=False)
plt.savefig("DiffusivityTableScatter1D" + ".png")
plt.show()

BoxListXY = np.asarray(BoxListXY, dtype="float")
plt.boxplot(BoxListXY.T, vert=False)
plt.xlabel("Diff (um^2 / s)")
plt.xscale("log")
plt.yticks(range(1,len(BoxListXYLabel) + 1), BoxListXYLabel)
plt.ylabel("file")
plt.title("Box Whisker Plot of ApL Diff XY")
fig = plt.gcf()
fig.set_size_inches((15, 11), forward=False)
plt.savefig("DiffusivityTableScatterXY" + ".png")
plt.show()
