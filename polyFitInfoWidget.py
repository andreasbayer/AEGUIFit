from PyQt5.QtWidgets import QLabel, QPushButton, QFormLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
from InftyDoubleSpinBox import InftyDoubleSpinBox
import polyFitDataInfo as pfd
import fitHelper as fh
import fitInfoWidget as fiw
import sys

class polyFitInfoWidget(fiw.fitInfoWidget):
    FITINITIALS = "pyf"

    FitFrom_changed = pyqtSignal()
    FitTo_changed = pyqtSignal()
    Degree_changed = pyqtSignal()

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
            self.initialize_from_parameters(parameters)

    def initialize_from_parameters(self, parameters):
        ps = parameters.split('\t')

        for parameter in ps:
            (short, value) = parameter.split('=')
            if short == 'ffr':
                self.setFitFrom(float(value))
            elif short == 'fto':
                self.setFitTo(float(value))
            elif short == 'deg':
                self.setDegree(float(value))
            elif short == 'wgt':
                print('wgt', value)
                if value == '1' or value == 'True':
                    self.setWeighted(True)
                else:
                    self.setWeighted(False)

    def get_fit_string(self):
        return self.FITINITIALS + ':' + \
               'ffr=' + str(round(self.getFitFrom(), 5)) + '\t' +\
               'fto=' + str(round(self.getFitTo(), 5)) + '\t' +\
               'deg=' + str(self.getDegree()) + '\t' +\
               'wgt=' + str(self.isWeighted())

    def isWeighted(self):
        return self.__chkWeightFit.isChecked()

    def setWeighted(self, value):
        self.__chkWeightFit.setChecked(value)
        print('setWeighted', value)

    def reset(self, enable):
      self.setEnabled(enable)

      self.__polyFitDataInfo.reset()

      self.setDegree(2)
      self.setFitFrom(0)
      self.setFitTo(sys.float_info.max)

      self.setWeighted(True)

      self.__cmdZoomToFitArea.setEnabled(False)

      self.setPostFitFunctionsEnabled(False)

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

    def __connectSignals(self):
        self.__dsbFitFrom.editingFinished.connect(self.__FitFrom_changed)
        self.__dsbFitTo.editingFinished.connect(self.__FitTo_changed)
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
        self.__dsbFitFrom = InftyDoubleSpinBox(min=0)
        self.__dsbFitFrom.setValue(0)
        self.__dsbFitFrom.setSingleStep(0.1)

        self.__lblFitTo = QLabel(" to ")
        self.__dsbFitTo = InftyDoubleSpinBox()
        self.__dsbFitTo.setSingleStep(0.1)

        self.__mainLayout.addRow(self.__lblFitFrom, self.__dsbFitFrom)
        self.__mainLayout.addRow(self.__lblFitTo, self.__dsbFitTo)

        self.__lblDegree = QLabel("n:")
        self.__dsbDegree = InftyDoubleSpinBox(min=0, max=100)
        self.__dsbDegree.setSingleStep(1)
        self.__dsbDegree.setDecimals(0)

        self.__mainLayout.addRow(self.__lblDegree, self.__dsbDegree)

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

    def _on_set_data(self, data, stderr):
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
        self.__polyFitDataInfo.setFitTo(self.getFitTo())
        #self.AEFrom_changed.emit()

    def __FitFrom_changed(self):
        self.__polyFitDataInfo.setFitFrom(self.getFitFrom())
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

        self.setFitFrom(self.getFitFrom() + increment)
        self.setFitTo(self.getFitTo() + increment)

    def fitToFunction(self):
        msg = self.__polyFitDataInfo.fitToFunction()

        self.Post_Fit.emit(self.__polyFitDataInfo, msg)

        if msg == self.__polyFitDataInfo.SUCCESS:
            print("success")

            parstring = ""
            p = self.getFitDataInfo().getParameters()
            residuals = self.getFitDataInfo().getResiduals()
            for i in reversed(range(0, len(p))):
                digits_of_error = 2

                par_str, err_str = fh.roundToErrorStrings(p[i], residuals[i], digits_of_error)

                parstring += 'a<sub>' + str(round(i)) + '</sub>: ' + par_str + ' &plusmn; ' + err_str
                if i >= 0:
                    parstring += '<br>'

            self.__lblFitParValues.setText(parstring)

            self.setPostFitFunctionsEnabled(True)
        else:

            self.__lblFitParValues.setText('')
            self.setPostFitFunctionsEnabled(False)

        return msg, self.__polyFitDataInfo
