#!/usr/bin/python
from numpy import *

import re

import helplib as hl

def readfile(filename):

    #create empty list
    a = []
    try:
        f = hl.openfile(filename)
    except IOError:
        raise IOError
        
    #we need to check if a line is actually useful
    num_tab_num = re.compile('^[0-9]+((\.){1}[0-9]+)?\\t[0-9]+((\.){1}[0-9]+)?.*[\\r]?\\n$')

    #read file, skip comment lines
    for line in f:
        #no comments
        if not line.startswith('#'):
            #only number tabulator number
            if num_tab_num.match(line):
                #strip newline and split by tabulator and append to array
                a.append(line.strip('\r\n').split('\t'))

    #convert list a to float array
    data = array(a,dtype = float)

    if len(data) == 0:
        raise IOError('File did not contain any valid lines')

    #close file
    f.close()

    return data

def getelements(identifier):
    # Falls die Dateien mit Monomer und Core Ion nicht existieren, erstellen und
    # mit vorgegebenen Werte füllen
    try:
        if identifier == 0:
            f = open('.\coreion_list.txt','r')
        elif identifier == 1:
            f = open('.\monomer_list.txt','r')
        elements = []
        for line in f:
            elements.append(line.strip('\r\n'))
            # elements[line[0:10]] = float(line[11:])
            # Leerzeichen löschen
            #elements[line[0:10].lstrip()] = float(line[11:])
        f.close
        return elements
    except FileNotFoundError:
        if identifier == 0:
            elements = ["C60 - 720", "C60He - 724.002603", "C60H2O - 738.010565",
                "Ar - 39.962383", "CH4 - 16.031300", "13CH4 - 17.034655",
                "CH5 - 17.039125"]
        elif identifier == 1:
            elements = ["H2 - 2.015650", "H2 - 2.015880", "He - 4.002603",
                "CH4 - 16.031300"]
        #fm = "{0:>10}{1:15.6f}\n"
        #elemente = elements.items()
        # Datei zum Schreiben öffnen
        try:
            if identifier == 0:
                f = open('.\coreion_list.txt','w')
            elif identifier == 1:
                f = open('.\monomer_list.txt','w')
        except IOError:
            raise IOError
        # Elemente schreiben
        for x in elements:
            f.write(x + '\n')
        #for (x,y) in elemente:
        #    f.write(fm.format(x,y))
        # Datei schließen
        f.close()
        return elements
    except IOError:
        raise IOError

def get_daten(data,mass_start,delta):
    mass_unten_index = argmax(nonzero(data[:,0] <= mass_start-delta))
    temp = nonzero(data[:,0] >= mass_start+delta)
    mass_oben_index = temp[0][0]
    #print(mass_unten_index)
    #print(mass_oben_index)
    # Daten im Intervall auswählen und zurückgeben
    x_daten = data[mass_unten_index:mass_oben_index,0]
    y_daten = data[mass_unten_index:mass_oben_index,1]
    return x_daten, y_daten

def get_left_baseline(data,mass_start,delta,bin):
    index_2 = argmax(nonzero(data[:,0] <= mass_start-delta))
    #print(index_2)
    if bin == 1:
        base_y_12 = data[index_2,1]
        x_base_left = data[index_2,0]
        y_base_left = base_y_12
    else:
        index_1 = index_2 - bin + 1
        #print(index_1)
        base_y_12 = data[index_1:index_2,1]
        x_base_left = data[index_1:index_2,0].mean(axis=0)
        y_base_left = base_y_12.min(0)
    #print(x_base_left)
    #print(y_base_left)
    return x_base_left, y_base_left

def get_right_baseline(data,mass_start,delta,bin):
    temp = nonzero(data[:,0] > mass_start+delta)
    index_3 = temp[0][0]
    #print(index_3)
    if bin == 1:
        base_y_34 = data[index_3,1]
        x_base_right = data[index_3,0]
        y_base_right = base_y_34
    else:
        index_4 = index_3 + bin - 1
        #print(index_4)
        base_y_34 = data[index_3:index_4,1]
        x_base_right = data[index_3:index_4,0].mean(axis=0)
        y_base_right = base_y_34.min(0)
    #print(x_base_right)
    #print(y_base_right)
    return x_base_right, y_base_right
    
