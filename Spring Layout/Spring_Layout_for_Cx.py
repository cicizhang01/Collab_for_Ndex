import math
import random
import json
from ndex.networkn import NdexGraph
import time

# "b":{"id":"b","x":324,"y":530,"z":342,"lock":False,"label":"Banana"}
node_list = {}
#{"source": "0", "target": "1"}
edge_list = []
properties_list = {}
#"true" and "false" are strings
edge_properties = {}

#200
natLength = 200
#0.3
ks = 0.03
#90, 600
kg = 600
#300
maxRepulsion = 300
#500
maxZ = 500
ZDecreaser = 1
#200
iterBegin = 400
#1000 50 and 200
maxLoops = 1000
#EGF, FanGO, FanGO3, Direct
cxFile = 'C-MYB.cx'
#sourceXLock = -500
#targetXLock = 500


# for key, value in d.iteritems():
def categorizing():
    if properties_list.get("node_width"):
        width = float(properties_list["node_width"])
    if not properties_list.get("node_width"):
        width = 60
    range = math.ceil(width * math.sqrt(len(node_list)) * 2.5)
    for node, properties in node_list.iteritems():
        in_count = 0
        out_count = 0
        for edge in edge_list:
            id = edge.get("id")
            if edge_properties.get(id):
                directed = edge_properties.get(id).get("directed")
            else:
                directed = "none"
            if directed == "true":
                if node == edge.get("source"):
                    out_count = out_count + 1
                if node == edge.get("target"):
                    in_count = in_count + 1
        if in_count > 0 and out_count == 0:
            #len(node_list) * 10
            properties["category"] = "Target"
            properties["x"] = range
        elif out_count > 0 and in_count == 0:
            properties["category"] = "Source"
            properties["x"] = -range
        elif in_count > 0 and out_count > 0:
            properties["category"] = "Middle"
        properties["degree"] = in_count + out_count
    print "Range is negative to positive " + str(float(range))
    return range

def loader(file):
    #start_loading = time.time()
    with open(file) as data_file:
        data = json.load(data_file)
    for item in data:
        for key, value in item.items():
            if key == "edges":
                for edge in value:
                    edgeDict = {}
                    edgeDict["source"] = str(edge["s"])
                    edgeDict["target"] = str(edge["t"])
                    edgeDict["id"] = str(edge["@id"])
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
            if key == "cyVisualProperties":
                for properties in value:
                    for name, items in properties.iteritems():
                        if name == "properties":
                            if items.get("NODE_WIDTH"):
                                properties_list["node_width"] = items.get("NODE_WIDTH")
                                print properties_list.get("node_width")
            if key == "edgeAttributes":
                for properties in value:
                    dict = {}
                    if properties.get("n") == "directed":
                        dict["directed"] = properties.get("v")
                        edge_properties[str(properties.get("po"))] = dict


    #elapsed_loading = time.time() - start_loading
    #print elapsed_loading
    return categorizing()

def exportToNetwork(file):
    #start_export = time.time()
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
            node["x"] = prop.get("x")
            node["y"] = prop.get("y")
            listNodes.append(node)

        coords["cartesianLayout"] = listNodes
        data.append(coords)

    G = NdexGraph(data)
    G.upload_to('http://www.ndexbio.org/', 'cc.zhang', 'piggyzhang')
    #elapsed_export = time.time() - start_export
    #print elapsed_export

def move(forceX,forceY,forceZ,node_id,maxZ,startedIter,range):
    maxed = maxZ
    node = node_list.get(node_id)
    xPos = node.get("x")
    yPos = node.get("y")
    zPos = node.get("z")
    newxPos = xPos+forceX
    newyPos = yPos+forceY
    newzPos = zPos+forceZ
    if startedIter:
        if newzPos > maxed:
            newzPos = maxed
        if newzPos < -maxed:
            newzPos = -maxed
    if newyPos > range * 2.5:
        newyPos = range * 2.5
    if newyPos < -range * 2.5:
        newyPos = -range * 2.5
    if newxPos > range * 2.5:
        newxPos = range * 2.5
    if newxPos < -range * 2.5:
        newxPos = -range * 2.5
    node["x"] = newxPos
    node["y"] = newyPos
    node["z"] = newzPos
    #print str(node["x"]) + " and "+ str(node["y"])+ " and " + str(node["z"]) + " in " + node_id

def hookesLaw(a,b,constant):
    xdist = b.get("x")-a.get("x")
    ydist = b.get("y")-a.get("y")
    zdist = b.get("z")-a.get("z")
    d2 = xdist*xdist+ydist*ydist+zdist*zdist
    d3 = math.sqrt(d2)
    distance = d3-natLength
    if d2 == 0:
        return [0,0,0]
    if d2 != 0:
        force = constant*distance/d3
        return [xdist*force, ydist*force,zdist*force ]


def coulombsLaw(a,b, range):
    xdist = b.get("x")-a.get("x")
    ydist = b.get("y")-a.get("y")
    zdist = b.get("z")-a.get("z")
    d2 = xdist*xdist+ydist*ydist+zdist*zdist
    d3 = math.sqrt(d2)
    if d2 == 0 or d3 >= maxRepulsion:
        return [0,0,0]
    if d2 != 0 and d3 < maxRepulsion:
        #if a.get("degree") / 2 < b.get("degree") and a.get("degree") > 5:
            #constant = kg * math.sqrt(a.get("degree"))
        #else:
            #constant = kg
        component = (a.get("degree") + b.get("degree"))/2
        if component > range:
            component = range
        if component < -range:
            component = -range
        constant = component * kg
        force = constant / (d3 * d3)
        return [-force*xdist,-force*ydist,-force*zdist]

def distanceBtw(a,b):
    xdist = b.get("x")-a.get("x")
    ydist = b.get("y")-a.get("y")
    zdist = b.get("z")-a.get("z")
    d2 = xdist*xdist+ydist*ydist+zdist*zdist
    return math.sqrt(d2)

def totalEnergy():
    totalEnergy = 0
    for edge in edge_list:
        totalEnergy = abs(edge.get("length") - natLength) + totalEnergy
    return totalEnergy

def scaleFactoring():
    numNodes = len(node_list)
    springConstant = ks
    if numNodes < 140:
        return springConstant
    if numNodes >= 140:
        factor = springConstant/math.sqrt(numNodes)
        return factor


def loop():
    numLoops = 0
    startedIter = False
    maxed = maxZ
    rangeX = loader(cxFile)
    springConstant = scaleFactoring()
    numHookes = 0
    numCoulombs = 0
    print "Nodes: " + str(len(node_list))
    print "Edges: " + str(len(edge_list))
    start_loop = time.time()
    for length in range(maxLoops):
        if numLoops > iterBegin:
            startedIter = True
        for node1, properties1 in node_list.iteritems():
            netForceX = 0
            netForceY = 0
            netForceZ = 0
            if properties1.get("lock") == False:
                for node2, properties2 in node_list.iteritems():
                    if node1 != node2:
                        start_coulomb = time.time()
                        forceCArray = coulombsLaw(properties1, properties2, rangeX)
                        addedXCForce = forceCArray[0]
                        addedYCForce = forceCArray[1]
                        addedZCForce = forceCArray[2]
                        netForceX = netForceX + addedXCForce
                        netForceY = netForceY + addedYCForce
                        netForceZ = netForceZ + addedZCForce
                        numCoulombs = numCoulombs + 1
                        elapsed_coulomb = time.time() - start_coulomb
                        #print elapsed_coulomb
                for edge in edge_list:
                    start_hookes = time.time()
                    if node1 == edge.get("source"):
                        for search, prop in node_list.iteritems():
                            if edge.get("target") == search:
                                forceHArray = hookesLaw(properties1, prop, springConstant)
                                addedXHForce = forceHArray[0]
                                addedYHForce = forceHArray[1]
                                addedZHForce = forceHArray[2]
                                netForceX = netForceX + addedXHForce
                                netForceY = netForceY + addedYHForce
                                netForceZ = netForceZ + addedZHForce
                                edge["length"] = distanceBtw(properties1, prop)
                                numHookes = numHookes + 1
                                elapsed_hookes = time.time() - start_hookes
                                #print elapsed_hookes
                    if node1 == edge.get("target"):
                        for search, prop in node_list.iteritems():
                            if edge.get("source") == search:
                                forceHArray = hookesLaw(properties1, prop, springConstant)
                                addedXHForce = forceHArray[0]
                                addedYHForce = forceHArray[1]
                                addedZHForce = forceHArray[2]
                                netForceX = netForceX + addedXHForce
                                netForceY = netForceY + addedYHForce
                                netForceZ = netForceZ + addedZHForce
                                edge["length"] = distanceBtw(properties1, prop)
                                numHookes = numHookes + 1
                                elapsed_hookes = time.time() - start_hookes
                                #print elapsed_hookes
                                #print forceHArray
            #print str(netForceX) + " and "+ str(netForceY)+ " and " + str(netForceZ) + " in " + node1
            if properties1.get("category") == "Source" or properties1.get("category") == "Target":
                netForceX = 0
            move(netForceX, netForceY, netForceZ, node1, maxed, startedIter,rangeX)
            numLoops = numLoops + 1
        if startedIter and maxed != 0:
            maxed = maxed - ZDecreaser
    elapsed_loop = time.time() - start_loop
    print elapsed_loop
    print "Hookes calls: " + str(numHookes)
    print "Coulomb calls: " + str(numCoulombs)

        #print node_list

#loader(cxFile)
#categorizing()
#print edge_list
#print node_list
loop()
exportToNetwork(cxFile)
