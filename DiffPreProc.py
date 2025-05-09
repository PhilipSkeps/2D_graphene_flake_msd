#!/usr/bin/python

import os
import re
import pandas as pd
import numpy as np
import sys

# first arg is True or False for splitcol
# next args are the groups

# pass file groups using wildcard expansion
# groupby = [ "water_dppc54ApLg_prodtrim0-10000_1", 
#     "water_dppc54ApLg_prodtrim0-10000_2", 
#     "water_dppc54ApLg_prodtrim0-10000_3", 
#     "water_dppc54ApLg_prodtrim0-10000_4",
#     "water_dppc54ApLg_prodtrim0-10000_5"]

groupby = sys.argv[1:]

def xvgreader(file):
    returnTime = []
    returnData = []
    DataTitle = []
    FileIden = []
    with open(file, "r") as fh:
        for line in fh:
            regx = re.compile("^@|^#")
            lineList = []
            if re.compile('xaxis').search(line):
                TimeTitle = re.search(r'xaxis\s+label\s+\"(.*)\"', line).group(1)
            if re.compile(r"^@\s+s[0-9]\s+legend\s+").search(line):
                DataTitle.append(re.search(r"^@\s+s[0-9]\s+legend\s+\"(.*)\"", line).group(1))
                FileIden.append(re.search(r"^@\s+s[0-9]*\s+legend\s+\"D\[resnr\s+([0-9]*)", line).group(1))
            if not regx.match(line):
                lineList = line.strip().split()
                returnTime.append(lineList[0])
                del lineList[0]
                returnData.append(lineList)
    returnData = list(zip(*returnData))
    return(returnTime, returnData, TimeTitle, DataTitle, FileIden)

def write_to_csv(df_list, groupNames):
    for i, df in enumerate(df_list):
        df.to_csv(groupNames[i] + '.csv', index = False)

lsdir = os.scandir(os.getcwd())

xvgfiles = [ x.name for x in lsdir if (".xvg" in x.name)] # get all xvg files from dir

lsdir.close()

groupedfiles = [] # list of tuples that contain a list and name of group

if (len(groupby) == 0):
    groupedfiles = [("ALL", xvgfiles)]
else: 
    for group in groupby:
        groupedfiles.append((group, [x for x in xvgfiles if (re.match(group, x))]))

DataHandler = []
groupNames = []

for filenamepair in groupedfiles:
    PreviousTime = None
    PreviousCols = None
    SubDataHandler = []
    for file in filenamepair[1]:
        (Time, Data, TimeTitle, DataTitle, FIleIden) = xvgreader(file)
        if (PreviousTime != None):
            if (Time != PreviousTime):
                sys.stderr.write("Files that are grouped must have the same time points")
                exit()
        if (PreviousCols != None):
            if (len(Data) != PreviousCols):
                sys.stderr.write("Files that are grouped must have the same number of columns")
                exit()
        else:
            SubDataHandler = [[Time]] * len(Data)
            TitleHandler = [[]] * len(Data)
        for i, Col in enumerate(Data):
            SubDataHandler[i] = SubDataHandler[i].copy() # HACK
            SubDataHandler[i].append(list(Col))
            TitleHandler[i] = TitleHandler[i].copy()
            TitleHandler[i].append(file)

        PreviousTime = Time
        PreviousCols = len(Data)

    for f, Data2D in enumerate(SubDataHandler):
        tempDF = pd.DataFrame(Data2D).T
        groupNames.append(filenamepair[0] + "_" + FIleIden[f])
        TitleHandler[f][0:0] = [TimeTitle]
        tempDF.columns = TitleHandler[f]
        DataHandler.append(tempDF) # append pandas dataframe

write_to_csv(DataHandler, groupNames)

