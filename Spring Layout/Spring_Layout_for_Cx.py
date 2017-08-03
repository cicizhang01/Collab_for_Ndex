import math
import random
import json
from ndex.networkn import NdexGraph

# "b":{"id":"b","x":324,"y":530,"z":342,"lock":False,"label":"Banana"}
node_list = {}
#{"source": "0", "target": "1"}
edge_list = []

#200
natLength = 30
#0.3
ks = 0.5
#90
kg = 90
#300
maxRepulsion = 700
#500
maxZ = 700
ZDecreaser = 5
iterBegin = 200
maxLoops = 1000
cxFile = 'Visual.cx'


# for key, value in d.iteritems():

def loader(file):
    with open(file) as data_file:
        data = json.load(data_file)
    for item in data:
        for key, value in item.items():
            if key == "edges":
                for edge in value:
                    edgeDict = {}
                    edgeDict["source"] = edge["s"]
                    edgeDict["target"] = edge["t"]
                    edge_list.append(edgeDict)
            if key == "nodes":
                for node in value:
                    nodeProperties = {}
                    nodeProperties["id"] = node.get("n")
                    nodeProperties["x"] = random.randint(1,maxZ)
                    nodeProperties["y"] = random.randint(1,maxZ)
                    nodeProperties["z"] = random.randint(1,maxZ)
                    nodeProperties["lock"] = False
                    node_list[str(node.get("@id"))] = nodeProperties

def exportToNetwork(file):
    exists = False
    with open(file) as data_file:
        data = json.load(data_file)
    for item in data:
        if item.get("cartesianLayout"):
            for node in item["cartesianLayout"]:
                #print node
                id = str(node.get("node"))
                node["x"] = node_list[id]["x"]
                node["y"] = node_list[id]["y"]
            print True
            exists = True


    if not exists:
        print False
        coords = {}
        listNodes = []
        for name, prop in node_list.iteritems():
            node = {}
            node["node"] = name
            node["x"] = prop["x"]
            node["y"] = prop["y"]
            listNodes.append(node)

        coords["cartesianLayout"] = listNodes
        data.append(coords)

    G = NdexGraph(data)
    G.upload_to('http://www.ndexbio.org/', 'cc.zhang', 'piggyzhang')





def move(forceX,forceY,forceZ,node_id,maxZ,startedIter):
    maxed = maxZ
    node = node_list[node_id]
    xPos = node["x"]
    yPos = node["y"]
    zPos = node["z"]
    newxPos = xPos+forceX
    newyPos = yPos+forceY
    newzPos = zPos+forceZ
    if startedIter:
        if newzPos > maxed:
            newzPos = maxed
        if newzPos < -maxed:
            newzPos = -maxed
    node["x"] = newxPos
    node["y"] = newyPos
    node["z"] = newzPos


def hookesLaw(a,b):
    xdist = b["x"]-a["x"]
    ydist = b["y"]-a["y"]
    zdist = b["z"]-a["z"]
    d3 = xdist*xdist+ydist*ydist+zdist*zdist
    d3 = math.sqrt(d3)
    distance = d3-natLength
    if d3 == 0:
        return [0,0,0]
    if d3 != 0:
        force = ks*distance/d3
    return [xdist*force, ydist*force,zdist*force ]

def coulombsLaw(a,b):
    xdist = b["x"]-a["x"]
    ydist = b["y"]-a["y"]
    zdist = b["z"]-a["z"]
    d3 = xdist*xdist+ydist*ydist+zdist*zdist
    d3 = math.sqrt(d3)
    if d3 == 0 or d3 > maxRepulsion:
        return [0,0,0]
    if d3 != 0 and d3 < maxRepulsion:
        force = kg/(d3*d3)
    return [-force*xdist,-force*ydist,-force*zdist]


def loop():
    numLoops = 0
    startedIter = False
    maxed = maxZ
    loader(cxFile)
    while True:
        if numLoops > iterBegin:
            startedIter = True
        for node1, properties1 in node_list.iteritems():
            netForceX = 0
            netForceY = 0
            netForceZ = 0
            if properties1["lock"] == False:
                for node2, properties2 in node_list.iteritems():
                    if node1 != node2:
                        addedXCForce = coulombsLaw(properties1, properties2)[0]
                        addedYCForce = coulombsLaw(properties1, properties2)[1]
                        addedZCForce = coulombsLaw(properties1, properties2)[2]
                        netForceX = netForceX + addedXCForce
                        netForceY = netForceY + addedYCForce
                        netForceZ = netForceZ + addedZCForce
                for edge in edge_list:
                    if node1 == edge["source"]:
                        for search, prop in node_list.iteritems():
                            if edge["target"] == search:
                                addedXHForce = hookesLaw(properties1, prop)[0]
                                addedYHForce = hookesLaw(properties1, prop)[1]
                                addedZHForce = hookesLaw(properties1, prop)[2]
                                netForceX = netForceX + addedXHForce
                                netForceY = netForceY + addedYHForce
                                netForceZ = netForceZ + addedZHForce
                    if node1 == edge["target"]:
                        for search, prop in node_list.iteritems():
                            if edge["source"] == search:
                                addedXHForce = hookesLaw(properties1, prop)[0]
                                addedYHForce = hookesLaw(properties1, prop)[1]
                                addedZHForce = hookesLaw(properties1, prop)[2]
                                netForceX = netForceX + addedXHForce
                                netForceY = netForceY + addedYHForce
                                netForceZ = netForceZ + addedZHForce

            move(netForceX, netForceY, netForceZ, node1, maxed, startedIter)
        if startedIter and maxed != 0:
            maxed = maxed - ZDecreaser
        if maxLoops > 0 and numLoops > maxLoops:
            break
        numLoops = numLoops + 1


loop()
exportToNetwork(cxFile)
