from PyQt5.QtWidgets import QLabel, QPushButton, QDoubleSpinBox, QFormLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
import polyFitDataInfo as pfd
import fitHelper as fh
import fitInfoWidget as fiw
import sys

class polyFitInfoWidget(fiw.fitInfoWidget):
    FITINITIALS = "pyf"

    FitFrom_changed = pyqtSignal()
    FitTo_changed = pyqtSignal()
    Degree_changed = pyqtSignal()
    ExtendFrom_changed = pyqtSignal()
    ExtendTo_changed = pyqtSignal()


    def __init__(self, index, shift_function, parameters=None):
        fiw.fitInfoWidget.__init__(self)

        self.__polyFitDataInfo = pfd.polyFitDataInfo(index)
        self.__polyFitDataInfo.setProgressUpdateFunction(self.emitProgressUpdate)
        shift_function.connect(self.shiftData)

        self.__initLayout()

        self.reset(True)

        self.__initialized = True

        self.__connectSignals()

        if parameters is not None:
            self.init_from_parameters(parameters)

    def initialize_from_parameters(self, parameters):
        ps = parameters.split(",")

        for parameter in ps:
            (short, value) = parameter.split('=')
            if short == 'ffr':
                self.setFitFrom(float(value))
            elif short == 'fto':
                self.setFitTo(float(value))
            elif short == 'efr':
                self.setExtendFrom(float(value))
            elif short == 'eto':
                self.setExtendTo(float(value))
            elif short == 'deg':
                self.setDegree(float(value))
            elif short == 'wgt':
                if value == '1' or value == 'True':
                    self.setWeighted(True)
                else:
                    self.setWeighted(False)

    def get_fit_string(self):
        return self.FITINITIALS + ':' + \
               'ffr=' + str(round(self.getFitFrom(), 5)) + ',' +\
               'fto=' + str(round(self.getFitTo(), 5)) + ',' +\
               'efr=' + str(round(self.getExtendFrom(), 5)) + ',' +\
               'eto=' + str(round(self.getExtendTo(), 5)) + ',' +\
               'deg=' + str(self.getDegree()) + ',' +\
               'wgt=' + str(self.isWeighted())

    def isWeighted(self):
        return self.__chkWeightFit.isChecked()

    def setWeighted(self, value):
        self.__chkWeightFit.setChecked(value)

    def reset(self, enable):
      self.setEnabled(enable)

      self.__polyFitDataInfo.reset()

      self.setDegree(2)
      self.setFitFrom(0)
      self.setFitTo(sys.float_info.max)

      self.setExtendFrom(0)
      self.setExtendTo(sys.float_info.max)

      self.__cmdZoomToFitArea.setEnabled(False)

    def getDegree(self):
      return self.__dsbDegree.value()

    def setDegree(self, n):
        self.__dsbDegree.setValue(float(n))
        self.__Degree_changed()

    def setFitFrom(self, value):
        self.__dsbFitFrom.setValue(float(value))
        self.__FitFrom_changed()

    def getFitFrom(self):
      return self.__dsbFitFrom.value()

    def setFitTo(self, value):
        self.__dsbFitTo.setValue(float(value))
        self.__FitTo_changed()

    def getFitTo(self):
      return self.__dsbFitTo.value()

    def getExtendFrom(self):
        return self.__dsbExtendFrom.value()

    def setExtendFrom(self, value):
        self.__dsbExtendFrom.setValue(float(value))
        self.__ExtendFrom_changed()

    def getExtendTo(self):
        return self.__dsbExtendTo.value()

    def setExtendTo(self, value):
        self.__dsbExtendTo.setValue(float(value))
        self.__ExtendTo_changed()

    def __connectSignals(self):
        self.__dsbFitFrom.editingFinished.connect(self.__FitFrom_changed)
        self.__dsbFitTo.editingFinished.connect(self.__FitTo_changed)
        self.__dsbExtendFrom.editingFinished.connect(self.__ExtendFrom_changed)
        self.__dsbExtendTo.editingFinished.connect(self.__ExtendTo_changed)
        self.__dsbDegree.editingFinished.connect(self.__Degree_changed)
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
        self.__dsbFitFrom = QDoubleSpinBox()
        self.__dsbFitFrom.setRange(0, sys.float_info.max)
        self.__dsbFitFrom.setValue(0)
        self.__dsbFitFrom.setSingleStep(0.1)

        self.__lblFitTo = QLabel(" to ")
        self.__dsbFitTo = QDoubleSpinBox()
        self.__dsbFitTo.setSingleStep(0.1)

        self.__mainLayout.addRow(self.__lblFitFrom, self.__dsbFitFrom)
        self.__mainLayout.addRow(self.__lblFitTo, self.__dsbFitTo)

        self.__lblExtendFrom = QLabel("Extend From ")
        self.__dsbExtendFrom = QDoubleSpinBox()
        self.__dsbExtendFrom.setRange(0, sys.float_info.max)
        self.__dsbExtendFrom.setValue(0)
        self.__dsbExtendFrom.setSingleStep(0.1)

        self.__lblExtendTo = QLabel(" to ")
        self.__dsbExtendTo = QDoubleSpinBox()
        self.__dsbExtendTo.setSingleStep(0.1)

        self.__mainLayout.addRow(self.__lblExtendFrom, self.__dsbExtendFrom)
        self.__mainLayout.addRow(self.__lblExtendTo, self.__dsbExtendTo)

        self.__lblDegree = QLabel("n:")
        self.__dsbDegree = QDoubleSpinBox()
        self.__dsbDegree.setSingleStep(1)
        self.__dsbDegree.setRange(0, 100) #sys.float_info.max)
        self.__dsbDegree.setDecimals(0)

        self.__mainLayout.addRow(self.__lblDegree, self.__dsbDegree)

        self.__cmdFit = QPushButton("Fit")
        self.__cmdFit.setFixedWidth(75)
        self.__chkWeightFit = QCheckBox("Weighted")

        self.__mainLayout.addRow(self.__chkWeightFit, self.__cmdFit)

        self.__cmdZoomToFitArea = QPushButton("Zoom To Fit")
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
        return (self.getFitDataInfo() is not None) and self.getFitDataInfo().isFitted()

    def getFitDataInfo(self):
        return self.__polyFitDataInfo

    def __chkDisableFit_stateChanged(self, state):

        self.getFitDataInfo().setDisabled(state == Qt.Checked)

        self.disable_fit.emit(self.getFitDataInfo(), (state == Qt.Checked))

    def __cmdRemoveFit_clicked(self):
        self.remove_fit.emit(self.getFitDataInfo())

    def _on_set_data(self, data, stderr):
        if self.__polyFitDataInfo.is_initialized() is False:
            self.__polyFitDataInfo.setData(data)

            self.__polyFitDataInfo.setStdErr(stderr)

            self.setFitFrom(data[0][0])
            self.setFitTo(data[-1][0])

            self.setExtendFrom(data[0][0])
            self.setExtendTo(data[-1][0])

            self.__dsbFitFrom.setMinimum(data[0][0])
            self.__dsbFitFrom.setMaximum(data[-1][0])

            self.__dsbFitTo.setMinimum(data[0][0])
            self.__dsbFitTo.setMaximum(data[-1][0])

            self.__dsbExtendFrom.setMinimum(data[0][0])
            self.__dsbExtendFrom.setMaximum(data[-1][0])

            self.__dsbExtendTo.setMinimum(data[0][0])
            self.__dsbExtendTo.setMaximum(data[-1][0])

    def __cmdFit_clicked(self):
        self.fitToFunction()

    def __cmdZoomToFitArea_clicked(self):
        if self.__polyFitDataInfo.isFitted():
          lb = fh.find_ev_position(self.__polyFitDataInfo.getFitData(), self.__polyFitDataInfo.getFitFrom())
          ub = fh.find_ev_position(self.__polyFitDataInfo.getFitData(), self.__polyFitDataInfo.getFitTo())

          self.zoom_to_fit.emit(lb, ub, self.__polyFitDataInfo.get_fit_index())

    def getName(self):
        return self.__polyFitDataInfo.getName()

    def get_fit_index(self):
        return self.__polyFitDataInfo.get_fit_index()

    def __FitTo_changed(self):
        self.__polyFitDataInfo.setFitTo(self.getFitTo())
        #self.AEFrom_changed.emit()

    def __FitFrom_changed(self):
        self.__polyFitDataInfo.setFitFrom(self.getFitFrom())
        #self.AETo_changed.emit()

    def __ExtendTo_changed(self):
        self.__polyFitDataInfo.setExtendTo(self.getExtendTo())
        #self.AEFrom_changed.emit()

    def __ExtendFrom_changed(self):
        self.__polyFitDataInfo.setExtendFrom(self.getFitFrom())
        #self.AETo_changed.emit()

    def __Degree_changed(self):
        self.__polyFitDataInfo.setDegree(self.getDegree())
        self.Degree_changed.emit()

    def __chkWeightFit_stateChanged(self, state):
        self.__polyFitDataInfo.set_weighted(state == Qt.Checked)

    def resetFit(self):
        self.__polyFitDataInfo.reset()

    def shiftData(self, increment):
        self.__polyFitDataInfo.shift_fit(increment)

        self.setAEFrom(self.getAEFrom() + increment)
        self.setAETo(self.getAETo() + increment)

    def fitToFunction(self):
        msg = self.__polyFitDataInfo.fitToFunction()

        self.Post_Fit.emit(self.__polyFitDataInfo, msg)

        if msg == self.__polyFitDataInfo.SUCCESS:
          #self.__lblFoundAE.setText(self.AEFOUNDAT.format(self.__polyFitDataInfo.getFoundAE()))
          #self.__lblStdDev.setText(self.STDDEVAT.format(self.__polyFitDataInfo.getStdDeviation()))
          #self.__dsbFWHM.setValue(self.__polyFitDataInfo.getFittedFWHM())
          #self.__edtFitFunc.setText(self.__polyFitDataInfo.getFitFunc())
          #self.__cmdZoomToFitArea.setEnabled(True)
          print("success")
        else:
          self.__cmdZoomToFitArea.setEnabled(False)

        return msg, self.__polyFitDataInfo
