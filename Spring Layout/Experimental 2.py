import numpy as np
import time

#this should be a list of all the positions of the nodes in node_list
x = np.array([[2,5,3], [4,5,6], [7,2,0], [3,7,10], [3,5,8], [5,15,3], [3,12,3], [8,6,9], [6,1,9], [3,7,11], [5,7,13]])
natLength = 100
a = x[1]
b = np.delete(x,1,0)
ks = 0.03
kg = 600
#missing exceptions for when distance is zero, should result in net force on one node due to hooke's law
def hookesLaw(a,b,constant):
    difference = b-a
    squared = np.square(difference)
    added = np.sum(squared,axis = 1)
    d3 = np.sqrt(added)
    distance = d3-natLength
    force = constant * distance
    for i in range(np.shape(force)[0]):
        force[i] = force[i]/d3[i]
    #everything below is not correct yet
    forceComp = np.array([0,0,0])
    for j in range(np.shape(force)[0]):
        forceComp = np.vstack([forceComp,[[force[j],force[j],force[j]]]])
    forceComp = np.delete(forceComp, 0,0)
    for k in range(np.shape(forceComp)[0]):
        for m in range(np.shape(forceComp)[1]):
            forceComp[k,m] = difference[k,m] * forceComp[k,m]
    netForce = np.sum(forceComp,axis = 0)
    return netForce #this output is an array that contains netforces from all nodes due to hooke's law on one node in x, y, and z

start_hookes = time.time()
print hookesLaw(a,b,ks)
elapsed_hookes = time.time() - start_hookes
print elapsed_hookes

def coulombsLaw(a,b, range):
    difference = b - a
    squared = np.square(difference)
    added = np.sum(squared, axis=1)
    d3 = np.sqrt(added)
    distance = d3 - natLength
