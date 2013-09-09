#!/usr/bin/python

import tkinter
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk

import serieslib
#import helplib as hl

import numpy as np
#from numpy import arange, sin, pi
#import scipy.linalg

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

# ----------------------------------------
# Klasse CSPeak mit allen Informationen
# ----------------------------------------
class CSPeak:
    def __init__(self,ci,mo,cs):
        #self.CoreIon = ci
        #self.Monomer = mo
        self.ClusterSize = cs
        self.StartMass = ci + cs * mo
    def getDaten(self):
        self.x_daten, self.y_daten = serieslib.get_daten(data,self.StartMass,
                                                         float(deltamax.wert.get()))
    def findMax(self):
        # Maximum im Ionensignal suchen
        self.y_max,index_y_max = self.y_daten.max(0),self.y_daten.argmax(0)
        self.x_max = self.x_daten[index_y_max]
    def baseline(self):
        #print("Baselinepunkt links")
        self.x_base_l, self.y_base_l = serieslib.get_left_baseline(data,self.StartMass,
                                                         float(deltamin_l.wert.get()),
                                                         float(binmin_l.wert.get()))
        #print("Baselinepunkt rechts")
        self.x_base_r, self.y_base_r = serieslib.get_right_baseline(data,self.StartMass,
                                                          float(deltamin_r.wert.get()),
                                                          float(binmin_r.wert.get()))
        coeff = np.polyfit(np.array([self.x_base_l,self.x_base_r]),
                           np.array([self.y_base_l,self.y_base_r]),1);
        polynom = np.poly1d(coeff)
        self.base_y = polynom(self.x_max)
    def plotDaten(self):
        self.xp_daten, self.yp_daten = serieslib.get_daten(data,self.StartMass,
                                                 float(deltaplot.wert.get()))


# ----------------------------------------
# Class CSParams für die Eingabefelder rechts vom Graphen
# ----------------------------------------
class CSParams:
    def __init__(self,paramname,zeile,startwert,callback):
        self.text = tkinter.Label(frame6, background=bg_color, text=paramname)
        self.text.grid(column=0, row=zeile, sticky="w")
        self.wert = tkinter.StringVar()
        self.edit = tkinter.Entry(frame6, textvariable=self.wert,
                                  justify=tkinter.RIGHT)
        self.edit.insert(0,startwert)
        self.edit.bind("<Return>", callback)
        self.edit.grid(column=1, row=zeile)
    def disable(self):
        self.edit.config(state=tkinter.DISABLED)
    def enable(self):
        self.edit.config(state=tkinter.NORMAL)
        
# ----------------------------------------
# Callbacks
# ----------------------------------------
# Schließen des Fenster
def close():
    print("Window closed")
    mainf.destroy()
# Auswählen des Dateinamens    
def openFileDialog():
    global data
    start_push.config(state=tkinter.DISABLED)
    next_push.config(state=tkinter.DISABLED)
    deltaplot.disable()
    deltamax.disable()
    deltamin_l.disable()
    binmin_l.disable()
    deltamin_r.disable()
    binmin_r.disable()
    fname = filedialog.askopenfilename()
    #print(fname)
    if fname != "":
        data = serieslib.readfile(fname)
        spec_file["text"] = "Current file: " + fname;
    start_push.config(state=tkinter.NORMAL)
    return fname
# Auswählen des Core Ions
def select_ci(event):
    global ci_info
    ci_info = event.widget.get().split(' - ')
    temp = ci_info[1]
    ci_info[1] = float(temp)
# Auswählen des Monomers
def select_mo(event):
    global mo_info
    mo_info = event.widget.get().split(' - ')
    temp = mo_info[1]
    mo_info[1] = float(temp)
# Wert hat sich geändert -> neue Berechnung und Zeichnung
def value_changed(event):
    #if auto_value.get():
    #    print("hier")
    berechne_peak()
def deltaplot_changed(event):
    zeichne_peak()

# ----------------------------------------
# Starten der Hauptroutine
# ----------------------------------------    
def start():
    #saved = 0
    global current_cs
    #global current_si
    global peaks
    current_cs = 0 # Clustersize
    #current_si = 0 # Saveindex
    #output = np.zeros((int(ncl_wert.get()),7))
    peaks = []
    #print("in start vor berechne_peak")
    next_push.config(state=tkinter.NORMAL)
    deltaplot.enable()
    deltamax.enable()
    deltamin_l.enable()
    binmin_l.enable()
    deltamin_r.enable()
    binmin_r.enable()
    berechne_peak()

def berechne_peak():
    global current_peak
    try:
        current_peak = CSPeak(ci_info[1],mo_info[1],current_cs)
    except:
        print("Please choose Core Ion and/or Monomer")
    #print(current_peak)
    current_peak.getDaten()
    current_peak.findMax()
    #print("Baseline")
    current_peak.baseline()
    #output[current_si][0] = current_cs # 1. Spalte... Clustersize
    #output[current_si][1] = current_peak.x_max
    #output[current_si][2] = current_peak.StartMass
    #output[current_si][4] = current_peak.y_max
    #output[current_si][5] = current_peak.base_y
    #print(output[current_si][:])
    #print("in berechne_peak vor zeichne_peak")
    zeichne_peak()

def zeichne_peak():
    #print(deltaplot_wert.get())
    current_peak.plotDaten()
    #print("in zeichne_peak vor plot")
    area.clear()
    area.plot(current_peak.xp_daten, current_peak.yp_daten, color='k')
    #print(current_peak.y_max)
    area.axvline(x=current_peak.x_max, color='r')
    area.set_title(("Cluster Size: " + str(current_cs)))
    # Baseline etc. zeichnen
    area.plot(np.array([current_peak.x_base_l,current_peak.x_base_r]),
              np.array([current_peak.y_base_l,current_peak.y_base_r]),color='b')
    # Plot darstellen
    area.relim()
    area.autoscale_view(True,True,True)
    canvas.draw()
    #print("in zeichne_peak nach plot")

def next_peak():
    global current_cs
    #global current_si
    global peaks
    global current_peak
    #print("in next_peak")
    #print(current_cs)
    current_cs += 1
    #print(current_cs)
    if current_cs < float(ncl_wert.get()):
        peaks.append(current_peak)
        #current_si += 1
        berechne_peak()
    else:
        peaks.append(current_peak)
        print("Speichern")
        f = open('output.txt', 'w')
        for i in range(len(peaks)):
            print(peaks[i].ClusterSize)
            saveformat = '{0:2d}\t{1:15.6f}\t{2:15.6f}\t{3:15.6f}\t{4:15.6f}\t{5:15.6f}\t{6:15.6f}\n'
            f.write(saveformat.format(peaks[i].ClusterSize, peaks[i].x_max,
                                      peaks[i].StartMass, peaks[i].x_max-peaks[i].StartMass,
                                      peaks[i].y_max, peaks[i].base_y,
                                      peaks[i].y_max-peaks[i].base_y))
        f.close()
        

# ----------------------------------------
# Definitionen zur Oberfläche
# ----------------------------------------
bg_color = "#CCCCCC";

#handles.smoothed = 0;
#handles.saved = 0;

# Hauptfenster öffnen
mainf = tkinter.Tk()
mainf.title("Cluster Series v0.1")
mainf.geometry('860x800+20+20')
mainf.protocol('WM_DELETE_WINDOW', close)

coreions = serieslib.getelements(0)
monomers = serieslib.getelements(1)

# Frame1 - Spectrum File und Load File Knopf
# ----------------------------------------
frame1 = tkinter.Frame(mainf, borderwidth=1, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame1.grid(column=0, row=0, columnspan=3, sticky="we")
# Spectrum-File
spec_file = tkinter.Label(frame1, text="no spectrum file open")
spec_file.grid(column=0, row=0, sticky="we")
# Load Button
load_spec = tkinter.Button(frame1, text="Load File", command=openFileDialog)
load_spec.grid(column=1, row=0, sticky="e")
frame1.columnconfigure(0, weight=5)
frame1.columnconfigure(1, weight=1)
# Savitzky-Golay-Filter fehlt noch
# window_size = 5, order = 2, deriv = 0 entspricht den Matlab-Einstellungen
# callback = smooth_spec

# Frame2 - Core Ion
# ----------------------------------------
frame2 = tkinter.Frame(mainf, borderwidth=1, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame2.grid(column=0, row=1)

# Liste mit Coreions
# Beschreibung
ci_text = tkinter.Label(frame2, background=bg_color, text="Core Ion")
ci_text.grid(column=0, row=0, sticky="w")
# Combobox
ci_list = tkinter.StringVar()
ci_combo=ttk.Combobox(frame2, textvariable="ci_list", values=coreions,
    exportselection=0, state="readonly")
ci_combo.bind('<<ComboboxSelected>>', select_ci)
ci_combo.grid(column=0, row=1)
ci_new = tkinter.Button(frame2, text="New Core Ion")
ci_new.grid(column=0, row=2)

# Frame3 - Monomer
# ----------------------------------------
frame3 = tkinter.Frame(mainf, borderwidth=1, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame3.grid(column=1, row=1)

# Liste mit Monomers
# Beschreibung
mo_text = tkinter.Label(frame3, background=bg_color, text="Monomer")
mo_text.grid(column=0, row=0, sticky="w")
# Combobox
mo_list = tkinter.StringVar()
# exportselection=0, ansonsten wird ausgewählter Text in die
# Zwischenablage kopiert
mo_combo=ttk.Combobox(frame3, textvariable="mo_list", values=monomers,
    exportselection=0, state="readonly")
mo_combo.bind('<<ComboboxSelected>>', select_mo)
mo_combo.grid(column=0, row=1)
mo_new = tkinter.Button(frame3, text="New Monomer")
mo_new.grid(column=0, row=2)

# Frame 4 - Number of Clusters
# ----------------------------------------
frame4 = tkinter.Frame(mainf, borderwidth=1, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame4.grid(column=2, row=1, sticky="n")
ncl_text = tkinter.Label(frame4, background=bg_color, text="#Clusters")
ncl_text.grid(column=0, row=0, sticky="w")
ncl_wert = tkinter.StringVar()
ncl_edit = tkinter.Entry(frame4, textvariable=ncl_wert, justify=tkinter.RIGHT)
ncl_edit.insert(0,'100')
ncl_edit.grid(column=0, row=1)

# Frame 5 - Graph mit matplotlib
# ----------------------------------------
peak = Figure(figsize=(6,6), dpi=100)

# a tk.DrawingArea
canvas = FigureCanvasTkAgg(peak, master=mainf)
canvas.show()
canvas.get_tk_widget().grid(column=0, row=2, columnspan=3)

area = peak.add_subplot(111)
area.autoscale(enable=True, axis="both", tight="None")

#a = f.add_subplot(111)
#t = np.arange(0.0,3.0,0.01)
#s = np.sin(2*np.pi*t)
#area.plot(t,s)

#line_cmenu = uicontextmenu;
#uimenu(line_cmenu,'Label','left','Tag','left','Callback',@change_line_rl);
#uimenu(line_cmenu,'Label','right','Tag','right','Callback',@change_line_rl);

# Frame 6 - Details zum Peak Finden
# ----------------------------------------
frame6 = tkinter.Frame(mainf, borderwidth=1, padx=5, pady=5, relief="sunken",
    background=bg_color)
frame6.grid(column=3, row=2, sticky="n")
# Checkbox "automatic"
auto_value = tkinter.IntVar()
auto_check = tkinter.Checkbutton(frame6, text="automatic", variable=auto_value)
auto_check.grid(column=0, row=0, columnspan=2, sticky="nw")
# auto_check["state"] = tkinter.DISABLED
# Start Knopf
start_push = tkinter.Button(frame6, text="Start", command=start, state=tkinter.DISABLED)
start_push.grid(column=0, row=1, columnspan=2, sticky="nw")
# Delta Plot
deltaplot = CSParams("Delta Plot",2,'10',deltaplot_changed)
deltaplot.disable()
# Delta Max
deltamax = CSParams("Delta Max_Peak",3,'0.01',value_changed)
deltamax.disable()
# Delta Min Links
deltamin_l = CSParams("Delta Min_BG left",4,'0.5',value_changed)
deltamin_l.disable()
# Bin Min Links
binmin_l = CSParams("Bins Min_BG left",5,'1',value_changed)
binmin_l.disable()
# Delta Min Rechts
deltamin_r = CSParams("Delta Min_BG right",6,'0.5',value_changed)
deltamin_r.disable()
# Bin Min Rechts
binmin_r = CSParams("Bins Min_BG right",7,'1',value_changed)
binmin_r.disable()
# Next Knopf
next_push = tkinter.Button(frame6, text="Next", command=next_peak, state=tkinter.DISABLED)
next_push.grid(column=0, row=8, columnspan=2, sticky="nw")
#Comments
comment_text = tkinter.Label(frame6, background=bg_color, text="Comment")
comment_text.grid(column=0, row=9, columnspan=2, sticky="w")
comment_edit = scrolledtext.ScrolledText(frame6, width="25")
comment_edit.grid(column=0, row=10, columnspan=2, sticky="s")

# Endlosschleife
mainf.mainloop()

#filename = filedialog.askopenfilename()
#filename = filedialog.asksaveasfilename()
#dirname = filedialog.askdirectory()
