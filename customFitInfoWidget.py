from PyQt5.QtWidgets import QLabel, QPushButton, QFormLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
import customFitDataInfo as cfd
import fitHelper as fh
import fitInfoWidget as fiw
import sys
from InftyDoubleSpinBox import InftyDoubleSpinBox
import numpy as np

class customFitInfoWidget(fiw.fitInfoWidget):
    FITINITIALS = "cus"

    DomainFrom_changed = pyqtSignal()
    DomainTo_changed = pyqtSignal()
    FunctionStr_changed = pyqtSignal()

    def __init__(self, index, shift_function, parameters=None):
        fiw.fitInfoWidget.__init__(self)

        self.__customFitDataInfo = cfd.customFitDataInfo(index)
        self.__customFitDataInfo.setProgressUpdateFunction(self.emitProgressUpdate)
        shift_function.connect(self.shiftData)

        self.__initLayout()

        self.reset(True)

        self.__initialized = True

        self.__connectSignals()

        if parameters is not None:
            self.initialize_from_parameters(parameters)

    def initialize_from_parameters(self, parameters):
        ps = parameters.split('\v')

        for parameter in ps:
            (short, value) = parameter.split('=')
            if short == 'rfr':
                self.setDomainFrom(np.float64(value))
            elif short == 'rto':
                self.setDomainTo(np.float64(value))
            elif short == 'fst':
                self.setFunctionStr(np.float64(value))

    def get_fit_string(self):
        return self.FITINITIALS + ':' + \
               'rfr=' + str(round(self.getDomainFrom(), 5)) + '\v' +\
               'rto=' + str(round(self.getDomainTo(), 5)) + '\v' +\
               'fst=' + self.getFunctionStr()

    def isWeighted(self):
        return self.__chkWeightFit.isChecked()

    def setWeighted(self, value):
        self.__chkWeightFit.setChecked(value)

    def reset(self, enable):
      self.setEnabled(enable)

      self.getFitDataInfo().reset()

      self.setDomainFrom(0)
      self.setDomainTo(sys.float_info.max)

      self.setFunctionStr('')

      self.__cmdZoomToFitArea.setEnabled(False)

    def getDomainFrom(self):
        return self.__dsbDomainFrom.value()

    def setDomainFrom(self, value):
        self.__dsbDomainFrom.setValue(np.float64(value))
        self.__DomainFrom_changed()

    def getDomainTo(self):
        return self.__dsbDomainTo.value()

    def setDomainTo(self, value):
        self.__dsbDomainTo.setValue(np.float64(value))
        self.__DomainTo_changed()

    def getFunctionStr(self):
        return self.__edtFunctionStr.text()

    def setFunctionStr(self, value):
        self.__edtFunctionStr.setText(value)
        self.__FunctionStr_changed()

    def __connectSignals(self):
        self.__dsbDomainFrom.editingFinished.connect(self.__DomainFrom_changed)
        self.__dsbDomainTo.editingFinished.connect(self.__DomainTo_changed)
        self.__edtFunctionStr.editingFinished.connect(self.__FunctionStr_changed)
        self.__cmdFit.clicked.connect(self.__cmdFit_clicked)
        self.__cmdZoomToFitArea.clicked.connect(self.__cmdZoomToFitArea_clicked)
        self.__chkDisableFit.stateChanged.connect(self.__chkDisableFit_stateChanged)
        self.__cmdRemoveFit.clicked.connect(self.__cmdRemoveFit_clicked)

    def emitProgressUpdate(self, relation, p):
        pass
        # self.progressUpdate.emit(relation, p)

    def __initLayout(self):
        self.setCheckable(False)
        self.setChecked(True)
        self.setTitle(self.getFitDataInfo().getName())

        self.__mainLayout = QFormLayout()

        self.__lblDomainFrom = QLabel("Domain From ")
        self.__dsbDomainFrom = InftyDoubleSpinBox()
        self.__dsbDomainFrom.setRange(0, sys.float_info.max)
        self.__dsbDomainFrom.setValue(0)
        self.__dsbDomainFrom.setSingleStep(0.1)

        self.__lblDomainTo = QLabel(" to ")
        self.__dsbDomainTo = InftyDoubleSpinBox()
        self.__dsbDomainTo.setSingleStep(0.1)

        self.__mainLayout.addRow(self.__lblDomainFrom, self.__dsbDomainFrom)
        self.__mainLayout.addRow(self.__lblDomainTo, self.__dsbDomainTo)

        self.__lblFunctionStr = QLabel("Python function:")
        self.__lblPreFuncStr = QLabel("x: ")
        self.__edtFunctionStr = QLineEdit()

        self.__mainLayout.addRow(self.__lblFunctionStr)
        self.__mainLayout.addRow(self.__lblPreFuncStr, self.__edtFunctionStr)

        self.__cmdFit = QPushButton("Fit")
        self.__cmdFit.setFixedWidth(75)

        self.__mainLayout.addRow(self.__cmdFit)

        self.__cmdZoomToFitArea = QPushButton("Zoom To Domain Area")
        self.__cmdZoomToFitArea.setFixedWidth(75)

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
        return (self.__customFitDataInfo is not None) and self.__customFitDataInfo.isFitted()

    def getFitDataInfo(self):
        return self.__customFitDataInfo

    def __chkDisableFit_stateChanged(self, state):

        self.getFitDataInfo().setDisabled(state == Qt.Checked)

        self.disable_fit.emit(self.getFitDataInfo(), (state == Qt.Checked))

    def __cmdRemoveFit_clicked(self):
        self.remove_fit.emit(self.getFitDataInfo())

    def _on_set_data(self, data, stderr):
        if self.__customFitDataInfo.is_initialized() is False:
            self.setDomainFrom(data[0][0])
            self.setDomainTo(data[-1][0])

            self.__dsbDomainFrom.setMinimum(data[0][0])
            self.__dsbDomainFrom.setMaximum(data[-1][0])

            self.__dsbDomainTo.setMinimum(data[0][0])
            self.__dsbDomainTo.setMaximum(data[-1][0])

    def __cmdFit_clicked(self):
        self.fitToFunction()

    def __cmdZoomToFitArea_clicked(self):
        if self.getFitDataInfo().isFitted():
          lb = fh.find_ev_position(self.getFitDataInfo().getFitData(), self.getFitDataInfo().getDomainFrom())
          ub = fh.find_ev_position(self.getFitDataInfo().getFitData(), self.getFitDataInfo().getDomainTo())

          self.zoom_to_fit.emit(lb, ub, self.getFitDataInfo().get_fit_index())

    def getName(self):
        return self.getFitDataInfo().getName()

    def get_fit_index(self):
        return self.getFitDataInfo().get_fit_index()

    def __DomainTo_changed(self):
        self.getFitDataInfo().setDomainTo(self.getDomainTo())
        #self.AEFrom_changed.emit()

    def __DomainFrom_changed(self):
        self.getFitDataInfo().setDomainFrom(self.getDomainFrom())
        #self.AETo_changed.emit()

    def __FunctionStr_changed(self):
        self.getFitDataInfo().setFunctionStr(self.getFunctionStr())
        #self.Degree_changed.emit()

    def __chkWeightFit_stateChanged(self, state):
        # won't be relevant here as the custom function will not be fittet
        self.getFitDataInfo().set_weighted(state == Qt.Checked)

    def resetFit(self):
        self.getFitDataInfo().reset()

    def shiftData(self, increment):
        self.getFitDataInfo().shift_fit(increment)

        self.setDomainFrom(self.getDomainFrom() + increment)
        self.setDomainTo(self.getDomainTo() + increment)

    def fitToFunction(self):
        # fit to function will just produce y-values to the datas x-values inside
        msg = self.getFitDataInfo().fitToFunction()

        self.Post_Fit.emit(self.getFitDataInfo(), msg)

        if msg == self.getFitDataInfo().SUCCESS:
          #self.__lblFoundAE.setText(self.AEFOUNDAT.format(self.getFitDataInfo().getFoundAE()))
          #self.__lblStdDev.setText(self.STDDEVAT.format(self.getFitDataInfo().getStdDeviation()))
          #self.__dsbFWHM.setValue(self.getFitDataInfo().getFittedFWHM())
          #self.__edtFitFunc.setText(self.getFitDataInfo().getFitFunc())
          #self.__cmdZoomToFitArea.setEnabled(True)
          print("success")
        else:
          self.__cmdZoomToFitArea.setEnabled(False)

        return msg, self.getFitDataInfo()
