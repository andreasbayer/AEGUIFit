from PyQt5.QtWidgets import QGroupBox, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt
#from PyQt5.Qt import ali
import AEFitInfoWidget as afw
import polyFitInfoWidget as pfw
import customFitInfoWidget as cfw
import fitDataInfo as fid
from numpy import ndarray, empty
import numpy as np


class fitInfoWidgetContainer(QGroupBox):

    progressUpdate = pyqtSignal(np.float64, list)

    Post_Fit = pyqtSignal(str, fid.fitDataInfo, ndarray)
    Combined_Fit_Data_Updated = pyqtSignal(ndarray)
    zoom_to_fit = pyqtSignal(np.float64, np.float64, int)
    shift_data = pyqtSignal(np.float64)
    fit_added = pyqtSignal(fid.fitDataInfo)
    remove_fit = pyqtSignal(fid.fitDataInfo)
    disable_fit = pyqtSignal(fid.fitDataInfo)
    
    def __init__(self):
        self.__data = None
        self.__std_err = None
        self.__combined_fit_data = empty(0)
        self.__fitInfoWidgets = []
        
        QGroupBox.__init__(self)
        self.__initLayout()


    def __initLayout(self):

        self.__mainLayout = QVBoxLayout()
        self.__scrollArea = QScrollArea(self)

        self.__cbxFits = QComboBox()
        self.__cbxFits.addItem("Wannier Fit")
        self.__cbxFits.addItem("Polynomial Fit")
        #self.__cbxFits.addItem("Custom Function")
        self.__cbxFits.setVisible(True)

        self.setTitle('Fit Settings')
        
        self.__mainLayout.stretch(100)
        
        self.__cmdAddFit = QPushButton("Add Fit")
        self.__cmdAddFit.clicked.connect(self.__cmdAddFitClicked)
        self.shift_data.connect(self.__shift_combined_fit_data)
        
        self.__hbMenu = QHBoxLayout()
        self.__hbMenu.addWidget(self.__cbxFits)
        self.__hbMenu.addWidget(self.__cmdAddFit)
        self.__mainLayout.setAlignment(Qt.AlignTop)
        self.__mainLayout.addLayout(self.__hbMenu)
        self.__mainLayout.addWidget(self.__scrollArea)
        
        self.__vbFitInfoWidgets = QVBoxLayout()
        self.__scrollArea.setWidgetResizable(True)
        #self.__scrollArea.setLayout(self.__vbFitInfoWidgets)
        #self.__scrollArea.setAlignment(Qt.AlignTop)
        
        self.__widgetFrame = QFrame()
        self.__widgetFrame.setLayout(self.__vbFitInfoWidgets)
        self.__scrollArea.setWidget(self.__widgetFrame)
        self.__vbFitInfoWidgets.setAlignment(Qt.AlignTop)
        
        #self.__mainLayout.addWidget(self.__cbxFits)
        #self.__mainLayout.addWidget(self.__cmdAddFit)
        
        self.setLayout(self.__mainLayout)
        
        self.reset(False)
        
    def load_fits(self, fit_strings):
        try:
            for fit_string in fit_strings:
                item = fit_string.split(':')
                if item[0] == afw.AEFitInfoWidget.FITINITIALS:
                    new_fit = afw.AEFitInfoWidget(len(self.__fitInfoWidgets), self.shift_data)
                    self.__add_fiw(new_fit)
                    new_fit.initialize_from_parameters(item[1])
                elif item[0] == pfw.polyFitInfoWidget.FITINITIALS:
                    new_fit = pfw.polyFitInfoWidget(len(self.__fitInfoWidgets), self.shift_data)
                    self.__add_fiw(new_fit)
                    new_fit.initialize_from_parameters(item[1])
                elif item[0] == cfw.customFitInfoWidget.FITINITIALS:
                    new_fit = cfw.customFitInfoWidget(len(self.__fitInfoWidgets), self.shift_data)
                    self.__add_fiw(new_fit)
                    new_fit.initialize_from_parameters(item[1])
        except:
            return 'Error: Meta data seems to be corrupted.'

    def fit_on_startup(self):
        for fiw_i in self.__fitInfoWidgets:
            fiw_i.fitToFunction()

    def get_fit_strings(self):
        fit_strings = list()
        
        for fiw_i in self.__fitInfoWidgets:
            fit_strings.append(fiw_i.get_fit_string())
            
        return fit_strings

    def __cmdAddFitClicked(self, checked):
        self.__add_fit(self.__cbxFits.currentIndex())
        
    def __shift_combined_fit_data(self, increment):
        if self.__combined_fit_exists():
            for set in self.__combined_fit_data:
                set[0] += increment
        
    def __combined_fit_exists(self):
        return (self.__combined_fit_data is not None and len(self.__combined_fit_data) > 0)
        
    def __add_fit(self, currentIndex):
        if currentIndex == 0:
            # onset fit
            self.__add_fiw(afw.AEFitInfoWidget(len(self.__fitInfoWidgets), self.shift_data))
        elif currentIndex == 1:
            # polynomial fit
            self.__add_fiw(pfw.polyFitInfoWidget(len(self.__fitInfoWidgets), self.shift_data))
        elif currentIndex == 2:
            # custom Function
            self.__add_fiw(cfw.customFitInfoWidget(len(self.__fitInfoWidgets), self.shift_data))

    
    def __add_fiw(self, fiw):
        self.__vbFitInfoWidgets.addWidget(fiw)
        self.__fitInfoWidgets.append(fiw)
        
        self.__update_diff_data(fiw.get_fit_index())
        
        fiw.Post_Fit.connect(self.__post_fit)
        fiw.progressUpdate.connect(self.progressUpdate)
        fiw.zoom_to_fit.connect(self.__zoom_to_fit)
        fiw.remove_fit.connect(self.__remove_fit)
        fiw.disable_fit.connect(self.__disable_fit)

        fiw.setFixedWidth(self.__widgetFrame.width()-35)
        
        self.fit_added.emit(fiw.getFitDataInfo())
        
    def __disable_fit(self, fdi_Info, disable):
        self.__update_combined_fit_data()
        self.__update_diff_data(fdi_Info.get_fit_index())
        
        self.Combined_Fit_Data_Updated.emit(self.__combined_fit_data)
        self.disable_fit.emit(fdi_Info)
        
    def __remove_fit(self, fdi_Info):
        for i_fiw in reversed(self.__fitInfoWidgets):
            if i_fiw.getFitDataInfo() != fdi_Info:
                #update index
                i_fiw.getFitDataInfo().set_fit_index(i_fiw.getFitDataInfo().get_fit_index()-1)
            else:
                #emit delete_fit signal and remove fitInfoWidget from the container

                self.remove_fit.emit(fdi_Info)
                
                self.__fitInfoWidgets.remove(i_fiw)
                self.__mainLayout.removeWidget(i_fiw)
                i_fiw.deleteLater()
                
                self.__update_combined_fit_data()
                
                self.Combined_Fit_Data_Updated.emit(self.__combined_fit_data)
                break
    
    def __post_fit(self, fdi_Info, msg):
        self.__update_combined_fit_data()
        self.__update_diff_data(fdi_Info.get_fit_index()+1)
        self.Post_Fit.emit(msg, fdi_Info, self.__combined_fit_data)
    
    def __zoom_to_fit(self, lb, ub, fit_index):
        self.zoom_to_fit.emit(lb, ub, fit_index)
        #pass
    
    def __update_combined_fit_data(self):
        self.__combined_fit_data = empty(0)
        
        for fiw_i in self.__fitInfoWidgets:
            if fiw_i.isFitted() and fiw_i.isDisabled() != True:
                
                if self.__combined_fit_exists():
                    #add to new
                    fit_data = fiw_i.getFitDataInfo().getFitData()
                    
                    for i in range(0, len(fit_data)):
                        if fit_data[i][1] is not None:
                            self.__combined_fit_data[i][1] = self.__combined_fit_data[i][1] + fit_data[i][1]
                else:
                    #make new
                    self.__combined_fit_data = fiw_i.getFitDataInfo().getFitData().copy()
    
    def __update_diff_data(self, i_starting=0):
        #i_starting: first fitInfoWidget to be updated
        print("update diff data at " + str(i_starting))

        if i_starting == 0:
            diff_data = self.__data.copy()
        else:
            diff_data = self.__fitInfoWidgets[i_starting-1].getData().copy()
        
        for fiw_i in self.__fitInfoWidgets:
            print("looping at " + str(fiw_i.get_fit_index()))

            if fiw_i.get_fit_index() >= i_starting-1:
                
                if fiw_i.get_fit_index() >= i_starting:
                    fiw_i.setData(diff_data.copy(), self.__std_err)
                    print("updating for " + str(fiw_i.get_fit_index()))

                if fiw_i.isFitted() and fiw_i.isDisabled() is not True and\
                        fiw_i.get_fit_index() < len(self.__fitInfoWidgets)-1:
                    print("fiw #" + str(fiw_i.get_fit_index()) + "is fittet and not disabled and fitindex is less than number of fiw -1")
                    fit_data = fiw_i.getFitDataInfo().getFitData()
                    
                    for i in range(0, len(fit_data)):
                        if fit_data[i][1] is not None:
                            diff_data[i][1] = diff_data[i][1] - fit_data[i][1]



                    #print('Fitdata was just updated at', fiw_i.get_fit_index())

    def IgnoreFirstPoint(self, ignoreFirstPoint):
        for fiw in self.__fitInfoWidgets:
            fiw.IgnoreFirstPoint()
            self.__mainLayout.removeWidget(fiw)

    def reset(self, enable):
        self.__cmdAddFit.setEnabled(enable)
        self.__cbxFits.setEnabled(enable)
        
        for fiw in self.__fitInfoWidgets:
            fiw.deleteLater()
            self.__mainLayout.removeWidget(fiw)
            
        self.__data = None
        self.__combined_fit_data = empty(0)
        self.__fitInfoWidgets.clear()
    
    #get-set-Block
    def getData(self):
        return self.__data
    
    def get_combined_fit_data(self):
        return self.__combined_fit_data
    
    def setData(self, data):
        self.__data = data
    
    def setStdErr(self, std_err):
        self.__std_err = std_err

    def get_fit_info_widgets(self):
        return self.__fitInfoWidgets