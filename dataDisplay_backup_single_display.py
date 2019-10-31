from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal, Qt
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import AEFitDataInfo as aef
import fitDataInfo as fdi
import helplib as hl
import sys
import numpy as np


class DataDisplay_(FigureCanvas):
    statusbar_update = pyqtSignal(str)
    
    def __init__(self, parent=None):
        self.__fig, self.__ax = plt.subplots(1, 1, constrained_layout=True, figsize=(6, 8))
        
        FigureCanvas.__init__(self, self.__fig)
        
#        self.draw_event.connect(self.on_draw)
        
        if self.hasMouseTracking():
            self.setMouseTracking(True)

            self.__inv = self.__ax.transData.inverted()
        else:
            self.__inv = None
        
        self.setParent(parent)
        
        self.reset()
    
    def reset(self):
        self.__dc = 'black'
        self.__fc = 'orange'
        self.__ls = '-'
        self.__ew = 1
        self.__lw = 1.2
        self.__data = None
        self.__fdiFits = list()
        self.__stdErrors = None
        self.__clickmark = None
        self.__showErrorBars = False
        
        self.__upperZoom = 0
        self.__lowerZoom = 0

        self.__ax.clear()
        
    def draw_event(self, renderer):
        #super.draw_event(renderer)
        
        self.__inv = self.__ax.transData.inverted()
        
    def isLoaded(self):
        return self.__data is not None
    
    def mousePressEvent(self, event):
        
        if self.isLoaded():
            
            #super.mousePressEvent(event)
            
            if event.button() == Qt.LeftButton:
                if self.__inv is not None:
                    values = (np.float64(event.x()), np.float64(event.y()))
                    
                    tr_point = self.__inv.transform(values)
        
                    self.statusbar_update.emit(str(round(tr_point[0], 4)) + " eV")#, round(tr_point[1], 4))
                    # self.statusbar_update.emit(round(tr_point[0], 4), round(tr_point[1], 4))
                    
                    self.__clickmark = tr_point[0]
                    
                    self.refresh()
                else:
                    tr_point = (0.,0.)
            elif event.button() == Qt.RightButton:
                self.statusbar_update.emit("")
                
                self.__clickmark = None
                self.refresh()
    
   
    def refresh(self, data=None, stdErrors=None, showErrorBars=None):
        if data is not None:
            self.setData(data)
            
        if showErrorBars is not None:
            self.__showErrorBars = showErrorBars
        
        if self.isLoaded():
            if stdErrors is not None:
                self.__stdErrors = stdErrors
            
            if self.__stdErrors is not None:
                stdErrors = self.__stdErrors[self.__lowerZoom:self.__upperZoom]
            else:
                stdErrors = None
            
            if self.__showErrorBars == False:
                stdErrors = None
            
            self.__ax.clear()
            
            self.__ax.errorbar(self.__data[self.__lowerZoom:self.__upperZoom, 0],
                               self.__data[self.__lowerZoom:self.__upperZoom, 1],
                               yerr=stdErrors, fmt='.', markersize=3,
                               markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                               barsabove=True, capsize=2)
            
            self.__ax.set(ylabel='Counts (1/s)')
            self.__ax.set(xlabel='Energy (eV)')
            
            for fdiFit in self.__fdiFits:
                try:
                    if fdiFit.isFitted():
                        self.__plotFit(fdiFit)
                except Exception:
                    print("e")
            
            if self.__clickmark is not None:
                self.__ax.plot([self.__clickmark],[0],'g^')
            
            self.draw()
    
    def shiftData(self, increment):
        if self.isLoaded():
            for set in self.__data:
                set[0] += increment
    
    def ZoomByIncrement(self, bound, increment):
        if self.isLoaded():
            if bound == 'u':
                if ((self.__upperZoom + increment) <= len(self.__data)) and (
                    (self.__upperZoom + increment) > self.__lowerZoom):
                    self.__upperZoom += increment
            elif bound == 'l':
                if ((self.__lowerZoom + increment) >= 0) and ((self.__lowerZoom + increment) < self.__upperZoom):
                    self.__lowerZoom += increment
    
    def ZoomShowAll(self):
        if self.isLoaded():
            self.__lowerZoom = 0
            self.__upperZoom = len(self.__data)
    
    def ZoomToFit(self, lb, ub):
        if self.isLoaded():
            self.__lowerZoom = lb
            self.__upperZoom = ub
    
    def setData(self, data):
        self.__data = data
            
        self.__upperZoom = len(data)
        self.__lowerZoom = 0
    
    def setStdErrors(self, stdErrors):
        self.__stdErrors = stdErrors
    
    def addFit(self, fitData):
        self.__fdiFits.append(fitData)
    
    def resetFits(self):
        self.__fdiFits.clear()
    
    def clearFits(self):
        self.__fdiFits.clear()
    
    def showErrorBars(self, showErrorBars):
        self.refresh(showErrorBars=showErrorBars)
    
    def __plotFit(self, fdiCurrent: fdi.fitDataInfo):
        fitData = fdiCurrent.getFitData()
        
        self.__ax.plot(fitData[self.__lowerZoom:self.__upperZoom, 0], fitData[self.__lowerZoom:self.__upperZoom, 1],
                       linestyle=self.__ls, color=self.__fc, linewidth=self.__lw)
        self.__mark_ae_data_in_plot(fdiCurrent)
    
    def __mark_ae_data_in_plot(self, fdiCurrent: fdi.fitDataInfo):
        
        aec = 'black'
        fitareac = '#EFEFEF'
        aeareac = '#ABABAB'
        
        lowerFitBound = fdiCurrent.getFitRelFrom()
        upperFitBound = fdiCurrent.getFitRelTo()
        fwhm = fdiCurrent.getFWHM()
        p = fdiCurrent.getParameters()
        
        # mark AE
        self.__ax.axvline(x=p[1], color=aec, linestyle='-', linewidth='1')
        
        x_min = self.__ax.viewLim.intervalx[0]
        x_max = self.__ax.viewLim.intervalx[1]
        
        lb_fwhm = p[1] - 0.5 * fwhm
        ub_fwhm = p[1] + 0.5 * fwhm
        
        if lb_fwhm < x_min:
            lb_fwhm = x_min
        
        if ub_fwhm > x_max:
            ub_fwhm = x_max
        
        # mark relevant fit area
        
        if lowerFitBound != -1 and upperFitBound != -1:
            self.__ax.axvspan(lowerFitBound, upperFitBound, facecolor=fitareac, alpha=0.5)
        
        if fwhm > 0:
            self.__ax.axvspan(lb_fwhm, ub_fwhm, facecolor=aeareac, alpha=0.5)
    
    def getFigure(self):
        return self.__fig
