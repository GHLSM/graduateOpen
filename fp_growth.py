from collections import Counter
from .graph_theory import DtcGraph
from configs.config import CHECKED_DATA, POSSIBLEXCEL
import csv
import os
import pandas as pd
import networkx as nx
from .graph_theory import DtcGraph

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

    def update(self, count):
        self.count += count
        self._moreData()

    def _moreData(self):
        self.possible2all = self.count / self.allCount
        if self.father.count != None:
            if self.father.count != 0:
                self.possible2father = self.count / self.father.count

class FpTree:
    def __init__(self, Identify, minSupportRate, minSupport=0, suffix=set(), frequentItemDict={}) -> None:
        self.Identify = Identify
        self.minSupportRate = minSupportRate
        self.minSupport = minSupport
        self.orderItem = []
        self.headerTable = {}
        self.RawHeader = {}
        self.allItemCount = {}
        self.changeCount = 0
        self.root = Node("root", None, None, None)
        self.updateItem = []
        self.suffix = suffix
        self.frequentItemDict = frequentItemDict

    def _clearSelf(self):
        self.orderItem = []
        self.headerTable = {}
        self.RawHeader = {}
        self.allItemCount = {}
        self.frequentItemDict = {}

    def clearFrequent(self):
        self.suffix = set()
        self.frequentItemDict = {}

    def _isOrderItemChange(self, newData):
        self.updateItem = []
        dataDict = dict(Counter(newData))
        newMinSupport = len(newData) * self.minSupportRate + self.minSupport
        newItemSet = frozenset([item for transaction in dataDict for item in transaction])
        for item in newItemSet:
            supportCount = 0
            for transaction in dataDict:
                if item in transaction:
                    supportCount += dataDict[transaction]
            supportCount += self.allItemCount.get(item, 0)
            self.allItemCount[item] = supportCount
            if supportCount >= newMinSupport:
                # 如果在老header表中找不到，则说明orderitem有新值，已改变
                if self.RawHeader.get(item, 0) == 0:
                    return True
                self.updateItem.append(item)
                self.RawHeader[item] = supportCount

        # 更新完支持度和header Count之后，看一下以前是否有部分item现在不满足最小支持度的
        for i in self.RawHeader:
            if self.RawHeader[i] < newMinSupport:
                return True

        newOrderItem = [itemSupport[0] for itemSupport in sorted(self.RawHeader.items(), key=lambda x: (x[1], x[0]), reverse=True)]
        if newOrderItem == self.orderItem:
            return False
        else:
            return True

    def _constructHeaderTable(self, dataDict):
        itemSet = frozenset([item for transaction in dataDict for item in transaction])
        for item in itemSet:
            supportCount = 0
            for transaction in dataDict:
                if item in transaction:
                    supportCount += dataDict[transaction]
            # 记录所有item的支持度，供数据更新
            self.allItemCount[item] = supportCount
            if supportCount >= self.minSupport:
                self.RawHeader[item] = supportCount
                self.headerTable[item] = supportCount

        '''引入一个排序列表，排序按值的降序进行，当值相同时则按键的字典序'''
        self.orderItem = [itemSupport[0] for itemSupport in sorted(self.headerTable.items(), key=lambda x: (x[1], x[0]), reverse=True)]
        for item in self.headerTable:
            self.headerTable[item] = [self.headerTable[item], None]

    def _constructTree(self, dataDict):
        for transaction in dataDict:
            fatherNode = self.root             
            for item in self.orderItem:
                if item in transaction:
                    count = dataDict[transaction]
                    fatherNode = self._constructing(item, fatherNode, count)

    def _constructing(self, item, fatherNode, count):
        if item not in fatherNode.children:
            newNode = Node(item, fatherNode, self.headerTable[item][0], count)
            fatherNode.children[item] = newNode
            '''更新同名项链表'''
            linkNode = self.headerTable[item][1]
            if linkNode == None:
                self.headerTable[item][1] = newNode
            else:
                while linkNode.sameNodeLink != None:
                    linkNode = linkNode.sameNodeLink
                linkNode.sameNodeLink = newNode
        else:
            fatherNode.children[item].update(count)
        return fatherNode.children[item]

    def needBigUpdate(self, newData):
        return self._isOrderItemChange(newData)

    def littleUpdate(self, newData):
        for item in self.updateItem:
            # 更新一条链路上的所有allCount
            self.headerTable[item] = [self.RawHeader[item], self.headerTable[item][1]]
            headerNode = self.headerTable[item][1]
            while headerNode != None:
                headerNode.allCount = self.RawHeader[item]
                headerNode.update(0)
                headerNode = headerNode.sameNodeLink
        dataDict = dict(Counter(newData))
        self._constructTree(dataDict)
    
    def bigUpdate(self, data):
        self.initFp(data)

    def initFp(self, data):
        self._clearSelf()
        if not isinstance(data, dict):
            dataDict = dict(Counter(data))
            self.minSupport = len(data) * self.minSupportRate
        else:
            self.minSupport = sum(data.values()) * self.minSupportRate
            dataDict = data
        self._constructHeaderTable(dataDict)
        self._constructTree(dataDict)
    
    def _recur(self, dataDict):
        # recursion时，保持最小支持度不变，和init Fp还是有区别的
        self._constructHeaderTable(dataDict)
        self._constructTree(dataDict)

    def findFrequentItem(self):
        for item in reversed(self.orderItem):
            newItem = self.suffix.copy()
            newItem.add(item)
            self.frequentItemDict[frozenset(newItem)] = self.frequentItemDict.get(frozenset(newItem),0) + self.headerTable[item][0]
            cpBase = self._trace(item)
            cpTree = FpTree(self.Identify, self.minSupportRate, self.minSupport, newItem, self.frequentItemDict)
            cpTree._recur(cpBase)
            if cpTree.headerTable != None:
                cpTree.findFrequentItem()
        
    def _trace(self, item):
        cpBase = {}
        headNode = self.headerTable[item][1]
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

class FpTreeWithGraph(FpTree):
    def __init__(self, carType, minSupportRate, data, allDcts=None, edgeConfidence=0.8) -> None:
        super().__init__(carType, minSupportRate)
        super().initFp(data)
        self.edgeConfidence = edgeConfidence
        self.dtcGraphObj = DtcGraph(carType)
        self.confidenceDict, edges = self._findLink()
        self.dtcGraphObj.add_nodes(allDcts)
        self.dtcGraphObj.add_edges(edges)
        self.subGraph = None

    def updateGraph(self):
        pass
        
    def _findLink(self):
        confidenceDict = {}
        edges = []
        for item in reversed(self.orderItem):
            headNode = self.headerTable[item][1]
            while headNode != None:
                leafNode = headNode
                while leafNode.father.father != None:
                    # 如果表中已有，则相加dtc链接可能性
                    confidenceDict[(leafNode.father.name, headNode.name)] = \
                        confidenceDict.get((leafNode.father.name, headNode.name), 0) + \
                            (headNode.count / leafNode.father.count) * leafNode.father.possible2all
                    confidenceDict[(headNode.name, leafNode.father.name)] = \
                        confidenceDict.get((headNode.name, leafNode.father.name), 0) + \
                            headNode.possible2all
                    leafNode = leafNode.father
                headNode = headNode.sameNodeLink
        for edge in confidenceDict:
            # 支持度判定
            # a,b = edge
            if confidenceDict[edge] >= self.edgeConfidence:
                # 添加相关性判定、使用Kulczynski进行关联度判定，考虑是否添加IR偏度计算？
                # Kulczynski = (1 / 2) * (confidenceDict[edge] + confidenceDict.get((b,a)))
                # if Kulczynski >= 0.5:
                edges.append(edge)
        return confidenceDict, edges

    def _formatSubGraph(self, dtcs):
        self.subGraph = self.dtcGraphObj.dtc_graph.subgraph(dtcs)

    def getMainDtc(self, dtcs):
        self._formatSubGraph(dtcs)
        first, _ = self._convergeGraph()
        return first

    def _convergeGraph(self):
        graph = self.subGraph
        loops = list(nx.strongly_connected_components(graph))
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
            if degree[1] == 0:
                for loop in loops:
                    if degree[0] in loop:
                        first.append(loop)
        return first, graph

    def findLinkSet(self, dtc, confidence, pace=0):
        allSet = set()
        leftResult = findLeftLinkSet()(dtc, self.confidenceDict, confidence, pace)
        rightResult = findRightLinkSet()(dtc, self.confidenceDict, confidence, pace)
        for i in leftResult:
            allSet.add(i)
        for j in rightResult:
            allSet.add(j)
        allSet.add(dtc)
        return allSet

def createCSVFile(fName, dataSet):
    fileRoute = os.path.join(CHECKED_DATA, fName)
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

# def showMainDtcGraph(graphObj, dtcs):
#     sub = graphObj.dtc_graph.subgraph(dtcs)
#     _, graph = convergeGraph(sub)
#     # print(first)
#     nx.draw_networkx(graph, with_labels=True)
#     ax = plt.gca()
#     ax.set_axis_off()
#     plt.show()

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


