from PyQt5.QtWidgets import QWidget, QGroupBox
from PyQt5.QtCore import pyqtSignal
import fitDataInfo as fdi

class fitInfoWidget(QGroupBox):
    
    Post_Fit = pyqtSignal(fdi.fitDataInfo, str)
    zoom_to_fit = pyqtSignal(float, float, int)
    progressUpdate = pyqtSignal(float, list)
    disable_fit = pyqtSignal(fdi.fitDataInfo, bool)
    remove_fit = pyqtSignal(fdi.fitDataInfo)
    
    #implement:
    # relevancy for diff-data
    # fit only relevant in area
    # show fit specific data (like ae, fwhm, minspan)
    
    def __init__(self):
        QGroupBox.__init__(self)
        self.__initLayout()
        
        self.__data = None
        self.__std_err = None
        
        #self.__index = index
        
        #self.reset(False)
        
        #self.__connectSignals()
        
    def init_from_parameters(self):
        pass
    
    def get_fit_string(self):
        return " "
    
    def reset(self, enable):
        self.setEnabled(enable)
        self.__cmdZoomToFitArea.setEnabled(False)
    
    def __connectSignals(self):
        self.__cmdFit.clicked.connect(self.__cmdFit_clicked)
        self.__cmdZoomToFitArea.clicked.connect(self.__cmdZoomToFitArea_clicked)
    
    def emitProgressUpdate(self, relation, p):
        self.progressUpdate.emit(relation, p)
    
    def __initLayout(self):
        pass
    
    def get_fit_index(self):
        pass
    
    # get-set-block
    def isFitted(self):
        pass
    
    def isDisabled(self):
        pass
    
    def getFitDataInfo(self):
        pass
        #return self.__AEFitDataInfo
    
    def getData(self):
        return self.__data
    
    def is_initialized(self):
        return (self.__data is None)
    
    def setData(self, data, std_err):
        self._on_set_data(data, std_err)
        self.__data = data
        self.__std_err = std_err

    def _on_set_data(self, data, std_err):
        pass
    
    def getName(self):
        pass
    
    # Signals
    def __cmdFit_clicked(self):
        self.fitToFunction()
        
    def resetFit(self):
        pass
        
    def shiftData(self, increment):
        self.__AEFitDataInfo.shift_fit(increment)

        self.setAEFrom(self.getAEFrom() + increment)
        self.setAETo(self.getAETo() + increment)
    
    def fitToFunction(self):
        pass

