#!/usr/bin/python

## MAY NEED MORE DEBUGGING

## NOTE WE DO NOT NEED TO PERFORM PERIODIC CORRECTIONS FOR TWOY ONLY TWO X

import re
import math
import sys
from collections import defaultdict
from enum import Enum

PERDISTANCE = 5 # nm
# build a pair list prior to runtime and then fill it with coords at run time

def lte(LHS, RHS):
    return LHS <= RHS

def gte(LHS, RHS):
    return LHS <= RHS

class PERTYPE(Enum):
    FOUR = 3
    TWOX = 2
    TWOY = 1
    ZERO = 0



def distance(X1, X2, Y1, Y2):
    return math.sqrt((X1 - X2) ** 2 + (Y1 - Y2) ** 2)



def typePer(GraphCarbCoords): # this may not work may have to increase cutoff or check all four corners or somethin idk its late

    CountX = int()
    CountY = int()
    PerTypeMap = defaultdict(PERTYPE)

    for FlakeNum, CarbList in GraphCarbCoords.items():
        for X, Y in CarbList:
            if ( X < 0.11 and Y < 0.11):
                PerTypeMap.update({FlakeNum:PERTYPE.FOUR})
                break
            elif (X < 0.11):
                CountX += 1
            elif (Y < 0.11):
                CountY += 1

        else:
            if (CountX > CountY):
                PerTypeMap.update({FlakeNum:PERTYPE.TWOX})
            elif (CountY < CountX):
                PerTypeMap.update({FlakeNum:PERTYPE.TWOY})
            else:
                PerTypeMap.update({FlakeNum:PERTYPE.ZERO})

    return PerTypeMap



def findPairFour(X, Y, BoundX, BoundY, CoordListX, CoordListY, Index):

    FoundAtom = int()
    TestList = [(0, 0), (0, BoundY), (BoundX, 0), (BoundX, BoundY)]

    MinDist = distance(X, TestList[0][0], Y, TestList[0][1])
    minIndex = 0

    for i in range(1, len(TestList)):
        
        Dist = distance(X, TestList[i][0], Y, TestList[i][1])

        if Dist < MinDist:
            MinDist = Dist
            minIndex = i

    # performance increase by going backwards
    i = Index - 1
    while (True): # will loop infinitely if no periodic atom exists for current definition

        FoundAtom = i + 1    
        
        if (distance(X, CoordListX[i], Y, CoordListY[i]) > PERDISTANCE):
            break

        i -= 1

    return TestList[minIndex][0], TestList[minIndex][1], ((TestList[minIndex][0], CoordListX[FoundAtom]), (TestList[minIndex][1], CoordListY[FoundAtom]))



def findPairTwo(XcoordList, YCoordList, X, Y, PerType, TestIndex):

    ClosestMatch = float()
    SearchVal = float()
    SearchList = list()
    ClosestIndex = int()

    if (PerType == PERTYPE.TWOX):
        ClosestMatch = abs(XcoordList[0] - X)
        SearchVal = X
        SearchList = XcoordList
    else:
        ClosestMatch = abs(YCoordList[0] - Y)
        SearchVal = Y
        SearchList = YCoordList

    for Index, Test in enumerate(SearchList):

        if abs(Test - SearchVal) < ClosestMatch and TestIndex != Index:
            ClosestMatch = abs(Test - SearchVal)
            ClosestIndex = Index

    return XcoordList[ClosestIndex], YCoordList[ClosestIndex]



def genCoordList(HydroList, AtomDict):

    YCoordList = list()
    XCoordList = list()

    for Hydro in HydroList:
        XCoordList.append(AtomDict[Hydro][0])
        YCoordList.append(AtomDict[Hydro][1])

    return XCoordList, YCoordList



def trackEdges(GraphDict, GraphCarbCoords, BoundX, BoundY):

    PerTypeMap = typePer(GraphCarbCoords)
    
    OrderedPairDict = defaultdict(list)
    YCoordList = list()
    XCoordList = list()
    
    for FlakeNum, AtomDict in GraphDict.items():
        
        (XCoordList, YCoordList) = genCoordList(HydroList, AtomDict)
        
        TempList = list()

        for i in range(len(YCoordList)):
            
            j = i + 1

            if j == len(YCoordList):

                j = 0

            X1 = XCoordList[i]
            X2 = XCoordList[j]
            Y1 = YCoordList[i]
            Y2 = YCoordList[j]

            if (PerTypeMap[FlakeNum] != PERTYPE.ZERO):

                Dist = distance(X1, X2, Y1, Y2)

                if ( Dist > 0.4): # if we need a performance increase these pairs are being added in not consecutive order which may help speed up final step

                    if (PerTypeMap[FlakeNum] == PERTYPE.TWOX or PerTypeMap[FlakeNum] == PERTYPE.TWOY):
                        (X2, Y2) = findPairTwo(XCoordList, YCoordList, X1, Y1, PerTypeMap[FlakeNum], i)

                    else:
                        (X2, Y2, AdditPair) = findPairFour(X1, Y1, BoundX, BoundY, XCoordList, YCoordList, i)
                        TempList.append(AdditPair)


            TempList.append( ((X1, X2), (Y1, Y2)) ) # store Y info

        OrderedPairDict.update({FlakeNum:TempList})

    return OrderedPairDict



def parseGro(Filename):

    MatchFrame = re.compile("Protein\s+t=\s*([0-9]*\.[0-9]*)\s*step=\s*[0-9]*$")
    MatchDPPC = re.compile("\s*([0-9]*)DPPC[\saA0-zZ9]{6}\s*([0-9]*)\s*([0-9]*\.[0-9]*)\s+([0-9]*\.[0-9]*)\s*([0-9]*\.[0-9]*)")
    MatchGraph = re.compile("\s*([0-9]*)GP001\s+[aA0-zZ9]*\s+(C[a-z]*|H[a-z]*)[0-9]*\s+([0-9]*\.[0-9]*)\s+([0-9]*\.[0-9]*)\s+[0-9]*\.[0-9]*")
    MatchSize = re.compile("\s*([0-9]*\.[0-9]*)\s+([0-9]*\.[0-9]*)\s+([0-9]*\.[0-9]*)")

    FrameDict = {}
    FrameNumber = float()
    GraphNumSorted = list()
    Size = float()

    DPPCDict = defaultdict(list)
    GraphDict = defaultdict(dict)
    GraphCarbCoords = defaultdict(list)
    GraphPairMap = dict()
    Frame = 0
    GraphNum = set()

    with open(Filename, "r") as FH:

        for line in FH:

            if (CapDPPC := MatchDPPC.match(line)) is not None:
                if (int(CapDPPC.group(1)) == 79):
                    print()

                if int(CapDPPC.group(2)) - 130 * (int(CapDPPC.group(1)) - 1) >= 42: #count only tail info

                    DPPCDict[int(CapDPPC.group(1))].append((float(CapDPPC.group(3)), float(CapDPPC.group(4)), float(CapDPPC.group(5)))) # store Y and Z info
                    
                continue

            elif (CapGraph := MatchGraph.match(line)) is not None:

                if "C" in line:
                    GraphCarbCoords[int(CapGraph.group(1))].append((float(CapGraph.group(3)), float(CapGraph.group(4))))
                else:
                    GraphNum.add(int(CapGraph.group(1)))
                    GraphDict[int(CapGraph.group(1))].update({CapGraph.group(2):(float(CapGraph.group(3)), float(CapGraph.group(4)))})
                
                continue

            elif (CapFrame := MatchFrame.match(line)) is not None:

                FrameNumber = CapFrame.group(1)
                
                if Frame != 0: # not beginning frame

                    GraphPairMap = trackEdges(GraphDict, SizeX, SizeY)
                    FrameDict.update({FrameNumber:(DPPCDict.copy(), GraphPairMap.copy())})
                
                Frame+=1
                continue

            elif (CapSize := MatchSize.match(line)) is not None:

                SizeX = float(CapSize.group(1))
                SizeY = float(CapSize.group(2))
                SizeZ = float(CapSize.group(3))
        
        else:

            GraphNumSorted = sorted(list(GraphNum))
            GraphPairMap = trackEdges(GraphDict, GraphCarbCoords, SizeX, SizeY)
            FrameDict.update({FrameNumber:(DPPCDict.copy(), GraphPairMap.copy())})

    return FrameDict, GraphNumSorted, SizeZ, SizeX



def countDPPC(FrameDict, GraphNumsorted, Cutoff, BoundX):

    CheckLen = BoundX / 2

    DPPCFrameList = list()

    for Frame, Tuple in FrameDict.items():
        
        DPPCDict = Tuple[0]
        GraphPairMap = Tuple[1]

        CheckPairList = list()
        Flake = int()
        DPPCNumMap = defaultdict(list)

        for DPPCNum, DPPCAtomList in DPPCDict.items():

            AtomCount = 0

            if DPPCNum == 112:
                print()

            for X, Y, Z in DPPCAtomList:
                
                if (X < CheckLen): # we need to flip
                    CheckDirection = lte
                else:
                    CheckDirection = gte

                if Z > Cutoff: # might grab the wrong list
                    Flake = GraphNumsorted[0]
                else:
                    Flake = GraphNumsorted[1]
                
                CheckPairList = GraphPairMap[Flake]

                IntersectCount = 0
                for XValue, YValue in CheckPairList:
                    if (CheckDirection(XValue[0], X) and CheckDirection(XValue[1], X)):
                        if ((Y < YValue[0] and Y > YValue[1]) or (Y > YValue[0] and Y < YValue[1])):
                            IntersectCount += 1
                
                if IntersectCount % 2 == 1:
                    AtomCount += 1

            if AtomCount / 89 > 0.6:
                DPPCNumMap[Flake].append(DPPCNum)

        DPPCFrameList.append(DPPCNumMap)
    
    return DPPCFrameList



def autoPyMoL(DPPCFrameList, filename):
    
    import pymol
    from pymol import cmd
    pymol.finish_launching()

    cmd.load(filename)

    DPPCSel = "(resi "

    for i, Frame in enumerate(DPPCFrameList):
        for GraphNum, FoundList in Frame.items():
            for Item in FoundList:
                DPPCSel += str(Item) + '+'

    DPPCSel = DPPCSel[:-1] + ')'
    RestSel = "(not (resn GP001) and not" + DPPCSel + ")"

    cmd.hide(selection="(resn SOL)")
    cmd.color("red", "(resn GP001)")
    cmd.color("yellow", DPPCSel)
    cmd.set("stick_transparency", 0.1, RestSel) #IDK why this line dont work but its aight I guess
    cmd.color("0xADD8E6", RestSel)



if __name__ == "__main__":

    # Hardcoded needs to change for other flake designs

    HydroList = ['Hwo', 'Hwm', 'Hwq', 'Hwu', 'Hxx', 'Hxy', 'Hxz', 'Hya', 'Hwk', 'Hyb', 'Hyc', 'Hyd', 'Hye', \
                 'Hyf', 'Hyg', 'Hyh', 'Hyi', 'Hyj', 'Hwd', 'Hwe', 'Hwf', 'Hwg', 'Hwh', 'Hwi', 'Hwj', 'Hwl', \
                 'Hwn', 'Hwp', 'Hwr', 'Hwt', 'Hwv', 'Hwx', 'Hwz', 'Hxb', 'Hxd', 'Hxg', 'Hxh', 'Hxj', 'Hxl', \
                 'Hxn', 'Hxo', 'Hxq', 'Hxs', 'Hxu', 'Hxv', 'Hxt', 'Hxr', 'Hxp', 'Hxm', 'Hxw', 'Hxk', 'Hxi', \
                 'Hxf', 'Hxe', 'Hxc', 'Hxa', 'Hwy', 'Hww', 'Hwc', 'Hws']

    # if (len(sys.argv) != 2):
    #     print("please provide a gro filename")
    #     exit()
    
    # filename = sys.argv[1]

    filename = "/home/pskeps/HomeDir/misc/GROM_RES/test/test.gro"

    (FrameDict, GraphNumsorted, Cutoff, BoundX) = parseGro(filename)

    DPPCFrameList = countDPPC(FrameDict, GraphNumsorted, Cutoff / 2, BoundX)

    for i, Frame in enumerate(DPPCFrameList):
        for GraphNum, FoundList in Frame.items():
            print(GraphNum, ":")
            print(*FoundList, sep=" ")
            print("Total: ", len(FoundList))

    autoPyMoL(DPPCFrameList, filename)


