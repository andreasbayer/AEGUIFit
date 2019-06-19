from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal, Qt
import matplotlib.pyplot as plt
import fitDataInfo as fdi


class DataDisplay(FigureCanvas):
    statusbar_update = pyqtSignal(str)

    mark_default_text = 'Click on figure to show energy value.'

    def __init__(self, parent=None):
        self.__fig, self.__ax = plt.subplots(1, 1, tight_layout=True)
        FigureCanvas.__init__(self, self.__fig)

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
        self.__ew = 1.2
        self.__lw = 1.2
        4#1.2
        self.__data = None
        self.__fdiFits = list()
        self.reset_fitIndex()
        self.__combined_fit_data = list()
        self.__stdErrors = None
        self.__clickmark = None
        self.__showErrorBars = False
        self.__annotation = None
        
        self.__upperZoom = 0
        self.__lowerZoom = 0

        self.__label_font = {'size':14}
        self.__scale_font = {'size':14}
        self.__annotation_font = {'size':14}

        self.__ax.clear()

    def draw_event(self, renderer):
        #super.draw_event(renderer)
        
        self.__inv = self.__ax.transData.inverted()

    def set_fig_size(self, figsize):
        self.__fig.figsize = figsize

    def increase_fig_size(self, new_fig_size):
        if new_fig_size[0] > 0 and new_fig_size[1] > 0:
            self.__fig.set_size_inches(new_fig_size, forward=True)

    def isLoaded(self):
        return self.__data is not None
        
    def mousePressEvent(self, event):
        if self.isLoaded():
            
            #super.mousePressEvent(event)
            
            if event.button() == Qt.LeftButton:
                if self.__inv is not None:
                    values = (float(event.x()), float(event.y()))

                    tr_point = self.__inv.transform(values)

                    self.statusbar_update.emit(str(round(tr_point[0], 4)) + " eV")#, round(tr_point[1], 4))
                    # self.statusbar_update.emit(round(tr_point[0], 4), round(tr_point[1], 4))
                    
                    self.__clickmark = tr_point[0]
                    
                    self.refresh()
                else:
                    tr_point = (0., 0.)
            elif event.button() == Qt.RightButton:
                self.statusbar_update.emit(DataDisplay.mark_default_text)
                
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

            #plot data only here:
            
            if self.show_all_fits():
                self.__plot_data(self.__data, stdErrors)
                self.__plot_combined_fit()
            else:
                try:
                    self.__plot_data(self.current_fdi().get_data(), stdErrors)
                    
                    if self.current_fdi().isFitted():
                        self.__plotFit(self.current_fdi())
                except Exception:
                    print("e")
            
            if self.__clickmark is not None:
                self.__ax.plot([self.__clickmark], [0], 'g^')

            if self.__annotation is not None and len(self.__annotation) > 0:
                (xmin, xmax) = self.__ax.get_xlim()
                (ymin, ymax) = self.__ax.get_ylim()
                
                xpos = xmin + 0.01 * (xmax - xmin)
                ypos = ymax - 0.01 * (ymax - ymin)
                
                self.__ax.annotate(self.__annotation,
                                   xy=(xpos, ypos),
                                   horizontalalignment='left', verticalalignment='top',
                                   fontsize=self.__annotation_font['size'])
            self.draw()

    def current_fdi(self):
        return self.__fdiFits[self.__fitIndex]
    
    def show_all_fits(self):
        return self.__fitIndex == -1
    
    def getCurrentData(self):
        return self.__data

    def set_annotation(self, annotation):
        self.__annotation = annotation
    
    def getCurrentFitData(self):
        if self.show_all_fits():
            if self.__combined_fit_exists():
                return self.__combined_fit_data[self.__lowerZoom:self.__upperZoom, ]
            else:
                return None
        else:
            if self.current_fdi().isFitted() and self.current_fdi().isDisabled() is False:
                return self.current_fdi().getFitData()
            else:
                return None
    
    def __plot_data(self, data, stdErrors):
        self.__ax.errorbar(data[self.__lowerZoom:self.__upperZoom, 0],
                           data[self.__lowerZoom:self.__upperZoom, 1],
                           yerr=stdErrors, fmt='.', markersize=3,
                           markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                           barsabove=True, capsize=2)
        
        self.__ax.set_ylabel('Counts (1/s)', fontdict=self.__label_font)
        self.__ax.set_xlabel('Energy (eV)', fontdict=self.__label_font)
        
        
        
        for tick in self.__ax.xaxis.get_major_ticks():
            tick.label.set_size(self.__scale_font['size'])
        
        for tick in self.__ax.yaxis.get_major_ticks():
            tick.label.set_size(self.__scale_font['size'])
    
    def shiftData(self, increment):
        if self.isLoaded():
            for set in self.__data:
                set[0] += increment

    def update_combined_fit_data(self, combined_fit_data):
        self.__combined_fit_data = combined_fit_data
        
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
            self.__upperZoom = len(self.__data)-1
    
    def ZoomToFit(self, lb, ub, index):
        if self.isLoaded():
            self.__lowerZoom = lb
            self.__upperZoom = ub
            
    def ZoomWithMouse(self):
        #do a drag and drop zoom, because those increments stink
        pass

    def set_label_font_size(self, value):
        if value > 0:
            self.__label_font["size"] = value
            
    def set_scale_font_size(self, value):
        if value > 0:
            self.__scale_font["size"] = value

    def set_annotation_font_size(self, value):
        if value > 0:
            self.__annotation_font["size"] = value

    def setData(self, data):
        self.__data = data
            
        self.__upperZoom = len(data)-1
        self.__lowerZoom = 0
    
    def setStdErrors(self, stdErrors):
        self.__stdErrors = stdErrors
    
    def addFit(self, p_fitDataInfo):
        self.__fdiFits.append(p_fitDataInfo)
        
    def removeFit(self, p_fitDataInfo):
        self.__fdiFits.remove(p_fitDataInfo)
    
    def resetFits(self):
        self.__fdiFits.clear()
        self.reset_fitIndex()
        
    #pass index through, or implement it into fitInfo?
    def update_fit(self, fitInfo):
        #self.__fdiFits.insert(fitInfo.get_fit_index(), fitInfo)
        pass
        
    def reset_fitIndex(self):
        self.__fitIndex = -1
    
    def fit_index_changed(self, index):
        self.__fitIndex = index
        
        self.refresh()
    
    def clearFits(self):
        self.__fdiFits.clear()
    
    def showErrorBars(self, showErrorBars):
        self.refresh(showErrorBars=showErrorBars)
    
    def __plotFit(self, fdiCurrent: fdi.fitDataInfo):
        fitData = fdiCurrent.getFitData()
        
        self.__ax.plot(fitData[self.__lowerZoom:self.__upperZoom, 0], fitData[self.__lowerZoom:self.__upperZoom, 1],
                       linestyle=self.__ls, color=self.__fc, linewidth=self.__lw)
        self.__mark_ae_data_in_plot(fdiCurrent)
        
    def __plot_combined_fit(self):
        if self.__combined_fit_exists():
    
            self.__ax.plot(self.__combined_fit_data[self.__lowerZoom:self.__upperZoom, 0],
                           self.__combined_fit_data[self.__lowerZoom:self.__upperZoom, 1],
                           linestyle=self.__ls, color=self.__fc, linewidth=self.__lw)
        
            for fdiCurrent in self.__fdiFits:
                if fdiCurrent.isFitted() and fdiCurrent.isDisabled() != True:
                    self.__mark_ae_data_in_plot(fdiCurrent)
    
    def __combined_fit_exists(self):
        return self.__combined_fit_data is not None and len(self.__combined_fit_data) > 0
    
    def __mark_ae_data_in_plot(self, fdiCurrent: fdi.fitDataInfo):
        
        aec = 'black'
        fitareac = '#EFEFEF'
        aeareac = '#ABABAB'
        
        lowerFitBound = fdiCurrent.getFitRelFrom()
        upperFitBound = fdiCurrent.getFitRelTo()
        fwhm = fdiCurrent.getFWHM()
        p = fdiCurrent.getParameters()
        
        lz = self.__data[self.__lowerZoom][0]
        uz = self.__data[self.__upperZoom][0]
        
        if lz >= upperFitBound:
            upperFitBound = -1
        elif lz >= lowerFitBound:
            lowerFitBound = lz
        
        if uz <= lowerFitBound:
            lowerFitBound = -1
        elif uz <= upperFitBound:
            upperFitBound = uz
        
        
        if lz <= p[1] and p[1] <= uz:
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
        
        if ub_fwhm-lb_fwhm > 0:
            self.__ax.axvspan(lb_fwhm, ub_fwhm, facecolor=aeareac, alpha=0.5)
    
    def getFigure(self):
        return self.__fig
