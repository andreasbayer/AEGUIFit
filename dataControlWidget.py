from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QCheckBox, QGroupBox
from InftyDoubleSpinBox import InftyDoubleSpinBox
from PyQt5.QtCore import pyqtSignal, Qt
import helplib as hl
import numpy as np

class dataControlWidget(QGroupBox):
    showErrorBars_changed = pyqtSignal(bool)
    ignoreFirstPoint_changed = pyqtSignal(bool)
    data_changed = pyqtSignal(bool, bool)
    data_shift = pyqtSignal(np.float64)
    load_fits = pyqtSignal(list)
    load_view = pyqtSignal(str)
    load_meta = pyqtSignal(str)
    fit_on_startup = pyqtSignal()
    
    SHOW_ERROR_BARS = "Show error bars"
    SHOW_ERROR_BARS_NOT_LOADED = "Show error bars (could not be calculated)"
    
    def __init__(self):
        QWidget.__init__(self)

        self.setTitle('Data Settings')

        self.__lblEnergyShift = QLabel("Energy Shift:")
        self.__dsbEnergyShift = InftyDoubleSpinBox()
        self.__dsbEnergyShift.editingFinished.connect(self.__energyShiftChanged)
        self.__dsbEnergyShift.setSingleStep(0.01)
        
        self.__chkShowErrorBars = QCheckBox(self.SHOW_ERROR_BARS_NOT_LOADED)
        self.__chkShowErrorBars.stateChanged.connect(self.__chkShowErrorBars_changed)

        self.__chkIgnoreFirstPoint = QCheckBox('Ignore first data point.')
        self.__chkIgnoreFirstPoint.stateChanged.connect(self.__chkIgnoreFirstPoint_changed)
        
        self.__mainLayout = QGridLayout()
        self.setLayout(self.__mainLayout)
        self.__mainLayout.setAlignment(Qt.AlignTop)

        self.__mainLayout.addWidget(self.__lblEnergyShift, 0, 0)
        self.__mainLayout.addWidget(self.__dsbEnergyShift, 0, 1)

        self.__mainLayout.addWidget(self.__chkShowErrorBars, 1, 0, 1, 2)

        self.__mainLayout.addWidget(self.__chkIgnoreFirstPoint, 2, 0, 1, 2)
        
        self.reset(False)
    
    def reset(self, enable):
        self.__data = None
        self.__all_data = None
        self.__stdErrors = None
        
        self.__chkShowErrorBars.setCheckable(True)
        self.__chkShowErrorBars.setChecked(False)
        self.__chkShowErrorBars.setEnabled(False)

        self.__chkIgnoreFirstPoint.setCheckable(True)
        self.__chkIgnoreFirstPoint.setChecked(False)
        self.__chkIgnoreFirstPoint.setEnabled(False)

        self.setEnergyShift(0.0)
        self.__prevShift = 0.0
        
        self.setEnabled(enable)
    
    def __chkShowErrorBars_changed(self, state):
        self.__chkShowErrorBars.setCheckState(state)
        self.showErrorBars_changed.emit(self.getShowErrorBars())

    def __chkIgnoreFirstPoint_changed(self, state):
        self.__chkIgnoreFirstPoint.setCheckState(state)
        self.ignoreFirstPoint_changed.emit(self.getIgnoreFirstPoint())
    
    def __energyShiftChanged(self):
        self.cause_shift()

    def cause_shift(self):
        energyShift = self.__dsbEnergyShift.value()

        increment = energyShift - self.__prevShift
        self.__prevShift = energyShift

        self.data_shift.emit(increment)
        self.data_changed.emit(self.getShowErrorBars(), self.getIgnoreFirstPoint())

    #  def setData(self, data):
    #    self.__data = data

    def getData(self):

        first_point = 0

        if self.getIgnoreFirstPoint():
            first_point = 1

        return self.__data[first_point:,]

    def getEnergyShift(self):
        return (self.__dsbEnergyShift.value())

    def setEnergyShift(self, value):
        #increment = self.__dsbEnergyShift.value() - value
        increment = value - self.__dsbEnergyShift.value()
        self.__dsbEnergyShift.setValue(value)

        #self.__shiftData(increment)
        #self.data_shift.emit(increment)

    def __shiftData(self, increment):
        try:
            if self.__data is not None:
                for set in self.__data:
                    set[0] += increment
        except Exception as e:
            print(e)


    def getStdErrors(self):
        first_point = 0

        if self.getIgnoreFirstPoint():
            first_point = 1

        return self.__stdErrors[first_point:]

    def getMax_Energy(self):
        if self.getData() is not None:
            return self.getData()[-1][0]
        else:
            return None

    def getMin_Energy(self):
        if self.getData() is not None:
            return self.getData()[0][0]
        else:
            return None
    
    def getShowErrorBars(self):
        return self.__chkShowErrorBars.isChecked()

    def setShowErrorBars(self, value):
        self.__chkShowErrorBars.setChecked(value)

    def getIgnoreFirstPoint(self):
        return self.__chkIgnoreFirstPoint.isChecked()

    def setIgnoreFirstPoint(self, value):
        self.__chkIgnoreFirstPoint.setChecked(value)
    
    def hasStdErrors(self):
        return self.__stdErrors is not None

    def loadFile(self, fileName, id_string):
        self.__all_data, self.__stdErrors, (fit_strings, view_string, data_string, meta_string), id_found =\
            hl.readFileForFitsDataAndStdErrorAndMetaData(fileName, id_string)

        #we need a copy to not save any altered data!
        self.__data = (self.__all_data[:, 0:2]).copy()

        if len(self.__data) <= 1:
            raise Exception("Not enough data in file!")
        
        if self.hasStdErrors():
            self.__chkShowErrorBars.setText(self.SHOW_ERROR_BARS)
        else:
            self.__chkShowErrorBars.setText(self.SHOW_ERROR_BARS_NOT_LOADED)
        
        self.__chkShowErrorBars.setEnabled(self.hasStdErrors())
        self.__chkShowErrorBars.setChecked(self.hasStdErrors())

        self.__chkIgnoreFirstPoint.setEnabled(True)

        self.data_changed.emit(self.hasStdErrors(), self.getIgnoreFirstPoint())
        self.load_fits.emit(fit_strings)
        self.load_view.emit(view_string)
        self.load_meta.emit(meta_string)

        self.load_from_data_string(data_string)
        self.cause_shift()

        self.fit_on_startup.emit()

        return id_found

    def load_from_data_string(self, data_string):
        if data_string is not None:
            split_string = data_string.split('\v')
            
            for i in range(0, len(split_string)):
                item = split_string[i].split('=')
                
                if len(item) == 2:
                    if (item[0] == 'egs'):
                        self.setEnergyShift(np.float64(item[1]))
                    elif item[0] == 'seb':
                        if item[1] == '1' or item[1] == 'True':
                            self.setShowErrorBars(True)
                        elif item[1] == '0' or item[1] == 'False':
                            self.setShowErrorBars(False)
                    elif item[0] == 'ifd':
                        if item[1] == '1' or item[1] == 'True':
                            self.setIgnoreFirstPoint(True)
                        elif item[1] == '0' or item[1] == 'False':
                            self.setIgnoreFirstPoint(False)

    def get_data_string(self):
        return 'egs=' + str(self.getEnergyShift()) + '\vseb=' + str(self.getShowErrorBars()) +\
               '\vifd=' + str(self.getIgnoreFirstPoint())
    
    def saveFile(self, fileName, id_string, fit_strings, view_string, data_string, meta_string):
        hl.saveFilewithMetaData(id_string, fileName, self.__all_data, (fit_strings, view_string, data_string, meta_string))
