import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal, Qt
#import matplotlib.pyplot as plt
import fitDataInfo as fdi

class DataDisplay(FigureCanvas):

    std_fig_width = 6.40
    std_fig_height = 4.80
    std_label_font_size = 15
    std_scale_font_size = 15
    std_ann_font_size = 24

    statusbar_update = pyqtSignal(str)

    mark_default_text = 'Click on figure to show energy value.'

    def __init__(self, parent=None):
        self.__fig, self.__ax = plt.subplots(1, 1, tight_layout=True)
#        FigureCanvas.__init__(self, self.__fig)
        super(FigureCanvas, self).__init__(self.__fig)

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
        #1.2
        self.__data = None
        self.__fdiFits = list()
        self.reset_fitIndex()
        self.__combined_fit_data = list()
        self.__stdErrors = None
        self.__clickmark = None
        self.__showErrorBars = False
        self.__annotations = None
        
        self.__label_font = {'size': self.std_label_font_size}
        self.__scale_font = {'size': self.std_scale_font_size}
        self.__annotation_font = {'size': self.std_ann_font_size}

        self.__ax.clear()
        self.refresh()
        self.set_fig_size([self.std_fig_width, self.std_fig_height], False)

    def draw_event(self, renderer):
        self.__inv = self.__ax.transData.inverted()
 
    def set_fig_size(self, figsize):
        self.__fig.figsize = figsize

    def set_fig_size(self, new_fig_size, forward=True):
        if self.isLoaded():
            if new_fig_size[0] > 0 and new_fig_size[1] > 0:
               try:
                   self.__fig.set_size_inches(new_fig_size, forward=True)
                   #pass
               except Exception as error:
                   print(error)

    def isLoaded(self):
        return self.__data is not None
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if self.isLoaded():

            if event.button() == Qt.MidButton:
                if self.__clickmark is None:
                    if self.__inv is not None:
                        values = (float(event.x()), float(event.y()))

                        tr_point = self.__inv.transform(values)

                        self.statusbar_update.emit(str(round(tr_point[0], 4)) + " eV")#, round(tr_point[1], 4))
                        # self.statusbar_update.emit(round(tr_point[0], 4), round(tr_point[1], 4))

                        self.__clickmark = tr_point[0]

                        self.update_clickmark()
                        self.draw()
                    else:
                        tr_point = (0., 0.)
                else:
                    self.statusbar_update.emit(DataDisplay.mark_default_text)

                    self.__clickmark = None
                    #self.update_clickmark()
                    self.refresh()


#    def drawEvent(self, a):
#        super().drawEvent(a)
#        print("resizeEvent")
#        print(a)

#    def draw_event(self, a):
#        print("resize_event")
#        super().draw_event(self)

        #self.getwidthheight()

    def refresh(self, data=None, stdErrors=None, showErrorBars=None):
        if data is not None:
            self.setData(data)
            
        if showErrorBars is not None:
            self.__showErrorBars = showErrorBars
        
        if self.isLoaded():
            if self.__showErrorBars == False:
                stdErrors = None
            else:
                if stdErrors is not None:
                    self.__stdErrors = stdErrors
                
                if self.__stdErrors is not None:
                    stdErrors = self.__stdErrors[:]
                else:
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
            
            self.update_clickmark()
            self.update_annotations()
            
            self.draw()
            
    def update_clickmark(self):
        if self.__clickmark is not None:
            #if self.__data[self.__lowerZoom, 0] <= self.__clickmark <= self.__data[self.__upperZoom, 0]:
                self.__ax.plot([self.__clickmark], [0], 'g^')

    def update_annotations(self):
        #trigger on_zoom or find another way
        if self.__annotations is not None and len(self.__annotations) > 0:
            (xmin, xmax) = self.__ax.get_xlim()
            (ymin, ymax) = self.__ax.get_ylim()

            xpos = xmin + 0.01 * (xmax - xmin)
            ypos = ymax - 0.01 * (ymax - ymin)
            
            xpos = 0.02
            ypos = 0.98

            if len(self.__annotations) > self.__fitIndex+1:
                annotation = self.__annotations[self.__fitIndex + 1]

                self.__ax.annotate(annotation,
                                   #xy=(xpos, ypos),
                                   #xycoords = 'axes fraction',
                                   xytext = (xpos, ypos),
                                   textcoords = 'axes fraction',
                                   horizontalalignment='left',
                                   verticalalignment='top',
                                   fontsize=self.__annotation_font['size'])

    def current_fdi(self):
        return self.__fdiFits[self.__fitIndex]
    
    def show_all_fits(self):
        return self.__fitIndex == -1
    
    def getCurrentData(self):
        if self.show_all_fits():
            return self.__data
        else:
            return self.current_fdi().get_data()

    def set_annotation(self, annotation):
        self.__annotations = annotation.split('-- next --\n')
        self.update_annotations()
        self.draw()
    
    def getCurrentFitData(self):
        if self.show_all_fits():
            if self.__combined_fit_exists():
                return self.__combined_fit_data[:, ]
            else:
                return None
        else:
            if self.current_fdi().isFitted() and self.current_fdi().isDisabled() is False:
                return self.current_fdi().getFitData()
            else:
                return None

    def __plot_data(self, data, stdErrors):
        self.__ax.errorbar(data[:, 0],
                           data[:, 1],
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
        pass
        #if self.isLoaded():
        #    if bound == 'u':
        #        if ((self.__upperZoom + increment) <= len(self.__data)) and (
        #            (self.__upperZoom + increment) > self.__lowerZoom):
        #            self.__upperZoom += increment
        #    elif bound == 'l':
        #        if ((self.__lowerZoom + increment) >= 0) and ((self.__lowerZoom + increment) < self.__upperZoom):
        #            self.__lowerZoom += increment
    
    def ZoomShowAll(self):
        if self.isLoaded():
            self.__ax.set_xlim(self.__data[0, 0], self.__data[-1, 0])
            self.__ax.set_ylim(self.__data[0:-1, 1].min(), self.__data[0:-1, 1].max())
            self.draw()
    
    def ZoomToFit(self, x_lb, x_ub, fit_index):
        if self.isLoaded():
            self._zoom_to_xbounds(x_lb, x_ub)

    def _zoom_to_xbounds(self, x_lb, x_ub):
            (x_margin, y_margin) = self.__ax.margins()
            y_lb = self._find_y_min_between(x_lb, x_ub, self.getCurrentData(), self.getStdErrors())
            #y_lb = self._find_y_min_between(x_lb, x_ub, self.getCurrentData(), None)
            
            if y_lb > 0:
                y_lb = 0
            
            y_ub = self._find_y_max_between(x_lb, x_ub, self.getCurrentData(), self.getStdErrors())
            #y_ub = self._find_y_max_between(x_lb, x_ub, self.getCurrentData(), None)

            x_dev = (x_ub-x_lb) * x_margin/2
            y_dev = (y_ub - y_lb) * y_margin / 2

            self.__ax.set_xlim(x_lb - x_dev, x_ub + x_dev)
            self.__ax.set_ylim(y_lb - y_dev, y_ub + y_dev)

            #self.__ax.set_xlim(x_lb, x_ub)
            #self.__ax.set_ylim(y_lb, y_ub)
            self.draw()

    def _find_y_max_between(self, xmin, xmax, data, errors):
        y_max = None
        error = 0
        for i in range(1, len(data)):
            (x, y) = data[i]
            
            if errors is not None and i < len(errors):
                error = errors[i]
            else:
                error = 0
            
            if xmin <= x <= xmax:
                if y_max is None or y + error > y_max:
                    y_max = y + error

        return y_max

    def _find_y_min_between(self, xmin, xmax, data, errors):
        y_min = None
        error = 0
        for i in range(1, len(data)):
            (x, y) = data[i]
            
            if errors is not None and i < len(errors):
                error = errors[i]
            
            if xmin <= x <= xmax:
                if y_min is None or y - error < y_min:
                    y_min = y - error
    
        return y_min

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
            
        #self.__upperZoom = len(data)-1
        #self.__lowerZoom = 0
    
    def setStdErrors(self, stdErrors):
        self.__stdErrors = stdErrors
        
    def getStdErrors(self):
        return self.__stdErrors
    
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
        
        self.__ax.plot(fitData[:, 0], fitData[:, 1],
                       linestyle=self.__ls, color=self.__fc, linewidth=self.__lw)
        self.__mark_ae_data_in_plot(fdiCurrent)
        
    def __plot_combined_fit(self):
        if self.__combined_fit_exists():
    
            self.__ax.plot(self.__combined_fit_data[:, 0],
                           self.__combined_fit_data[:, 1],
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
