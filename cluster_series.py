#!/usr/bin/python

import tkinter
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import ttk

import os
import serieslib
import helplib as hl

import numpy as np

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

# ----------------------------------------
# Klasse CSPeak mit allen Informationen
# ----------------------------------------
class CSPeak:
    def __init__(self,ci,mo,cs):
        self.CoreIon = ci
        self.Monomer = mo
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
    def basepoint(self):
        coeff = np.polyfit(np.array([self.x_base_l,self.x_base_r]),
                           np.array([self.y_base_l,self.y_base_r]),1);
        polynom = np.poly1d(coeff)
        self.base_y = polynom(self.x_max)
    def plotDaten(self):
        self.xp_daten, self.yp_daten = serieslib.get_daten(data,self.StartMass,
                                                 float(deltaplot.wert.get()))
    def area(self):
        #Peakwerte
        area, anzahl = serieslib.get_area(data,self.StartMass,self.x_base_l,self.x_base_r)
        self.area_corr = area - anzahl * np.mean(np.array([self.y_base_l,self.y_base_r]))

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
# Class CSBaseline - Linie mit verschiebarene Endpunkten
# ----------------------------------------
class CSBaseline:
    def __init__(self,line):
        self.line = line
        self.press = None

    def connect(self):
        self.cidpress = self.line.figure.canvas.mpl_connect(
            'button_press_event', self.click_baseline)
        self.cidrelease = self.line.figure.canvas.mpl_connect(
            'button_release_event', self.release_baseline)
        self.cidmove = self.line.figure.canvas.mpl_connect(
            'motion_notify_event', self.move_baseline)
        self.cidpick = self.line.figure.canvas.mpl_connect(
            'pick_event', self.onpick_baseline)

    def onpick_baseline(self,event):
        if isinstance(event.artist, Line2D):
            thisline = event.artist
            self.xdata = thisline.get_xdata()
            self.ydata = thisline.get_ydata()
            self.index = event.ind[0]
            self.x_old = np.take(self.xdata,event.ind)
            self.y_old = np.take(self.ydata,event.ind)
            #print("index:", self.index)
            #print('xdata:',self.x_old)
            #print('ydata:',self.y_old)
        
    def click_baseline(self,event):
        #print('button_click=', event.button, 'x=', event.x, 'y=', event.y,
        #      'xdata=', event.xdata, 'ydata=', event.ydata)
        contains, attrd = self.line.contains(event)
        #print(contains)
        if not contains: return
        #print(attrd)
        self.press = True
    def move_baseline(self,event):
        if self.press is None: return
        #print('button_move=', event.button, 'x=', event.x, 'y=', event.y,
        #      'xdata=', event.xdata, 'ydata=', event.ydata)
        self.new_x = self.xdata
        self.new_x[self.index] = event.xdata
        self.new_y = self.ydata
        self.new_y[self.index] = event.ydata
        #print("x neu", new_x)
        #print("y neu", new_y)
        self.line.set_xdata(self.new_x)
        self.line.set_ydata(self.new_y)
        self.line.figure.canvas.draw()
    def release_baseline(self,event):
        if self.press is None: return
        #print('button_release=', event.button, 'x=', event.x, 'y=', event.y,
        #      'xdata=', event.xdata, 'ydata=', event.ydata)
        self.press = None
        self.new_x = self.xdata
        self.new_x[self.index] = event.xdata
        self.new_y = self.ydata
        self.new_y[self.index] = event.ydata
        self.line.set_xdata(self.new_x)
        self.line.set_ydata(self.new_y)
        # Background-Punkt am Maximum berechnen
        current_peak.x_base_l = self.new_x[0]
        current_peak.x_base_r = self.new_x[1]
        current_peak.y_base_l = self.new_y[0]
        current_peak.y_base_r = self.new_y[1]
        current_peak.basepoint()
        g_base.set_ydata(current_peak.base_y)
        g_base.figure.canvas.draw()
        self.line.figure.canvas.draw()
        
# ----------------------------------------
# Callbacks
# ----------------------------------------
# Schließen des Fenster
def close():
    print("Window closed")
    mainf.destroy()
# Abbruch im Automatic-Mode
def cancel_auto():
    print("Automatic evaluation cancelled")
    active_stat.set(False)
# Auswählen des Dateinamens    
def openFileDialog():
    global data
    global fname
    fname = ""
    start_push.config(state=tkinter.DISABLED)
    next_push.config(state=tkinter.DISABLED)
    save_push.config(state=tkinter.DISABLED)
    deltaplot.disable()
    deltamax.disable()
    deltamin_l.disable()
    binmin_l.disable()
    deltamin_r.disable()
    binmin_r.disable()
    fname = filedialog.askopenfilename()
    #print(fname)
    if fname != "":
        data = hl.readfile(fname)
        spec_file["text"] = "Current file: " + fname;
    start_push.config(state=tkinter.NORMAL)
    deltaplot.enable()
    deltamax.enable()
    deltamin_l.enable()
    binmin_l.enable()
    deltamin_r.enable()
    binmin_r.enable()
    #return fname
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
# Neues Core Ion
def newCoreIon():
    name_ci = tkinter.simpledialog.askstring(
    "Enter new Core Ion", "Enter name of Core Ion")
    #print(name_ci)
    mass_ci = tkinter.simpledialog.askstring(
    "Enter new Core Ion", "Enter mass of Core Ion")
    #print(mass_ci)
    #print(name_ci, '-', mass_ci)
    coreions.append('{0} - {1}'.format(name_ci, mass_ci))
    #print(coreions)
    #print(ci_list.get().strip())
    ci_combo["values"] = coreions
    try:
        f = open('.\coreion_list.txt','w')
    except IOError:
        raise IOError
    # Elemente schreiben
    for x in coreions:
        f.write(x + '\n')
    # Datei schließen
    f.close()
def newMonomer():
    name_mo = tkinter.simpledialog.askstring(
    "Enter new Monomer", "Enter name of Monomer")
    mass_mo = tkinter.simpledialog.askstring(
    "Enter new Monomer", "Enter mass of Monomer")
    monomers.append('{0} - {1}'.format(name_mo, mass_mo))
    mo_combo["values"] = monomers
    try:
        f = open('.\monomer_list.txt','w')
    except IOError:
        raise IOError
    # Elemente schreiben
    for x in monomers:
        f.write(x + '\n')
    # Datei schließen
    f.close()
    
# Wert hat sich geändert -> neue Berechnung und Zeichnung
def value_changed(event):
    #if auto_value.get():
    #print("in value_changed")
    berechne_peak()
def deltaplot_changed(event):
    zeichne_peak()
# ----------------------------------------
# Starten der Hauptroutine
# ----------------------------------------    
def start():
    global current_cs
    global peaks
    global current_peak
    current_cs = 0 # Clustersize
    peaks = []
    if auto_value.get():
        auto_check.config(background='#f00')
        next_push.config(state=tkinter.DISABLED)
        cancel_push.config(state=tkinter.NORMAL)
        deltaplot.disable()
        deltamax.disable()
        deltamin_l.disable()
        binmin_l.disable()
        deltamin_r.disable()
        binmin_r.disable()
        progress_bar["value"] = 0
        active_stat.set(True)
        cs = int(ncl_wert.get())
        while active_stat.get():
            progress_bar["value"] = current_cs/cs*100
            berechne_peak()
            # Fläche berechnen
            current_peak.area()
            peaks.append(current_peak)
            if current_cs < cs:            
                current_cs += 1
            else:
                active_stat.set(False)
            mainf.update()
        save_push.config(state=tkinter.NORMAL)
        cancel_push.config(state=tkinter.DISABLED)
    else:
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
    current_peak.basepoint()
    #print("in berechne_peak vor zeichne_peak")
    zeichne_peak()

def zeichne_peak():
    #global b_line
    global baseline
    global g_base
    #print(deltaplot_wert.get())
    current_peak.plotDaten()
    #print("in zeichne_peak vor plot")
    area.clear()
    area.plot(current_peak.xp_daten, current_peak.yp_daten, color='k')
    area.axvline(x=current_peak.StartMass, color='r')
    #print(current_peak.y_max)
    g_base, = area.plot(np.array([current_peak.x_max,current_peak.x_max]),
                             np.array([current_peak.base_y,current_peak.y_max]),
                             color='g', marker='x', linestyle='None')
    area.set_title(("Cluster Size: " + str(current_cs)))
    
    # Baseline zeichnen
    b_line, = area.plot(np.array([current_peak.x_base_l,current_peak.x_base_r]),
                        np.array([current_peak.y_base_l,current_peak.y_base_r]),
                        color='b',marker='d',picker=5)
    baseline = CSBaseline(b_line)
    baseline.connect()
    
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
    current_cs += 1
    if current_cs < float(ncl_wert.get()):
        # Fläche berechnen
        current_peak.area()
        peaks.append(current_peak)
        save_push.config(state=tkinter.NORMAL)
        berechne_peak()
    else:
        # Fläche berechnen
        current_peak.area()
        peaks.append(current_peak)
        berechne_peak()
        next_push.config(state=tkinter.DISABLED)

def save_data():
    if auto_value.get() == 0:
        current_peak.area()
        peaks.append(current_peak)
    print("Speichern")
    # Dateinamen erstellen
    # spec.ext -> spec_coreion_monomer.ext
    fileName, fileExtension = os.path.splitext(fname)
    # Falls keine Extension -> .dat anfügen
    if not fileExtension:
        #fname += '.dat'
        fileExtension = '.dat'
    #print(fileName + '_' + ci_info[0] + '_' + mo_info[0] + fileExtension)
    f = open(fileName + '_' + ci_info[0] + '_' + mo_info[0] + fileExtension, 'w')
    #f = open('output.txt', 'w')
    if auto_value.get():
        f.write('# Mode: automatic\n')
    else:
        f.write('# Mode: interactive\n')
    f.write('# Settings:\n')
    saveformat = '# Core Ion: {0:f}; Monomer: {1:f}\n'
    f.write(saveformat.format(current_peak.CoreIon, current_peak.Monomer))
    f.write('# Comments:\n')
    f.write('# {}'.format(comment_edit.get('1.0','end').replace('\n', '\n# ')))
    f.write('Cluster Size; x-Maximum; x-StartMass; x-Diff; y-Maximum; y-Base; y-Diff; Area_Corr\n')
    for i in range(len(peaks)):
        #print(peaks[i].ClusterSize)
        saveformat = '{0:2d}\t{1:15.6f}\t{2:15.6f}\t{3:15.6f}\t{4:15.6f}\t{5:15.6f}\t{6:15.6f}\t{7:15.6f}\n'
        f.write(saveformat.format(peaks[i].ClusterSize, peaks[i].x_max,
                                  peaks[i].StartMass, peaks[i].x_max-peaks[i].StartMass,
                                  peaks[i].y_max, peaks[i].base_y,
                                  peaks[i].y_max-peaks[i].base_y,peaks[i].area_corr))
    f.close()
    #save_push.config(state=tkinter.DISABLED)  

# ----------------------------------------
# Definitionen zur Oberfläche
# ----------------------------------------
bg_color = "#CCCCCC";

#handles.smoothed = 0;

# Hauptfenster öffnen
mainf = tkinter.Tk()
mainf.title("Cluster Series v1.5")
mainf.geometry('860x800+20+20')
mainf.protocol('WM_DELETE_WINDOW', close)
mainf.configure(background=bg_color)

coreions = serieslib.getelements(0)
monomers = serieslib.getelements(1)

# Frame1 - Spectrum File und Load File Knopf
# ----------------------------------------
frame1 = tkinter.Frame(mainf, borderwidth=0, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame1.grid(column=0, row=0, columnspan=4, sticky="we")
# Spectrum-File
spec_file = tkinter.Label(frame1, text="no spectrum file open")
spec_file.grid(column=0, row=0, sticky="we")
# Load Button
load_spec = tkinter.Button(frame1, text="Load File", command=openFileDialog, background=bg_color)
load_spec.grid(column=1, row=0, sticky="we")
frame1.columnconfigure(0, weight=7)
frame1.columnconfigure(1, weight=1)
# Savitzky-Golay-Filter fehlt noch
# window_size = 5, order = 2, deriv = 0 entspricht den Matlab-Einstellungen
# callback = smooth_spec

# Frame2 - Core Ion
# ----------------------------------------
frame2 = tkinter.Frame(mainf, borderwidth=0, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame2.grid(column=0, row=1)

# Liste mit Coreions
# Beschreibung
ci_text = tkinter.Label(frame2, background=bg_color, text="Core Ion")
ci_text.grid(column=0, row=0, sticky="we")
# Combobox
#ci_list = tkinter.StringVar()
#ci_combo=ttk.Combobox(frame2, textvariable="ci_list", values=coreions,
#    exportselection=0, state="readonly")
ci_combo=ttk.Combobox(frame2, values=coreions,
    exportselection=0, state="readonly")
ci_combo.bind('<<ComboboxSelected>>', select_ci)
ci_combo.grid(column=0, row=1)
ci_new = tkinter.Button(frame2, text="New Core Ion", background=bg_color, command=newCoreIon)
ci_new.grid(column=0, row=2)

# Frame3 - Monomer
# ----------------------------------------
frame3 = tkinter.Frame(mainf, borderwidth=0, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame3.grid(column=1, row=1)

# Liste mit Monomers
# Beschreibung
mo_text = tkinter.Label(frame3, background=bg_color, text="Monomer")
mo_text.grid(column=0, row=0, sticky="we")
# Combobox
mo_list = tkinter.StringVar()
# exportselection=0, ansonsten wird ausgewählter Text in die
# Zwischenablage kopiert
mo_combo=ttk.Combobox(frame3, textvariable="mo_list", values=monomers,
    exportselection=0, state="readonly")
mo_combo.bind('<<ComboboxSelected>>', select_mo)
mo_combo.grid(column=0, row=1)
mo_new = tkinter.Button(frame3, text="New Monomer", background=bg_color, command=newMonomer)
mo_new.grid(column=0, row=2)

# Frame 4 - Number of Clusters
# ----------------------------------------
frame4 = tkinter.Frame(mainf, borderwidth=0, padx=2, pady=2, relief="sunken",
    background=bg_color)
frame4.grid(column=2, row=1, sticky="n")
ncl_text = tkinter.Label(frame4, background=bg_color, text="#Clusters")
ncl_text.grid(column=0, row=0, sticky="we")
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
canvas._tkcanvas.config(borderwidth=0,relief="sunken", background=bg_color)

toolbar_frame = tkinter.Frame(mainf, background=bg_color,borderwidth=0)
toolbar_frame.grid(column=0, row=3, columnspan=3, sticky="w")
toolbar = NavigationToolbar2TkAgg(canvas,toolbar_frame)

# area ist ein Axes instance
area = peak.add_subplot(111)
area.autoscale(enable=True, axis="both", tight="None")

#a = f.add_subplot(111)
#t = np.arange(0.0,3.0,0.01)
#s = np.sin(2*np.pi*t)

#def on_key_event(event):
#    print('you pressed %s'%event.key)
#    key_press_handler(event, canvas, toolbar)
#
#canvas.mpl_connect('key_press_event', on_key_event)

#line_cmenu = uicontextmenu;
#uimenu(line_cmenu,'Label','left','Tag','left','Callback',@change_line_rl);
#uimenu(line_cmenu,'Label','right','Tag','right','Callback',@change_line_rl);

# Frame 6 - Details zum Peak Finden
# ----------------------------------------
frame6 = tkinter.Frame(mainf, borderwidth=0, padx=5, pady=5, relief="sunken",
    background=bg_color)
frame6.grid(column=3, row=2, sticky="n")
# Checkbox "automatic"
auto_value = tkinter.IntVar()
auto_check = tkinter.Checkbutton(frame6, text="automatic", variable=auto_value, background=bg_color)
auto_check.grid(column=0, row=0, columnspan=2, sticky="nw")
# auto_check["state"] = tkinter.DISABLED
progress_bar = ttk.Progressbar(frame6, mode='determinate', orient=tkinter.HORIZONTAL)
progress_bar.grid(column=1, row=0, sticky="ne")                           
# Start Knopf
start_push = tkinter.Button(frame6, text="Start", command=start, state=tkinter.DISABLED, background=bg_color)
start_push.grid(column=0, row=1, sticky="nw")
cancel_push = tkinter.Button(frame6, text="Cancel", command=cancel_auto, state=tkinter.DISABLED, background=bg_color)
cancel_push.grid(column=1, row=1, sticky="ne")
active_stat = tkinter.BooleanVar(mainf)
active_stat.set(True)
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
next_push = tkinter.Button(frame6, text="Next", command=next_peak, state=tkinter.DISABLED, background=bg_color)
next_push.grid(column=0, row=8, sticky="nw")
# Save Knopf
save_push = tkinter.Button(frame6, text="Save", command=save_data, state=tkinter.DISABLED, background=bg_color)
save_push.grid(column=1, row=8, sticky="nw")
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
