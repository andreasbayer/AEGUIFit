from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QCheckBox, QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal
import helplib as hl


class dataControlWidget(QWidget):
    showErrorBars_changed = pyqtSignal(bool)
    data_changed = pyqtSignal(bool)
    data_shift = pyqtSignal(float)
    load_fits = pyqtSignal(list)
    load_view = pyqtSignal(str)
    
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
        self.__all_data = None
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
        self.__all_data, self.__stdErrors, (fit_strings, view_string, data_string) = hl.readFileForFitsDataAndStdErrorAndMetaData(fileName)
        self.__data = self.__all_data[:, 0:2]

        if len(self.__data) <= 1:
            raise Exception("Not enough data in file!")

        check = self.hasStdErrors()
        
        if check:
            self.__chkShowErrorBars.setText(self.SHOW_ERROR_BARS)
        else:
            self.__chkShowErrorBars.setText(self.SHOW_ERROR_BARS_NOT_LOADED)
        
        self.__chkShowErrorBars.setEnabled(check)
        self.__chkShowErrorBars.setChecked(check)
        
        self.data_changed.emit(check)
        self.load_fits.emit(fit_strings)
        self.load_view.emit(view_string)
        
        self.load_from_data_string(data_string)
        
    def load_from_data_string(self, data_string):
        
        if data_string is not None:
            split_string = data_string.split(',')
            
            for i in range(0, len(split_string)):
                item = split_string[i].split('=')
                
                if len(item) == 2:
                    if (item[0] == 'egs'):
                        self.setEnergyShift(float(item[1]))
                    elif (item[0] == 'seb'):
                        if item[1] == '1' or item[1] == 'True':
                            self.setShowErrorBars(True)
                        elif item[1] == '0' or item[1] == 'False':
                            self.setShowErrorBars(False)
                    
    def get_data_string(self):
        return 'egs=' + str(self.getEnergyShift()) + ',seb=' + str(self.getShowErrorBars())
    
    def saveFile(self, fileName, fit_strings, view_string, data_string):
        hl.saveFilewithMetaData(fileName, self.__all_data, (fit_strings, view_string, data_string))