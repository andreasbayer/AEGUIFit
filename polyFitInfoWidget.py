from PyQt5.QtWidgets import QLabel, QPushButton, QFormLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
from InftyDoubleSpinBox import InftyDoubleSpinBox
import polyFitDataInfo as pfd
import fitHelper as fh
import fitInfoWidget as fiw
import sys
import numpy as np

class polyFitInfoWidget(fiw.fitInfoWidget):
    FITINITIALS = "pyf"

    FitFrom_changed = pyqtSignal()
    FitTo_changed = pyqtSignal()
    Degree_changed = pyqtSignal()
    Degree_of_cont_changed = pyqtSignal()

    def __init__(self, index, shift_function, parameters=None):
        fiw.fitInfoWidget.__init__(self)

        self.__polyFitDataInfo = pfd.polyFitDataInfo(index)
        self.__polyFitDataInfo.setProgressUpdateFunction(self.emitProgressUpdate)
        shift_function.connect(self.shiftData)

        self.__initLayout()
        self.__connectSignals()
        self.reset(True)

        self.__initialized = True

        if parameters is not None:
            self.initialize_from_parameters(parameters)

    def initialize_from_parameters(self, parameters):
        ps = parameters.split('\v')

        for parameter in ps:
            (short, value) = parameter.split('=')
            if short == 'ffr':
                self.setFitFrom(np.float64(value))
            elif short == 'fto':
                self.setFitTo(np.float64(value))
            elif short == 'deg':
                self.setDegree(np.float64(value))
            elif short == 'doc':
                self.setDegreeOfCont(np.float64(value))
            elif short == 'wgt':
                print('wgt', value)
                if value == '1' or value == 'True':
                    self.setWeighted(True)
                else:
                    self.setWeighted(False)

    def get_fit_string(self):
        return self.FITINITIALS + ':' + \
               'ffr=' + str(round(self.getFitFrom(adjusted_for_shift=True), 5)) + '\v' +\
               'fto=' + str(round(self.getFitTo(adjusted_for_shift=True), 5)) + '\v' +\
               'deg=' + str(self.getDegree()) + '\v' +\
               'doc=' + str(self.getDegreeOfCont()) + '\v' +\
               'wgt=' + str(self.isWeighted())

    def isWeighted(self):
        return self.__chkWeightFit.isChecked()

    def setWeighted(self, value):
        self.__chkWeightFit.setChecked(value)
        print('setWeighted', value)

    def reset(self, enable):
      self.setEnabled(enable)

      self.__polyFitDataInfo.reset()

      self.setDegree(1)
      self.setDegreeOfCont(1)
      self.setFitFrom(0)
      self.setFitTo(sys.float_info.max)

      self.setWeighted(True)

      self.__cmdZoomToFitArea.setEnabled(False)

      self.setPostFitFunctionsEnabled(False)

    def getDegree(self):
      return self.__dsbDegree.value()

    def setDegree(self, n):
        self.__dsbDegree.setValue(np.float64(n))
        self.__Degree_changed()

    def getDegreeOfCont(self):
        return self.__dsbDegreeOfCont.value()

    def setDegreeOfCont(self, n):
        self.__dsbDegreeOfCont.setValue(np.float64(n))
        self.__Degree_of_cont_changed()

    def setFitFrom(self, value):
        self.__dsbFitFrom.setValue(np.float64(value))
        self.getFitDataInfo().setFitFrom(np.float64(value))

    def getFitFrom(self, adjusted_for_shift=False):
        return self.getFitDataInfo().getFitFrom(adjusted_for_shift)

    def setFitTo(self, value):
        self.__dsbFitTo.setValue(np.float64(value))
        self.getFitDataInfo().setFitTo(np.float64(value))

    def getFitTo(self, adjusted_for_shift=False):
      return self.getFitDataInfo().getFitTo(adjusted_for_shift)

    def __connectSignals(self):
        self.__dsbFitFrom.editingFinished.connect(self.__FitFrom_changed)
        self.__dsbFitTo.editingFinished.connect(self.__FitTo_changed)
        self.__dsbDegree.editingFinished.connect(self.__Degree_changed)
        self.__dsbDegreeOfCont.editingFinished.connect(self.__Degree_of_cont_changed)
        self.__cmdFit.clicked.connect(self.__cmdFit_clicked)
        self.__cmdZoomToFitArea.clicked.connect(self.__cmdZoomToFitArea_clicked)
        self.__chkDisableFit.stateChanged.connect(self.__chkDisableFit_stateChanged)
        self.__chkWeightFit.stateChanged.connect(self.__chkWeightFit_stateChanged)
        self.__cmdRemoveFit.clicked.connect(self.__cmdRemoveFit_clicked)

    def emitProgressUpdate(self, relation, p):
        pass
        # self.progressUpdate.emit(relation, p)

    def __initLayout(self):
        self.setCheckable(False)
        self.setChecked(True)
        self.setTitle(self.__polyFitDataInfo.getName())

        self.__mainLayout = QFormLayout()

        self.__lblFitFrom = QLabel("Fit From ")
        self.__dsbFitFrom = InftyDoubleSpinBox(min=0)
        self.__dsbFitFrom.setValue(0)
        self.__dsbFitFrom.setSingleStep(0.1)

        self.__lblFitTo = QLabel(" to ")
        self.__dsbFitTo = InftyDoubleSpinBox()
        self.__dsbFitTo.setSingleStep(0.1)

        self.__mainLayout.addRow(self.__lblFitFrom, self.__dsbFitFrom)
        self.__mainLayout.addRow(self.__lblFitTo, self.__dsbFitTo)

        self.__lblDegree = QLabel("Degree:")
        self.__dsbDegree = InftyDoubleSpinBox(min=0, max=100)
        self.__dsbDegree.setSingleStep(1)
        self.__dsbDegree.setDecimals(0)

        self.__mainLayout.addRow(self.__lblDegree, self.__dsbDegree)

        self.__lblDegreeOfCont = QLabel("Degree of continuation:")
        self.__dsbDegreeOfCont = InftyDoubleSpinBox(min=0, max=100)
        self.__dsbDegreeOfCont.setSingleStep(1)
        self.__dsbDegreeOfCont.setDecimals(0)

        self.__mainLayout.addRow(self.__lblDegreeOfCont, self.__dsbDegreeOfCont)

        self.__lblFitParameters = QLabel("Fit parameters:")
        self.__lblFitParValues = QLabel("")

        self.__mainLayout.addRow(self.__lblFitParameters)
        self.__mainLayout.addRow(self.__lblFitParValues)


        self.__cmdFit = QPushButton("Fit")
        self.__cmdFit.setFixedWidth(75)
        self.__chkWeightFit = QCheckBox("Weighted")

        self.__mainLayout.addRow(self.__chkWeightFit, self.__cmdFit)

        self.__cmdZoomToFitArea = QPushButton("Zoom To Fit")
        self.__cmdZoomToFitArea.setFixedWidth(75)

        self.__mainLayout.addRow(self.__cmdZoomToFitArea)

        self.__chkDisableFit = QCheckBox("Disable")
        self.__cmdRemoveFit = QPushButton("Remove")

        self.__mainLayout.addRow(self.__chkDisableFit, self.__cmdRemoveFit)
        self.__mainLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)

        self.setLayout(self.__mainLayout)

        self.setEnabled(True)

    def isDisabled(self):
        return self.getFitDataInfo().isDisabled()

    # get-set-block
    def isFitted(self):
        return (self.getFitDataInfo() is not None) and self.getFitDataInfo().isFitted()

    def getFitDataInfo(self):
        return self.__polyFitDataInfo

    def __chkDisableFit_stateChanged(self, state):

        self.getFitDataInfo().setDisabled(state == Qt.Checked)

        self.disable_fit.emit(self.getFitDataInfo(), (state == Qt.Checked))

    def __cmdRemoveFit_clicked(self):
        self.remove_fit.emit(self.getFitDataInfo())

    def __cmdZoomToFitArea_clicked(self):
        if self.getFitDataInfo().isFitted():
            lb = self.getFitDataInfo().getFitFrom()
            ub = self.getFitDataInfo().getFitTo()

            self.zoom_to_fit.emit(lb, ub, self.getFitDataInfo().get_fit_index())

    def _pre_set_data(self, data, stderr):
        if self.__polyFitDataInfo.is_initialized() is False:
            self.__polyFitDataInfo.setStdErr(stderr)

            self.setFitFrom(data[0][0])
            self.setFitTo(data[-1][0])

            self.__dsbFitFrom.setMinimum(data[0][0])
            self.__dsbFitFrom.setMaximum(data[-1][0])

            self.__dsbFitTo.setMinimum(data[0][0])
            self.__dsbFitTo.setMaximum(data[-1][0])

    def __cmdFit_clicked(self):
        self.fitToFunction()

    def setPostFitFunctionsEnabled(self, enabled):
        self.__cmdZoomToFitArea.setEnabled(enabled)

    def getName(self):
        return self.__polyFitDataInfo.getName()

    def get_fit_index(self):
        return self.__polyFitDataInfo.get_fit_index()

    def __FitTo_changed(self):
        self.__polyFitDataInfo.setFitTo(self.__dsbFitTo.value())
        #self.AEFrom_changed.emit()

    def __FitFrom_changed(self):
        self.__polyFitDataInfo.setFitFrom(self.__dsbFitFrom.value())

    def __Degree_changed(self):

        n = self.__dsbDegree.value()

        self.__polyFitDataInfo.setDegree(n)
        self.Degree_changed.emit()

        self.__dsbDegreeOfCont.setMaximum(n)

    def __Degree_of_cont_changed(self):

        n_cont = self.__dsbDegreeOfCont.value()

        self.__polyFitDataInfo.setDegreeOfContinuation(n_cont)
        self.Degree_of_cont_changed.emit()

    def __chkWeightFit_stateChanged(self, state):
        self.__polyFitDataInfo.set_weighted(state == Qt.Checked)

    def ignoreFirstPoint(self, IgnoreFirstPoint):
        pass


    def resetFit(self):
        self.__polyFitDataInfo.reset()

    def shiftData(self, increment):
        self.__polyFitDataInfo.shift_fit(increment)

        self.__dsbFitFrom.setMinimum(self.__dsbFitFrom.minimum() + increment)
        self.__dsbFitFrom.setMaximum(self.__dsbFitFrom.maximum() + increment)

        self.__dsbFitTo.setMinimum(self.__dsbFitTo.minimum() + increment)
        self.__dsbFitTo.setMaximum(self.__dsbFitTo.maximum() + increment)

        self.setFitFrom(self.getFitFrom() + increment)
        self.setFitTo(self.getFitTo() + increment)

    def fitToFunction(self):
        msg = self.__polyFitDataInfo.fitToFunction()

        self.Post_Fit.emit(self.__polyFitDataInfo, msg)

        if msg == self.__polyFitDataInfo.SUCCESS:
            print("success")

            self.__lblFitParValues.setText(self.getFitDataInfo().get_fit_info_string())

            self.setPostFitFunctionsEnabled(True)
        else:

            self.__lblFitParValues.setText('')
            self.setPostFitFunctionsEnabled(False)

        return msg, self.__polyFitDataInfo
