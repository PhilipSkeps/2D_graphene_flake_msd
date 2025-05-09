#!/usr/bin/python

import sys
import os
import re
import math

import matplotlib.pyplot as plt
import pandas as pd

def handleArgs():
    if (len(sys.argv) != 2):
        
        print("A xvg or csv file must be passed as a command line arg")
        exit(0)

    if not os.path.isfile(sys.argv[1]):

        print("File provided could not be found")
        exit(0)

    return sys.argv[1]



def createCSV(FileName:str):

    MatchFlakeNum = re.compile("^@ s[0-1] legend \"D\[resnr ([0-9]*)")
    MatchData = re.compile("^\s+([0-9]*\.[0-9]*)\s+([0-9]*\.{0,1}[0-9]*)\s+([0-9]*\.{0,1}[0-9]*)")
    
    dfcolumnList = list()

    df = pd.DataFrame(columns=range(3))
    dfcolumnList.append("LagTime (ps)")

    with (open(FileName, "r") as FH):
        
        for Line in FH:

            if ((FlakeGroup := MatchFlakeNum.match(Line)) != None):
                dfcolumnList.append(FlakeGroup.group(1))

            if ((DataGroup:= MatchData.match(Line)) != None): # only works if two flakes are in sim
                df.loc[len(df.index)] = [DataGroup.group(1), DataGroup.group(2), DataGroup.group(3)]


    df.columns = dfcolumnList
    df.to_csv(os.path.splitext(FileName)[0] + ".csv", index=False)

    return df



def readCSV(FileName:str):
    
    df = pd.read_csv(FileName)
    return df



def slope(row1:pd.Series, row2:pd.Series):
    
    row1L = row1
    row2L = row2

    LagTime = (float(row1L[0]) + float(row2L[0])) / 2
    Flake1Slope = (math.log(float(row1L[1])) - math.log(float(row2L[1]))) / (math.log(float(row1L[0])) - math.log(float(row2L[0])))
    Flake2Slope = (math.log(float(row1L[2])) - math.log(float(row2L[2]))) / (math.log(float(row1L[0])) - math.log(float(row2L[0])))

    returnTup = (LagTime, Flake1Slope, Flake2Slope)

    return returnTup



def slopeDFChef(df:pd.DataFrame):
    
    returnDF = pd.DataFrame(index=range(len(df.index) - 2), columns=["Average LagTime (ps)", df.columns[1], df.columns[2]])

    for i in range(1, len(df.index) - 1):
        
        j = i + 1
        returnDF.iloc[i-1] = slope(df.iloc[i], df.iloc[j])

    return returnDF



def graphSlopes(df:pd.DataFrame, fileroot:str):

    df.to_csv(fileroot + "_LogMSDSlope.csv",index=False)

    plt.scatter((df[df.columns[0]]), (df[df.columns[1]]), label=df.columns[1])
    plt.scatter(df[df.columns[0]], df[df.columns[2]], label=df.columns[2])
    plt.ylim((0,2))
    plt.xlim((0,300))
    plt.legend(loc=2, prop={'size': 8})
    fig = plt.gcf()
    fig.set_size_inches((11, 8), forward=False)
    plt.savefig(fileroot + ".png", dpi = 500)
    plt.show()



if __name__ == "__main__":
    
    FileName = handleArgs()
    #FileName = "/home/pskeps/HomeDir/misc/GROM_RES/prod54ApLxtc/water_dppc54ApLg_prodtrim0-10000_5xy.xvg"
    df = pd.DataFrame()
    slopedf = pd.DataFrame()

    FileDecomp = os.path.splitext(FileName)

    if (FileDecomp[1] != ".csv"):
        df = createCSV(FileName)
    else:
        df = readCSV(FileName)
    
    slopedf = slopeDFChef(df)
    graphSlopes(slopedf, FileDecomp[0])