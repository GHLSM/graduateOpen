from collections import Counter
from app.graph.dtc_graph import DtcGraph
import time
from conf.config import MAINTAIN_TIME, dataCSV, POSSIBLEXCEL
import csv
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    def __init__(self, nodeName, fatherNode, allCount, count=1) -> None:
        self.name = nodeName
        self.count = count
        self.allCount = allCount
        self.father = fatherNode
        self.children = {}
        self.sameNodeLink = None
        if self.name != "root":
            self.possible2all = count / allCount
            if self.father.count != None:
                self.possible2father = count / self.father.count
    '''
    仅做测试用，检查构造的树是否正确
    def disp(self, ind=1):
        # print('     ' * ind, self.name, '   ', self.count)
        print(' ' * ind, self.name, ':', self.count, " ", end="|")
        ind += 1
        for child in self.children.values():
            child.disp(ind)
        print("\n")
    '''

    def update(self, count):
        self.count += count
        self._moreData()

    def _moreData(self):
        self.possible2all = self.count / self.allCount
        if self.father.count != None:
            if self.father.count != 0:
                self.possible2father = self.count / self.father.count
# region
# def showChlildren(fatherNode):
#     for child in fatherNode.children:
#         print(child.name, ":", child.count, "|", end="")

# def showTree(headerTable, orderItem):
#     rootNode = headerTable[orderItem[0]][1].father
#     while rootNode.children != None:
#         showChlildren(rootNode)
#         print("\n")
#         for child in rootNode.children:
#             rootNode = child
# endregion

def fpGrowth(data, minSupportRate):
    # frequency = [1 for i in len(dataDict)]
    dataDict = dict(Counter(data))
    minSupport = len(data) * minSupportRate
    print("header Table Constructing...")
    headerTable, orderItem = constructHeader(dataDict, minSupport)
    headerTable = constructTree(dataDict, headerTable, orderItem)
    supportDict = CpTree(headerTable, orderItem, minSupport)
    return supportDict, orderItem

def constructHeader(dataDict, minSupport):
    headerTable = {}
    itemSet = frozenset([item for transaction in dataDict for item in transaction])
    for item in itemSet:
        supportCount = 0
        for transaction in dataDict:
            if item in transaction:
                supportCount += dataDict[transaction]
        if supportCount >= minSupport:
            headerTable[item] = supportCount
    '''引入一个排序列表，排序按值的降序进行，当值相同时则按键的字典序'''
    '''
    headertable = {
        "u1234":频次
    }
    '''
    orderItem = [itemSupport[0] for itemSupport in sorted(headerTable.items(), key=lambda x: (x[1], x[0]), reverse=True)]

    for item in headerTable:
        headerTable[item] = [headerTable[item], None]

    '''
    headerTbale = {
        "u1234":[频次,None]
    }
    '''
    return headerTable, orderItem

def constructTree(dataDict, headerTable, orderItem):
    # 空节点
    root = Node("root", None, None, None)
    for transaction in dataDict:
        fatherNode = root             
        for item in orderItem:
            if item in transaction:
                count = dataDict[transaction]
                fatherNode = update(item, fatherNode, headerTable, count)
    return headerTable

def update(item, fatherNode, headerTable, count):
    if item not in fatherNode.children:
        newNode = Node(item, fatherNode, headerTable[item][0], count)
        fatherNode.children[item] = newNode

        '''更新同名项链表'''
        linkNode = headerTable[item][1]
        if linkNode == None:
            headerTable[item][1] = newNode
        else:
            while linkNode.sameNodeLink != None:
                linkNode = linkNode.sameNodeLink
            linkNode.sameNodeLink = newNode
    else:
        fatherNode.children[item].update(count)
    return fatherNode.children[item]

def trace(item, headerTable):
    cpBase = {}
    headNode = headerTable[item][1]
    '''由头指针表横向搜索所有同名项'''
    while headNode != None:
        prefix = []
        #leaf_node = deepcopy(head_node)
        leafNode = headNode
        while leafNode.father != None:
            prefix.append(leafNode.name)
            leafNode = leafNode.father

        if len(prefix) > 1:
            cpBase[frozenset(prefix[1:])] = headNode.count
        headNode = headNode.sameNodeLink
    return cpBase

def CpTree(headerTable, orderItem, minSupport, suffix=set(), itemDict={}):
    for item in reversed(orderItem):
        newItem = suffix.copy()
        newItem.add(item)
        itemDict[frozenset(newItem)] = itemDict.get(frozenset(newItem),0) + headerTable[item][0]
        cpBase = trace(item, headerTable)
        cpHeaderTable, cpOrderItem = constructHeader(cpBase, minSupport)
        cpHeaderTable = constructTree(cpBase, cpHeaderTable, cpOrderItem)
        if cpHeaderTable != None:
            CpTree(cpHeaderTable, cpOrderItem, minSupport, newItem, itemDict)
    return itemDict

def findLink(headerTable, orderItem, confidence):
    confidenceDict = {}
    edges = []
    for item in reversed(orderItem):
        headNode = headerTable[item][1]
        while headNode != None:
            leafNode = headNode
            leafNode = leafNode.father
            while leafNode.father != None:
                # 如果表中已有，则相加dtc链接可能性
                confidenceDict[(leafNode.name, headNode.name)] = \
                    confidenceDict.get((leafNode.name, headNode.name), 0) + \
                        (headNode.count / leafNode.count) * leafNode.possible2all

                confidenceDict[(headNode.name, leafNode.name)] = \
                    confidenceDict.get((headNode.name, leafNode.name), 0) + \
                        headNode.possible2all

                leafNode = leafNode.father
            headNode = headNode.sameNodeLink

    for edge in confidenceDict:
    # 支持度判定
        a,b = edge
        if confidenceDict[edge] >= confidence:
            # 添加相关性判定、使用Kulczynski进行关联度判定，考虑是否添加IR偏度计算？
            # Kulczynski = (1 / 2) * (confidenceDict[edge] + confidenceDict.get((b,a)))
            # if Kulczynski >= 0.5:
            edges.append(edge)
    return confidenceDict, edges

def fpGrowthWithGraph(CAR, data, minSupportRate, confidence, allDTC):
    dataDict = dict(Counter(data))
    minSupport = len(data) * minSupportRate
    TreeNode = frozenset([item for transaction in dataDict for item in transaction])
    print("header Table Constructing...")
    headerTable, orderItem = constructHeader(dataDict, minSupport)
    print("construct tree...")
    headerTable = constructTree(dataDict, headerTable, orderItem)
    print("find link ...")
    confidenceDict, edges = findLink(headerTable, orderItem, confidence)
    print("formating graph")
    graph = DtcGraph(CAR)
    graph.add_nodes(TreeNode)
    graph.load_from_man(allDTC, edges)
    return graph, confidenceDict, orderItem

def formatHistoryData(faultDict):
    dataSet = []
    for vin in faultDict:
        flag = True
        dtcArray = faultDict.get(vin)
        if len(dtcArray) == 1 :
            line = []
            dtcInfo = dtcArray[0].get("dtc_info")
            for infoItem in dtcInfo:
                for dtc in infoItem.get("dtcs"):
                    line.append(dtc)
            dataSet.append(frozenset(line))
        else:
            timeArray = []
            for item in dtcArray:
                # '2021/8/15 12: 45: 03'
                maTime = item.get("time")
                maTime = time.mktime(time.strptime(maTime, "%Y/%m/%d %H:%M:%S"))
                timeArray.append(maTime)
            timeArray.sort()

            while flag:
                # 一次维修时间最长为3天，超过三天的维修数据认为是两次案例
                firstTime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(timeArray[0]))
                for item in dtcArray:
                    maTime = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.mktime(time.strptime(item.get("time"), "%Y/%m/%d %H:%M:%S"))))
                    if maTime == firstTime:
                        dtcInfo = item.get("dtc_info")
                        line = []
                        for infoItem in dtcInfo:
                            for dtc in infoItem.get("dtcs"):
                                line.append(dtc)
                        dataSet.append(frozenset(line))

                if (timeArray[0] + MAINTAIN_TIME < timeArray[-1]):
                    midTime = timeArray[0] + MAINTAIN_TIME
                    for index, timeItem in enumerate(timeArray):
                        # if index <= len(timeArray):
                        if timeItem > midTime:
                            timeArray = timeArray[index:]
                            # print(timeArray, len(timeArray))
                            if len(timeArray) == 0:
                                flag = False
                            break
                else:
                    break
    dataSet = dataSet[1:]
    # createCSVFile("E50Dtc.csv", dataSet)
    return dataSet

def createCSVFile(fName, dataSet):
    fileRoute = os.path.join(dataCSV, fName)
    with open(fileRoute, "w", encoding='utf-8', newline="") as f:
        writer = csv.writer(f)
        for item in dataSet:
            writer.writerow(item)

def writeMatrix2excel(confidenceDict, data):
    for index, item in enumerate(data):
        columns = []
        for dtc in item:
            columns.append(dtc)
        rows = columns[:]
        ratesArray = []
        
        for i in range(len(rows)):
            rates = []
            for j in range(len(columns)):
                if i == j:
                    rate = 1
                    rates.append(rate)
                else:
                    twin = rows[i], columns[j]
                    rate = confidenceDict.get(twin, 0)
                    rates.append(rate)

            ratesArray.append(rates)
        dataDf = pd.DataFrame(ratesArray)
        dataDf.index = rows
        dataDf.columns = columns
        writer = pd.ExcelWriter(os.path.join(POSSIBLEXCEL, '%d.xlsx' %(index + 1)))
        dataDf.to_excel(writer,float_format='%.5f')
        writer.save()

def one2allPossible(dtc, confidenceDict, confidence):
    otherDtc = {}
    for item in confidenceDict:
        if dtc == item[0]:
            if confidenceDict[item] >= confidence:
                otherDtc[item[1]] = confidenceDict[item]
    return otherDtc

def all2OnePossible(dtc, confidenceDict, confidence):
    otherDtc = {}
    for item in confidenceDict:
        if dtc == item[1]:
            if confidenceDict[item] >= confidence:
                otherDtc[item[0]] = confidenceDict[item]
    return otherDtc

def getRightDtcAssociate(dtc, confidenceDict, confidence, ok_set=set()):
    ok_set.add(dtc)
    info = {"name":dtc, "children":[], "value":""}
    ret = one2allPossible(dtc, confidenceDict, confidence)
    if len(ret.keys()) == 0:
        ok_set.remove(dtc)
        return info
    for item in ret.keys():
        if item in ok_set:
            ok_set.remove(dtc)
            return info
        ret2 = getRightDtcAssociate(item, confidenceDict, confidence, ok_set)
        if ret2:
            info["children"].append(ret2)
    ok_set.remove(dtc)
    return info
   



def findItems(dtc, data):
    items = []
    for item in data:
        if dtc in item:
            items.append(item)
    return items

def findLeftLinkSet():
    newDtcSet = set()
    def innner(dtc, confidenceDict, confidence, pace, dtcSet=set()):
        a2o = all2OnePossible(dtc, confidenceDict, confidence)
        for come in a2o.keys():
            newDtcSet.add(come)      
        if len(newDtcSet.difference(dtcSet)) != 0:
            needSet = newDtcSet.difference(dtcSet)
            confidence += pace
            for item in needSet:
                if confidence >= 1:
                    confidence = 1
                innner(item, confidenceDict, confidence, pace, newDtcSet.copy())
        return newDtcSet
    return innner

def findRightLinkSet():
    newDtcSet = set()
    def innner(dtc, confidenceDict, confidence, pace, dtcSet=set()):
        # print(confidence)
        o2a = one2allPossible(dtc, confidenceDict, confidence)
        # print(dtc, o2a)
        for to in o2a.keys():
            newDtcSet.add(to)                              
        if len(newDtcSet.difference(dtcSet)) != 0:
            needSet = newDtcSet.difference(dtcSet)
            confidence += pace
            for item in needSet:
                if confidence >= 1:
                    confidence = 1
                innner(item, confidenceDict, confidence, pace, newDtcSet.copy())
        return newDtcSet
    return innner

def findLinkSet(dtc, confidenceDict, confidence, pace=0, code=0):
    allSet = set()
    leftResult = findLeftLinkSet()(dtc, confidenceDict, confidence, pace)
    rightResult = findRightLinkSet()(dtc, confidenceDict, confidence, pace)
    for i in leftResult:
        allSet.add(i)
    for j in rightResult:
        allSet.add(j)
    allSet.add(dtc)
    if code == 1:
        print(leftResult)
        print(rightResult)
    return allSet

def convergeGraph(graph):
    loops = list(nx.strongly_connected_components(graph))
    # print(loops)
    for item in loops:
        if len(item) >= 1:
            con = list(item)
            for i in range(len(con)):
                for j in range(len(con)):
                    if i != j:
                        if (con[i], con[j]) in graph.edges:
                            graph = nx.contracted_nodes(graph, con[i], con[j], self_loops=False)
    
    first = []
    for degree in graph.in_degree:
        if degree[1]  == 0:
            for loop in loops:
                if degree[0] in loop:
                    first.append(loop)
    return first, graph

def showMainDtcGraph(graphObj, dtcs):
    sub = graphObj.dtc_graph.subgraph(dtcs)
    _, graph = convergeGraph(sub)

    pos = nx.nx_agraph.graphviz_layout(sub, prog="neato")
    nx.draw_networkx(sub, pos=pos, with_labels=True, node_size=3000)
    plt.show()

    pos = nx.nx_agraph.graphviz_layout(graph, prog="neato")
    nx.draw_networkx(graph, pos=pos, with_labels=True, node_size=3000)
    # ax = plt.gca() 
    # ax.set_axis_off()
    plt.show()
    # plt.savefig()

def getMainDtc(graphObj, dtcs):
    sub = graphObj.dtc_graph.subgraph(dtcs)
    first, _ = convergeGraph(sub)
    return first

def countSimi(dtcs, patterns):
    dtcs = frozenset(dtcs)
    simiDict = {}
    for pattern in patterns:
        simi = len(dtcs.intersection(pattern)) / len(dtcs.union(pattern))
        simiDict[pattern] = simi
    print(simiDict)
    ordered = sorted(simiDict.items(), key=lambda x:x[1], reverse=True)
    orderedSimiDict = dict(ordered)
    return orderedSimiDict

def dtcDenoise(originSet, frequentDict):
    okSet = []
    diffSet = []
    for originItem in originSet:
        freUnion = frozenset()
        for frequenItem in frequentDict.keys():
            if frequenItem.issubset(originItem):
                freUnion = freUnion.union(frequenItem)
        okSet.append(freUnion)
        diffSet.append(originItem.difference(freUnion))
    return okSet, diffSet
