from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QCheckBox, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal
import helplib as hl


class dataControlWidget(QWidget):
    showErrorBars_changed = pyqtSignal(bool)
    data_changed = pyqtSignal(bool)
    data_shift = pyqtSignal(float)
    load_fits = pyqtSignal(list)
    
    SHOW_ERROR_BARS = "Show error bars"
    SHOW_ERROR_BARS_NOT_LOADED = "Show error bars (could not be calculated)"
    
    def __init__(self):
        QWidget.__init__(self)
        
        self.__lblEnergyShift = QLabel("Energy Shift:")
        self.__dsbEnergyShift = QDoubleSpinBox()
        self.__dsbEnergyShift.valueChanged.connect(self.__energyShiftChanged)
        
        self.__chkShowErrorBars = QCheckBox(self.SHOW_ERROR_BARS_NOT_LOADED)
        self.__chkShowErrorBars.stateChanged.connect(self.__chkShowErrorBars_changed)
        
        self.__mainLayout = QVBoxLayout()
        self.setLayout(self.__mainLayout)

        self.__mainLayout.addWidget(self.__lblEnergyShift)
        self.__mainLayout.addWidget(self.__dsbEnergyShift)

        self.__mainLayout.addWidget(self.__chkShowErrorBars)
        
        self.reset(False)
    
    def reset(self, enable):
        self.__energyShiftValue = 0.0
        
        self.__data = None
        self.__stdErrors = None
        
        self.__chkShowErrorBars.setCheckable(True)
        self.__chkShowErrorBars.setChecked(False)
        self.__chkShowErrorBars.setEnabled(False)
        
        self.setEnabled(enable)
    
    
    def __chkShowErrorBars_changed(self, state):
        self.__chkShowErrorBars.setCheckState(state)
        
        self.showErrorBars_changed.emit(self.getShowErrorBars())
    
    def __energyShiftChanged(self, energyShift):
        increment = energyShift - self.__energyShiftValue
        self.__energyShiftValue = energyShift
        
        self.data_shift.emit(increment)
        self.data_changed.emit(self.getShowErrorBars())
    
    #  def setData(self, data):
    #    self.__data = data
    
    def getData(self):
        return self.__data
    
    def getEnergyShift(self):
        return (self.__dsbEnergyShift.value())
    
    def setEnergyShift(self, value):
        self.__dsbEnergyShift.setValue(value)
    
    def getStdErrors(self):
        return self.__stdErrors
    
    def getMax_Energy(self):
        if self.__data is not None:
            return self.__data[-1][0]
        else:
            return None
    
    def getMin_Energy(self):
        if self.__data is not None:
            return self.__data[0][0]
        else:
            return None
    
    def getShowErrorBars(self):
        return self.__chkShowErrorBars.isChecked()
    
    def hasStdErrors(self):
        return self.__stdErrors is not None
    
    def setShowErrorBars(self, value):
        self.__chkShowErrorBars.setChecked(value)
    
    def loadFile(self, fileName):
        self.__data, self.__stdErrors, fit_strings = hl.readFileForFitsDataAndStdError(fileName)
        #self.__data, self.__stdErrors = hl.readFileForDataAndStdError(fileName)
        
        check = self.hasStdErrors()
        
        if check:
            self.__chkShowErrorBars.setText(self.SHOW_ERROR_BARS)
        else:
            self.__chkShowErrorBars.setText(self.SHOW_ERROR_BARS_NOT_LOADED)
        
        self.__chkShowErrorBars.setEnabled(check)
        self.__chkShowErrorBars.setChecked(check)
        
        self.data_changed.emit(check)
        self.load_fits.emit(fit_strings)
