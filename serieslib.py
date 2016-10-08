import numpy as np
import json
import os

def readElements(iniData):
    # Falls die Dateien mit Monomer und Core Ion nicht existieren, werden leere
    # Listen zurückgegeben
    coreIonFile = iniData['Paths'].get('coreIon')
    monomerFile = iniData['Paths'].get('monomer')
    try:
        f = open(coreIonFile,'r')
        coreions = json.load(f)
        f.close()
    except:
        coreions = []
    try:
        f = open(monomerFile,'r')
        monomers = json.load(f)
        f.close()
    except:
        monomers = []
    return coreions, monomers
    
def writeElements(iniData, coreions, monomers):
    # Speichern der Core Ions und Monomers
    coreIonFile = iniData['Paths'].get('coreIon')
    monomerFile = iniData['Paths'].get('monomer')
    try:
        f = open(coreIonFile,'w')
        json.dump(coreions,f)
        f.close()
    except IOError:
        raise IOError
    try:
        f = open(monomerFile,'w')
        json.dump(monomers,f)
        f.close()
    except IOError:
        raise IOError

def get_daten(data,mass_start,delta):
    mass_unten_index = np.argmax(np.nonzero(data[:,0] <= mass_start-delta))
    temp = np.nonzero(data[:,0] >= mass_start+delta)
    mass_oben_index = temp[0][0]
    #print(mass_unten_index)
    #print(mass_oben_index)
    # Daten im Intervall auswählen und zurückgeben
    x_daten = data[mass_unten_index:mass_oben_index,0]
    y_daten = data[mass_unten_index:mass_oben_index,1]
    return x_daten, y_daten

def get_left_baseline(data,mass_start,delta,bins):
    index_2 = np.argmax(np.nonzero(data[:,0] <= mass_start-delta))
    #print(index_2)
    if bins == 1:
        base_y_12 = data[index_2,1]
        x_base_left = data[index_2,0]
        y_base_left = base_y_12
    else:
        index_1 = index_2 - bins + 1
        #print(index_1)
        base_y_12 = data[index_1:index_2,1]
        x_base_left = data[index_1:index_2,0].mean(axis=0)
        y_base_left = base_y_12.min(0)
    #print(x_base_left)
    #print(y_base_left)
    return x_base_left, y_base_left

def get_right_baseline(data,mass_start,delta,bins):
    temp = np.nonzero(data[:,0] > mass_start+delta)
    index_3 = temp[0][0]
    #print(index_3)
    if bins == 1:
        base_y_34 = data[index_3,1]
        x_base_right = data[index_3,0]
        y_base_right = base_y_34
    else:
        index_4 = index_3 + bins - 1
        #print(index_4)
        base_y_34 = data[index_3:index_4,1]
        x_base_right = np.mean(data[index_3:index_4,0],axis=0)
        y_base_right = base_y_34.min(0)
    #print(x_base_right)
    #print(y_base_right)
    return x_base_right, y_base_right
    
def get_area(data,mass_start,left_point,right_point):
    index_l = np.argmax(np.nonzero(data[:,0] <= left_point))
    temp = np.nonzero(data[:,0] > right_point)
    index_r = temp[0][0]
    x = data[index_l:index_r,0]
    y = data[index_l:index_r,1]
    area = np.sum(y)
    anzahl = index_r-index_l
    return area, anzahl

def get_closest_index(data,x):
    idx = (np.abs(data-x)).argmin()
    return idx
    
