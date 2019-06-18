from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np


class dia_goodness_of_minspan(QtWidgets.QDialog):
    def __init__(self, parent=None):
        #QtWidgets.QDialog(dia_goodness_of_minspan, self)
        super(dia_goodness_of_minspan, self).__init__()
        
        self.figure = Figure()
        
        self.canvas = FigureCanvas(self.figure)
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.lblSummary = QtWidgets.QLabel('Summary:')
        
        #self.display_statistics()
        #self.plot()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.lblSummary)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
        
        self.__dc = 'black'
        self.__fc = 'orange'
        self.__ew = 1
        self.__lw = 1.2

    def setAEs(self, aes, errs=None):
        self.AEs = aes
        self.AE_errs = errs
    
    def setMinSpans(self, minspans):
        self.minspans = minspans
        
    def setAlphas(self, alphas, errs=None):
        self.alphas = alphas
        self.alpha_errs = errs
    
    def calc_stats(self):
        avg_aes = np.average(self.AEs)
        std_aes = np.sqrt(np.sum(np.square(self.AE_errs)))

        avg_alphas = np.average(self.alphas)
        std_alphas = np.sqrt(np.sum(np.square(self.alpha_errs)))

        return u'AE = {:.3f} \u00B1 {:.3f}      Alpha = {:.3f} \u00B1 {:.3f}'.format(
            avg_aes, std_aes, avg_alphas, std_alphas)
        
        
    def plot(self):
        ax = self.figure.add_subplot(2, 1, 1)
        ax.set_title(self.calc_stats())
        ax.errorbar(self.minspans, self.AEs, yerr=None, fmt='.', markersize=3,
                           markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                           barsabove=True, capsize=2)
        #ax.set_xlabel('minspan')
        ax.set_ylabel('AE')

        
        ax = self.figure.add_subplot(2,1,2)
        ax.errorbar(self.minspans, self.alphas, yerr=None,  fmt='.', markersize=3,
                           markeredgecolor=self.__dc, markerfacecolor=self.__dc, ecolor=self.__dc, elinewidth=self.__ew,
                           barsabove=True, capsize=2)
        ax.set_xlabel('minspan')
        ax.set_ylabel('Alpha')
        
        self.canvas.draw()
