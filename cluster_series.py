# (C) 2012-2016 Arntraud Bacher
# Institut für Ionenphysik und Angewandte Physik
# Universitaet Innsbruck

from tkinter import ttk
import tkinter as tk
from tkinter import simpledialog as tksi
from tkinter import scrolledtext as tkst

import os
import serieslib as sl
import numpy as np
import matplotlib
import configparser as cp
import json
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
    def getDaten(self,data,deltaMax):
        self.x_daten, self.y_daten = sl.get_daten(data,
            self.StartMass,deltaMax)
    def findMax(self):
        # Maximum im Ionensignal suchen
        self.y_max,index_y_max = self.y_daten.max(0),self.y_daten.argmax(0)
        self.x_max = self.x_daten[index_y_max]
    def baseline(self,data,deltaMinL,binMinL,deltaMinR,binMinR):
        #print("Baselinepunkt links")
        self.x_base_l, self.y_base_l = sl.get_left_baseline(data,
            self.StartMass,deltaMinL,binMinL)
        #print("Baselinepunkt rechts")
        self.x_base_r, self.y_base_r = sl.get_right_baseline(data,
            self.StartMass,deltaMinR,binMinR)
    def basepoint(self):
        coeff = np.polyfit(np.array([self.x_base_l,self.x_base_r]),
                           np.array([self.y_base_l,self.y_base_r]),1);
        polynom = np.poly1d(coeff)
        self.base_y = polynom(self.x_max)
    def plotDaten(self,data,deltaPlot):
        self.xp_daten, self.yp_daten = sl.get_daten(data,self.StartMass,
            deltaPlot)
    def area(self,data):
        #Peakwerte
        area, anzahl = sl.get_area(data,self.StartMass,
            self.x_base_l,self.x_base_r)
        self.areaCorr = area - anzahl * np.mean(np.array([self.y_base_l,self.y_base_r]))

# ----------------------------------------
# Class CSParams für die Eingabefelder rechts vom Graphen
# ----------------------------------------
class CSParams:
    def __init__(self,frame,paramname,zeile,startwert,mode,parent):
        ttk.Label(frame, text=paramname).grid(column=0, row=zeile, sticky=tk.W)
        self.wert = tk.StringVar()
        self.edit = ttk.Entry(frame, textvariable=self.wert,
            justify=tk.RIGHT, state=tk.DISABLED)
        self.wert.set(startwert)
        self.edit.bind('<Return>', self.changed)
        self.edit.bind('<Tab>', self.changed)
        self.edit.grid(column=1, row=zeile)
        self.mode = mode
        self.parent = parent
    def disable(self):
        self.edit.config(state=tk.DISABLED)
    def enable(self):
        self.edit.config(state=tk.NORMAL)

    # Wert hat sich geändert -> neue Berechnung und Zeichnung
    def changed(self,event):
        text = self.wert.get()
        text = text.replace(',','.')
        self.wert.set(text)        
        if self.mode=='value':
            self.parent.berechne_peak()
        elif self.mode=='deltaplot':
            self.parent.zeichne_peak()        

# ----------------------------------------
# Class CSBaseline - Linie mit verschiebaren Endpunkten
# ----------------------------------------
class CSBaseline:
    def __init__(self,line,current_peak,g_base,toolbar):
        self.line = line
        self.press = None
        self.current_peak = current_peak
        self.g_base = g_base
        self.toolbar = toolbar

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
            #self.x_old = np.take(self.xdata,event.ind)
            #self.y_old = np.take(self.ydata,event.ind)
            #print("index:", self.index)
            #print('xdata:',self.x_old)
            #print('ydata:',self.y_old)
        
    def click_baseline(self,event):
        #print(self.toolbar.message.get())
        #print('button_click=', event.button, 'x=', event.x, 'y=', event.y,
        #      'xdata=', event.xdata, 'ydata=', event.ydata)
        contains, attrd = self.line.contains(event)
        if not contains: return
        if self.toolbar.mode!='':
            # leave toolbar mode
            tk.messagebox.showwarning('Navigation Toolbar Active','Please leave toolbar mode: '+self.toolbar.mode)
            return
        self.press = True
    def move_baseline(self,event):
        if self.press is None: return
        #print('button_move=', event.button, 'x=', event.x, 'y=', event.y,
        #      'xdata=', event.xdata, 'ydata=', event.ydata)
        self.xdata[self.index] = event.xdata
        self.ydata[self.index] = event.ydata
        self.line.set_xdata(self.xdata)
        self.line.set_ydata(self.ydata)
        self.line.figure.canvas.draw()
    def release_baseline(self,event):
        if self.press is None: return
        #print('button_release=', event.button, 'x=', event.x, 'y=', event.y,
        #      'xdata=', event.xdata, 'ydata=', event.ydata)
        self.press = None
        idx = sl.get_closest_index(self.current_peak.xp_daten,event.xdata)
        self.xdata[self.index] = self.current_peak.xp_daten[idx]
        self.ydata[self.index] = self.current_peak.yp_daten[idx]
        self.line.set_xdata(self.xdata)
        self.line.set_ydata(self.ydata)
        # Background-Punkt am Maximum berechnen
        self.current_peak.x_base_l = self.xdata[0]
        self.current_peak.x_base_r = self.xdata[1]
        self.current_peak.y_base_l = self.ydata[0]
        self.current_peak.y_base_r = self.ydata[1]
        self.current_peak.basepoint()
        self.g_base.set_ydata(self.current_peak.base_y)
        self.g_base.figure.canvas.draw()
        self.line.figure.canvas.draw()

# ----------------------------------------
# Definitionen zur Oberfläche CSFrame
# ----------------------------------------
class CSFrame(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.close)
        # Style konfigurieren
        style = ttk.Style()
        style.configure('TFrame', padding=5, relief='flat')
        style.configure('Red.TCheckbutton', background='#f00')
        # INI File laden
        self.custom = cp.ConfigParser()
        self.custom.read(os.path.join(os.path.dirname(os.path.realpath(__file__)),'cluster_series.ini'))
        # Gespeicherte Werte laden
        self.coreions, self.monomers = sl.readElements(self.custom)        
        # Menu
        mMenu = tk.Menu(self)
        self.config(menu=mMenu)
        mFile = tk.Menu(mMenu)
        mLoad = mFile.add_command(label='Load File', command=self.loadFile)
        mMenu.add_cascade(label='File', menu=mFile)

        # Spectrum File
        # ----------------------------------------
        self.specFileWert = tk.StringVar()
        ttk.Entry(self, textvariable=self.specFileWert,
            state=tk.DISABLED).grid(column=0,
            row=0, columnspan=2, sticky=tk.W+tk.E)
        self.specFileWert.set('no spectrum file open')
        # Savitzky-Golay-Filter fehlt noch
        # window_size = 5, order = 2, deriv = 0 entspricht den Matlab-Einstellungen
        # callback = smooth_spec       
        
        # Frame - Core Ion und Monomer
        # ----------------------------------------
        IonFrame = ttk.Frame(self, borderwidth=0, style='TFrame')
        IonFrame.grid(column=0, row=1, sticky=tk.W+tk.E)

        # Liste mit Coreions
        # Beschreibung
        ttk.Label(IonFrame, text='Core Ion').grid(column=0, row=0,
            sticky=tk.W+tk.E)
        # Combobox
        self.ciCombo=ttk.Combobox(IonFrame, values=self.coreions,
            exportselection=0, state='readonly')
        self.ciCombo.bind('<<ComboboxSelected>>', self.selectCI)
        self.ciCombo.grid(column=0, row=1)
        ttk.Button(IonFrame, text='Add Core Ion', command=self.newCI).grid(column=1, row=1)

        # Liste mit Monomers
        # Beschreibung
        ttk.Label(IonFrame, text='Monomer').grid(column=2, row=0,
            sticky=tk.W+tk.E)
        # Combobox
        # exportselection=0, ansonsten wird ausgewählter Text in die
        # Zwischenablage kopiert
        self.moCombo=ttk.Combobox(IonFrame, values=self.monomers,
            exportselection=0, state='readonly')
        self.moCombo.bind('<<ComboboxSelected>>', self.selectMO)
        self.moCombo.grid(column=2, row=1)
        ttk.Button(IonFrame, text='Add Monomer', command=self.newMO).grid(column=3, row=1)

        # Number of Clusters
        ttk.Label(IonFrame, text='#Clusters').grid(column=4, row=0,
            sticky=tk.W+tk.E)
        self.nclWert = tk.StringVar()
        ttk.Entry(IonFrame, textvariable=self.nclWert,
            justify=tk.RIGHT).grid(column=4, row=1)
        self.nclWert.set('100')

        # Frame - Graph mit matplotlib
        # ----------------------------------------
        peak = Figure(figsize=(6,6), dpi=100)

        # a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(peak, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=0, row=2, columnspan=3)
        self.canvas._tkcanvas.config(borderwidth=0,relief='sunken')

        toolbar_frame = ttk.Frame(self, borderwidth=0)
        toolbar_frame.grid(column=0, row=3, columnspan=3, sticky=tk.W)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas,toolbar_frame)

        # area ist ein Axes instance
        self.area = peak.add_subplot(111)
        self.area.autoscale(enable=True, axis='both', tight='None')
        # Set ticker to exponential
        self.area.ticklabel_format(style='sci',scilimits=(-3,3),axis='both')
        # tight layout has less space around axes
        peak.tight_layout()
        
        #def on_key_event(event):
        #    print('you pressed %s'%event.key)
        #    key_press_handler(event, canvas, toolbar)
        #
        #canvas.mpl_connect('key_press_event', on_key_event)

        # Frame - Details zum Peak Finden
        # ----------------------------------------
        PeakFrame = ttk.Frame(self, borderwidth=0)
        PeakFrame.grid(column=3, row=2, sticky=tk.N)
        # Checkbox "automatic"
        self.autoValue = tk.IntVar()
        self.autoCheck = ttk.Checkbutton(PeakFrame, text="automatic",
            variable=self.autoValue)
        self.autoCheck.grid(column=0, row=0, columnspan=2, sticky=tk.N+tk.W)
        self.progressBar = ttk.Progressbar(PeakFrame, mode='determinate', orient=tk.HORIZONTAL)
        self.progressBar.grid(column=1, row=0, sticky=tk.N+tk.E)
        # Start Knopf
        self.startPush = ttk.Button(PeakFrame, text="Start", command=self.start, state=tk.DISABLED)
        self.startPush.grid(column=0, row=1, sticky=tk.N+tk.W)
        self.cancelPush = ttk.Button(PeakFrame, text="Cancel", command=self.cancelAuto, state=tk.DISABLED)
        self.cancelPush.grid(column=1, row=1, sticky=tk.N+tk.E)
        self.activeStat = tk.BooleanVar(self)
        self.activeStat.set(True)
        # Delta Plot
        self.deltaPlot = CSParams(PeakFrame,"Delta Plot",2,'10','deltaplot',self)
        # Delta Max
        self.deltaMax = CSParams(PeakFrame,"Delta Max_Peak",3,'0.01','value',self)
        # Delta Min Links
        self.deltaMinL = CSParams(PeakFrame,"Delta Min_BG left",4,'0.5','value',self)
        # Bin Min Links
        self.binMinL = CSParams(PeakFrame,"Bins Min_BG left",5,'1','value',self)
        # Delta Min Rechts
        self.deltaMinR = CSParams(PeakFrame,"Delta Min_BG right",6,'0.5','value',self)
        # Bin Min Rechts
        self.binMinR = CSParams(PeakFrame,"Bins Min_BG right",7,'1','value',self)
        # Next Knopf
        self.nextPush = ttk.Button(PeakFrame, text="Next", command=self.nextPeak, state=tk.DISABLED)
        self.nextPush.grid(column=0, row=8, sticky=tk.N+tk.W)
        # Save Knopf
        self.savePush = ttk.Button(PeakFrame, text="Save", command=self.saveData, state=tk.DISABLED)
        self.savePush.grid(column=1, row=8, sticky=tk.N+tk.W)
        #Comments
        ttk.Label(PeakFrame, text='Comment').grid(column=0, row=9, columnspan=2, sticky=tk.W)
        self.commentEdit = tkst.ScrolledText(PeakFrame, width='25')
        self.commentEdit.grid(column=0, row=10, columnspan=2, sticky=tk.S)

    # Schließen des Fenster
    def close(self):
        sl.writeElements(self.custom,self.coreions,self.monomers)
        print('Window closed')
        self.destroy()
        
    # Auswählen des Dateinamens    
    def loadFile(self):
        # Knöpfe und Eingabefelder deaktivieren
        self.startPush.config(state=tk.DISABLED)
        self.nextPush.config(state=tk.DISABLED)
        self.savePush.config(state=tk.DISABLED)
        self.deltaPlot.disable()
        self.deltaMax.disable()
        self.deltaMinL.disable()
        self.binMinL.disable()
        self.deltaMinR.disable()
        self.binMinR.disable()
        self.fname = tk.filedialog.askopenfilename()
        if self.fname == '':
            self.specFileWert.set('no spectrum file open')
        else:
            self.data = np.loadtxt(self.fname)
            self.specFileWert.set('Current file: ' + self.fname)
            # Knöpfe und Eingabefelder aktivieren
            self.startPush.config(state=tk.NORMAL)
            self.deltaPlot.enable()
            self.deltaMax.enable()
            self.deltaMinL.enable()
            self.binMinL.enable()
            self.deltaMinR.enable()
            self.binMinR.enable()
        self.smoothed = 0;


    # Auswählen des Core Ions
    def selectCI(self,event):
        self.ci_info = event.widget.get().split(' - ')
        temp = self.ci_info[1]
        self.ci_info[1] = float(temp)
        
    # Neues Core Ion
    def newCI(self):
        name_ci = tksi.askstring(
        'Enter new Core Ion', 'Enter name of Core Ion')
        mass_ci = tksi.askstring(
        'Enter new Core Ion', 'Enter mass of Core Ion')
        self.coreions.append('{0} - {1}'.format(name_ci, mass_ci))
        self.ciCombo['values'] = self.coreions

    # Auswählen des Monomers
    def selectMO(self,event):
        self.mo_info = event.widget.get().split(' - ')
        temp = self.mo_info[1]
        self.mo_info[1] = float(temp)

    def newMO(self):
        name_mo = tksi.askstring(
        'Enter new Monomer', 'Enter name of Monomer')
        mass_mo = tksi.askstring(
        'Enter new Monomer', 'Enter mass of Monomer')
        self.monomers.append('{0} - {1}'.format(name_mo, mass_mo))
        self.moCombo['values'] = self.monomers
    
    def start(self):
        self.current_cs = 0 # Clustersize
        self.peaks = []
        if self.autoValue.get():
            self.autoCheck.configure(style='Red.TCheckbutton')
            self.nextPush.config(state=tk.DISABLED)
            self.cancelPush.config(state=tk.NORMAL)
            self.deltaPlot.disable()
            self.deltaMax.disable()
            self.deltaMinL.disable()
            self.binMinL.disable()
            self.deltaMinR.disable()
            self.binMinR.disable()
            self.progressBar['value'] = 0
            self.activeStat.set(True)
            cs = int(self.nclWert.get())
            while self.activeStat.get():
                self.progressBar['value'] = self.current_cs/cs*100
                self.berechne_peak()
                # Fläche berechnen
                self.current_peak.area(self.data)
                self.peaks.append(self.current_peak)
                if self.current_cs < cs:
                    self.current_cs += 1
                else:
                    self.activeStat.set(False)
                mainf.update()
            self.savePush.config(state=tk.NORMAL)
            self.cancelPush.config(state=tk.DISABLED)
        else:
            self.nextPush.config(state=tk.NORMAL)
            self.deltaPlot.enable()
            self.deltaMax.enable()
            self.deltaMinL.enable()
            self.binMinL.enable()
            self.deltaMinR.enable()
            self.binMinR.enable()
            self.berechne_peak()
            
    # Abbruch im Automatic-Mode
    def cancelAuto(self):
        print('Automatic evaluation cancelled')
        self.activeStat.set(False)            

    def berechne_peak(self):
        try:
            self.current_peak = CSPeak(self.ci_info[1],self.mo_info[1],self.current_cs)
        except:
            print('Please choose Core Ion and/or Monomer')
        #print(current_peak)
        self.current_peak.getDaten(self.data,float(self.deltaMax.wert.get()))
        self.current_peak.findMax()
        #print("Baseline")
        self.current_peak.baseline(self.data,float(self.deltaMinL.wert.get()),
            float(self.binMinL.wert.get()),float(self.deltaMinR.wert.get()),
            float(self.binMinR.wert.get()))
        self.current_peak.basepoint()
        #print("in berechne_peak vor zeichne_peak")
        self.zeichne_peak()

    def zeichne_peak(self):
        #print(deltaplot_wert.get())
        self.current_peak.plotDaten(self.data,float(self.deltaPlot.wert.get()))
        #print("in zeichne_peak vor plot")
        self.area.clear()
        self.area.plot(self.current_peak.xp_daten, self.current_peak.yp_daten,
            color='k')
        self.area.axvline(x=self.current_peak.StartMass, color='r')
        #print(current_peak.y_max)
        g_base, = self.area.plot(np.array([self.current_peak.x_max,self.current_peak.x_max]),
                             np.array([self.current_peak.base_y,self.current_peak.y_max]),
                             color='g', marker='x', linestyle='None')
        self.area.set_title(("Cluster Size: " + str(self.current_cs)))
    
        # Baseline zeichnen
        b_line, = self.area.plot(np.array([self.current_peak.x_base_l,self.current_peak.x_base_r]),
                        np.array([self.current_peak.y_base_l,self.current_peak.y_base_r]),
                        color='b',marker='d',picker=5)
        self.baseline = CSBaseline(b_line, self.current_peak, g_base, self.toolbar)
        self.baseline.connect()
    
        # Plot darstellen
        self.area.relim()
        self.area.autoscale_view(True,True,True)
        self.canvas.draw()
        #print("in zeichne_peak nach plot")

    def nextPeak(self):
        #print("in next_peak")
        self.current_cs += 1
        if self.current_cs < float(self.nclWert.get()):
            # Fläche berechnen
            self.current_peak.area(self.data)
            self.peaks.append(self.current_peak)
            self.savePush.config(state=tk.NORMAL)
            self.berechne_peak()
        else:
            # Fläche berechnen
            self.current_peak.area(self.data)
            self.peaks.append(self.current_peak)
            self.berechne_peak()
            self.nextPush.config(state=tk.DISABLED)

    def saveData(self):
        if self.autoValue.get() == 0:
            self.current_peak.area(self.data)
            self.peaks.append(self.current_peak)
        print("Speichern")
        # Dateinamen erstellen
        # spec.ext -> spec_coreion_monomer.ext
        fileName, fileExtension = os.path.splitext(self.fname)
        # Falls keine Extension -> .dat anfügen
        if not fileExtension:
            fileExtension = '.dat'
        f = open(fileName + '_' + self.ci_info[0] + '_' + self.mo_info[0] + fileExtension, 'w')
        if self.autoValue.get():
            f.write('# Mode: automatic\n')
        else:
            f.write('# Mode: interactive\n')
        f.write('# Settings:\n')
        saveformat = '# Core Ion: {0:f}; Monomer: {1:f}\n'
        f.write(saveformat.format(self.current_peak.CoreIon,
            self.current_peak.Monomer))
        f.write('# Comments:\n')
        f.write('# {}'.format(self.commentEdit.get('1.0','end').replace('\n', '\n# ')))
        f.write('Cluster Size; x-Maximum; x-StartMass; x-Diff; y-Maximum; y-Base; y-Diff; Area_Corr\n')
        for i in range(len(self.peaks)):
            saveformat = '{0:2d}\t{1:15.6f}\t{2:15.6f}\t{3:15.6f}\t{4:15.6f}\t{5:15.6f}\t{6:15.6f}\t{7:15.6f}\n'
            f.write(saveformat.format(self.peaks[i].ClusterSize,
                self.peaks[i].x_max, self.peaks[i].StartMass,
                self.peaks[i].x_max-self.peaks[i].StartMass,
                self.peaks[i].y_max, self.peaks[i].base_y,
                self.peaks[i].y_max-self.peaks[i].base_y,
                self.peaks[i].areaCorr))
        f.close()

# ----------------------------------------
# Hauptroutine
# ----------------------------------------
if __name__ == '__main__':
    # Hauptfenster öffnen
    mainf = CSFrame()
    mainf.title('Cluster Series v1.5')
    
    # Endlosschleife
    mainf.mainloop()

