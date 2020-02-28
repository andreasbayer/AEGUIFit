import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import pyqtSignal, Qt

import fitDataInfo as fdi
import AEFitDataInfo as adi
import polyFitDataInfo as pdi
import numpy as np
import traceback

class DataDisplay(FigureCanvas):

    std_fig_width = 6.40
    std_fig_height = 4.80
    std_label_font_size = 15
    std_scale_font_size = 15
    std_ann_font_size = 24

    statusbar_update = pyqtSignal(str)
    is_loaded_changed = pyqtSignal(bool)

    mark_default_text = 'Click with scroll wheel on figure to show energy value.'

    def __init__(self, parent=None):
        self.__fig, self.__ax = plt.subplots(tight_layout=True)

#        FigureCanvas.__init__(self, self.__fig)
        super(FigureCanvas, self).__init__(self.__fig)

        if self.hasMouseTracking():
            self.setMouseTracking(True)

            self.__inv = self.__ax.transData.inverted()
        else:
            self.__inv = None

        self.setParent(parent)

        self.DisableRefresh(False)
        self.setResizingEnabled(True)
        self.reset()

    def reset(self):
        self.__dc = 'black'
        self.__fc = 'orange'
        self.__ls = '-'
        self.__ew = 1.2
        self.__lw = 1.2
        #1.2
        self.setData(None)
        self.__fdiFits = list()
        self.reset_fitIndex()
        self.__combined_fit_data = list()
        self.setStdErrors(None)
        self.__clickmark = None
        self.__showErrorBars = False
        self.__annotations = None
        
        self.__label_font = {'size': self.std_label_font_size}
        self.__scale_font = {'size': self.std_scale_font_size}
        self.__annotation_font = {'size': self.std_ann_font_size}

        self.__ax.clear()
        #self.refresh()
        #self.set_fig_size([self.std_fig_width, self.std_fig_height], False)

    def draw_event(self, renderer):
        self.__inv = self.__ax.transData.inverted()
 
    def set_fig_size(self, new_fig_size, forward=True):

        if self.isLoaded():
            if new_fig_size is not None:
                if new_fig_size[0] is not None and new_fig_size[1] is not None:
                    if len(new_fig_size) == 2 and new_fig_size[0] > 0 and new_fig_size[1] > 0:
                        try:
                            self.__fig.set_size_inches(new_fig_size, forward=True)
                        except Exception as error:
                            print(error)
                else:
                    try:
                        # setting it to same size won't update, therefore resize it to one pixel less. resizing window
                        # will adapt it and otherwise 1px is not noticeable
                        self.resize(self.parent().width()-1, self.parent().height()-1)
                    except Exception as e:
                        print(e)
            else:
                # self.__fig.set_size_inches(None)
                # have the size adapt to the width of the canvas
                pass

    def isLoaded(self):
        # if this changes, the trigger for is_loaded_changed has also be changed!
        return self.__data is not None

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if self.isLoaded():

            if event.button() == Qt.MidButton:
                if self.__clickmark is None:
                    if self.__inv is not None:
                        values = (np.float64(event.x()), np.float64(event.y()))

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

    def isRefreshDisabled(self):
        return self.__refreshDisabled

    def DisableRefresh(self, disable):
        self.__refreshDisabled = disable

    def refresh(self, data=None, stdErrors=None, showErrorBars=None, forgetZoomFrame=False, ignoreFirstPoint=False):

        xlim = None
        ylim = None

        if data is not None:
            self.setData(data)

        if showErrorBars is not None:
            self.__showErrorBars = showErrorBars

        if self.isRefreshDisabled() is False:

            if not forgetZoomFrame:
                xlim = self.__ax.get_xlim()
                ylim = self.__ax.get_ylim()

                #(xmar, ymar) = self.__ax.margins()

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
                    except Exception as e:
                        print('refresh', e)

                self.update_clickmark()
                self.update_annotations()
                self.update_xaxis()

                self.draw()

                if not forgetZoomFrame:
                    #if (self.__ax.get_xlim(), self.__ax.get_ylim()) != (xlim, ylim):
                        #self.__ax.set_xlim(xlim)
                        #self.__ax.set_ylim(ylim)

                        #self.__ax.margins(x=xmar, y=ymar)

                        #print(self.__ax.get_xlim(), self.__ax.get_ylim())
                        #print(self.__ax.margins())

                    self._zoom_to_bounds(xlim, ylim)
                else:
                    set_breakpoint = True
        return (xlim, ylim)

    def update_clickmark(self):
        if self.__clickmark is not None:
            #if self.__data[self.__lowerZoom, 0] <= self.__clickmark <= self.__data[self.__upperZoom, 0]:
            self.__ax.axvline(x=[self.__clickmark], color='g', linestyle='-.', linewidth='1')
                #self.__ax.plot([self.__clickmark], [0], 'g^')

    def update_annotations(self):
        #trigger on_zoom or find another way
        if self.__annotations is not None and len(self.__annotations) > 0:
            #(xmin, xmax) = self.__ax.get_xlim()
            #(ymin, ymax) = self.__ax.get_ylim()

            #+xpos = xmin + 0.01 * (xmax - xmin)
            #ypos = ymax - 0.01 * (ymax - ymin)
            
            xpos = 0.02
            ypos = 0.98

            if len(self.__annotations) > self.__fitIndex+1:
                annotation = self.__annotations[self.__fitIndex + 1]

                self.__ax.annotate(annotation,
                                   xy=(xpos, ypos),
                                   xycoords = 'axes fraction',
                                   xytext = (xpos, ypos),
                                   textcoords = 'axes fraction',
                                   horizontalalignment='left',
                                   verticalalignment='top',
                                   fontsize=self.__annotation_font['size'])

    def update_xaxis(self):
        self.__ax.axhline(y=0, color='black', linestyle=':', linewidth='1')

    def current_fdi(self):
        print(self.__fitIndex)
        print(len(self.__fdiFits))
        return self.__fdiFits[self.__fitIndex]
    
    def show_all_fits(self):
        return self.__fitIndex == -1
    
    def getCurrentData(self):
        if self.show_all_fits():
            return self.__data
        else:
            return self.current_fdi().get_data()

    def getAllData(self):
        return self.__data

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

    def getAllFitData(self, incl_disabled=False):

        all_fit_data = list()

        for fit in self.__fdiFits:
            if fit.isFitted() and (fit.isDisabled() is False or incl_disabled):
                all_fit_data.append(fit.getFitData())

        return all_fit_data

    def getCombinedFitData(self):
        return self.__combined_fit_data

    def __plot_data(self, data, stdErrors):

        if stdErrors is not None:
            stdErrors = stdErrors/2

        self.__ax.errorbar(data[:, 0],
                           data[:, 1],
                           yerr=stdErrors, fmt='.', markersize=3,
                           markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                           barsabove=True, capsize=2)
        
        self.__ax.set_ylabel('Ion yield (1/s)', fontdict=self.__label_font)
        self.__ax.set_xlabel('Electron energy (eV)', fontdict=self.__label_font)

        for tick in self.__ax.xaxis.get_major_ticks():
            tick.label.set_size(self.__scale_font['size'])
        
        for tick in self.__ax.yaxis.get_major_ticks():
            tick.label.set_size(self.__scale_font['size'])
    
    def shiftData(self, increment):
        if self.isLoaded():
            for set in self.__data:
                set[0] += increment

            xlim = self.__ax.get_xlim()
            ylim = self.__ax.get_ylim()
            self._zoom_to_bounds((xlim[0] + increment, xlim[1] + increment), ylim)

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
            self._zoom_to_xbounds(self.__data[0, 0], self.__data[-1, 0], *self.__ax.margins())

    def ZoomToFit(self, x_lb, x_ub, fit_index):
        if self.isLoaded():
            self._zoom_to_xbounds(x_lb, x_ub, *self.__ax.margins())

    def _zoom_to_xbounds(self, x_lb, x_ub, x_margin=0, y_margin=0):
            print(x_lb, x_ub)

            #(x_margin, y_margin) = self.__ax.margins()

            y_lb = self._find_y_min_between(x_lb, x_ub, self.getCurrentData(), self.getStdErrors())
            #y_lb = self._find_y_min_between(x_lb, x_ub, self.getCurrentData(), None)

            if y_lb is None or y_lb > 0:
                y_lb = 0
            elif np.isnan(y_lb) or np.isinf(y_lb):
                print("y_lb is ", y_lb)
                return
            
            y_ub = self._find_y_max_between(x_lb, x_ub, self.getCurrentData(), self.getStdErrors())
            #y_ub = self._find_y_max_between(x_lb, x_ub, self.getCurrentData(), None)

            if y_ub is None:
                y_ub = 1
            elif np.isnan(y_ub) or np.isinf(y_ub):
                print("y_ub is ", y_ub)
                return

            x_dev = (x_ub-x_lb) * x_margin/2
            y_dev = (y_ub - y_lb) * y_margin / 2

            self.__ax.set_xlim(x_lb - x_dev, x_ub + x_dev)
            self.__ax.set_ylim(y_lb - y_dev, y_ub + y_dev)

            #self.__ax.set_xlim(x_lb, x_ub)
            #self.__ax.set_ylim(y_lb, y_ub)
            self.draw()

    def _zoom_to_bounds(self, xbounds, ybounds, x_margin=0, y_margin=0):
        (x_lb, x_ub) = xbounds
        (y_lb, y_ub) = ybounds

        x_dev = (x_ub - x_lb) * x_margin / 2
        y_dev = (y_ub - y_lb) * y_margin / 2

        self.__ax.set_xlim(x_lb - x_dev, x_ub + x_dev)
        self.__ax.set_ylim(y_lb - y_dev, y_ub + y_dev)

        # self.__ax.set_xlim(x_lb, x_ub)
        # self.__ax.set_ylim(y_lb, y_ub)
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
                if np.isnan(y) is not True and (y_max is None or y + error > y_max):
                    y_max = y + error
            elif x > xmax:
                break

        return y_max

    def _find_y_min_between(self, xmin, xmax, data, errors):

        y_min = None
        error = 0

        for i in range(1, len(data)):
            (x, y) = data[i]
            
            if errors is not None and i < len(errors):
                error = errors[i]
            
            if xmin <= x <= xmax:
                if np.isnan(y) is not True and (y_min is None or y - error < y_min):
                    y_min = y - error
            elif x > xmax:
                break
    
        return y_min

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

        self.is_loaded_changed.emit(self.isLoaded())

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
        if self.isLoaded():
            self.__fitIndex = index

            (xlim, ylim) = self.refresh()

            self._zoom_to_bounds(xlim, ylim)
    
    def clearFits(self):
        self.__fdiFits.clear()
    
    def showErrorBars(self, showErrorBars):
        self.refresh(showErrorBars=showErrorBars)
    
    def __plotFit(self, fdiCurrent: fdi.fitDataInfo):
        fitData = fdiCurrent.getFitData()
        
        self.__ax.plot(fitData[:, 0], fitData[:, 1],
                       linestyle=self.__ls, color=self.__fc, linewidth=self.__lw)
        self.__mark_fit_data_in_plot(fdiCurrent)
        
    def __plot_combined_fit(self):
        if self.__combined_fit_exists():
    
            self.__ax.plot(self.__combined_fit_data[:, 0],
                           self.__combined_fit_data[:, 1],
                           linestyle=self.__ls, color=self.__fc, linewidth=self.__lw)
            
            for fdiCurrent in self.__fdiFits:
                if fdiCurrent.isFitted() and fdiCurrent.isDisabled() != True:
                    self.__mark_fit_data_in_plot(fdiCurrent)
    
    def __combined_fit_exists(self):
        return self.__combined_fit_data is not None and len(self.__combined_fit_data) > 0

    def isResizingEnabled(self):
        return self.__isResizing

    def setResizingEnabled(self, enabled):
        self.__isResizing = enabled

    def resizeEvent(self, event):
        if self.isResizingEnabled():
            super().resizeEvent(event)
        #print(event.)

    def __mark_fit_data_in_plot(self, fdiCurrent: fdi.fitDataInfo):

        lowerFitBound = -1
        upperFitBound = -1

        aec = 'black'
        fitareac = '#EFEFEF'
        aeareac = '#ABABAB'

        if type(fdiCurrent) is adi.AEFitDataInfo:

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

            if ub_fwhm - lb_fwhm > 0:
                self.__ax.axvspan(lb_fwhm, ub_fwhm, facecolor=aeareac, alpha=0.5)

        elif type(fdiCurrent) is pdi.polyFitDataInfo:

            lowerFitBound = fdiCurrent.getFitFrom()
            upperFitBound = fdiCurrent.getFitTo()
            print(lowerFitBound, upperFitBound)


        # mark relevant fit area
        if lowerFitBound != -1 and upperFitBound != -1:
            self.__ax.axvspan(lowerFitBound, upperFitBound, facecolor=fitareac, alpha=0.5)


    def getFigure(self):
        return self.__fig
