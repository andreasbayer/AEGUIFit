from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np


class dia_goodness_of_minspan(QtWidgets.QDialog):
    def __init__(self, parent=None):
        #QtWidgets.QDialog(dia_goodness_of_minspan, self)
        super(dia_goodness_of_minspan, self).__init__()
        
        self.setFixedHeight(800)
        self.setFixedWidth(650)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.chk_show_errorbars = QtWidgets.QCheckBox('Show error bars')
        self.chk_show_errorbars.setChecked(True)
        self.chk_show_errorbars.stateChanged.connect(self.show_errorbars_changed)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.chk_show_errorbars)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        self.__dc = 'black'
        self.__fc = 'orange'
        self.__ew = 1
        self.__lw = 1.2

        self.yo_ax = self.figure.add_subplot(4, 1, 1)
        self.ae_ax = self.figure.add_subplot(4, 1, 2)
        self.sf_ax = self.figure.add_subplot(4, 1, 3)
        self.al_ax = self.figure.add_subplot(4, 1, 4)

    def show_errorbars_changed(self, state):
        self.plot(show_error_bars=self.chk_show_errorbars.isChecked())

    def setAEs(self, aes, errs=None):
        self.AEs = aes
        self.AE_errs = errs
    
    def setMinSpans(self, minspans):
        self.minspans = minspans
        
    def setAlphas(self, alphas, errs=None):
        self.alphas = alphas
        self.alpha_errs = errs
        
    def setScaleFactors(self, scale_factors, errs=None):
        self.scale_factors = scale_factors
        self.scale_factor_errs = errs
        
    def setYOffset(self, y_offsets, errs):
        self.y_offsets = y_offsets
        self.y_offset_errs = errs
    
    def calc_stats(self):
        avg_yos = np.average(self.y_offsets)
        std_yos = np.sqrt(np.sum(np.square(self.y_offset_errs))) / len(self.y_offset_errs)
        
        avg_aes = np.average(self.AEs)
        std_aes = np.sqrt(np.sum(np.square(self.AE_errs)))/len(self.AE_errs)

        avg_sfs = np.average(self.scale_factors)
        std_sfs = np.sqrt(np.sum(np.square(self.scale_factor_errs))) / len(self.scale_factor_errs)

        avg_alphas = np.average(self.alphas)
        std_alphas = np.sqrt(np.sum(np.square(self.alpha_errs)))/len(self.alpha_errs)

        return u'Y Offset = {:.3f} \u00B1 {:.3f}   AE = {:.3f} \u00B1 {:.3f}\n Scale factor = {:.3f} \u00B1 {:.3f}   Alpha = {:.3f} \u00B1 {:.3f}'.format(
            avg_yos, std_yos, avg_aes, std_aes, avg_sfs, std_sfs, avg_alphas, std_alphas)
        
        
    def plot(self, show_error_bars=None):
        
        if show_error_bars is None:
            show_error_bars = self.chk_show_errorbars.isChecked()
        
        if show_error_bars:
            yo_errs = self.y_offset_errs
            ae_errs = self.AE_errs
            sf_errs = self.scale_factor_errs
            al_errs = self.alpha_errs
        else:
            yo_errs = None
            ae_errs = None
            sf_errs = None
            al_errs = None
            
        self.yo_ax.clear()
        self.ae_ax.clear()
        self.sf_ax.clear()
        self.al_ax.clear()
        
        self.yo_ax.set_ylabel('Y-Offset')
        self.ae_ax.set_ylabel('AE')
        self.sf_ax.set_ylabel('Scale Factor')
        self.al_ax.set_ylabel('Alpha')

        self.al_ax.set_xlabel('Min Span')

        
        self.yo_ax.set_title(self.calc_stats())
        
        self.yo_ax.errorbar(self.minspans, self.y_offsets, yerr=yo_errs, fmt='.', markersize=3,
                            markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                            barsabove=True, capsize=2)
        
        self.ae_ax.errorbar(self.minspans, self.AEs, yerr=ae_errs,  fmt='.', markersize=3,
                            markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                            barsabove=True, capsize=2)
        

        self.sf_ax.errorbar(self.minspans, self.scale_factors, yerr=sf_errs, fmt='.', markersize=3,
                         markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                         barsabove=True, capsize=2)
        

        self.al_ax.errorbar(self.minspans, self.alphas, yerr=al_errs, fmt='.', markersize=3,
                         markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                         barsabove=True, capsize=2)
        
        self.canvas.draw()
        self.adjustSize()
