from PyQt5.QtWidgets import QLabel, QPushButton, QDoubleSpinBox, QFormLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
import polyFitDataInfo as pfd
import fitHelper as fh
import fitInfoWidget as fiw
import sys


class polyFitInfoWidget(fiw.fitInfoWidget):

  def __init__(self, index, shift_function, parameters=None):
    fiw.fitInfoWidget.__init__(self)

    self.__polyFitDataInfo = pfd.polyFitDataInfo(index)
    self.__polyFitDataInfo.setProgressUpdateFunction(self.emitProgressUpdate)
    shift_function.connect(self.shiftData)

    self.__initLayout()

    self.reset(True)

    #self.__connectSignals()

    #if parameters is not None:
    #  self.init_from_parameters(parameters)

  # def init_from_parameters(self, parameters):
  #   #p = parameters.split("p")
  #
  #   #if len(p) == 4:
  #     self.setAEFrom(float(p[0]))
  #     self.setAETo(float(p[1]))
  #     self.setFWHM(float(p[2]))
  #
  #     self.setMinSpan(float(p[3]))
  #
  #     str = self.get_fit_string()
  #     print(str)
  #
  # def get_fit_string(self):
  #   return str(round(self.getAEFrom(), 2)) + "p" + \
  #          str(round(self.getAETo(), 2)) + "p" + \
  #          str(round(self.getFWHM(), 2)) + "p" + \
  #          str(round(self.getMinSpan(), 2))

  def reset(self, enable):
      self.setEnabled(enable)

      self.__polyFitDataInfo.reset()

      self.setDegree(0)
      self.setFrom(0)
      self.setTo(sys.float_info.max)

      self.__cmdZoomToFitArea.setEnabled(False)

  def getDegree(self):
      return self.__dsbDegree.value()

  def setDegree(self, n):
      self.__dsbDegree.setValue(float(n))
      self.__polyFitDataInfo.setDegree(n)

  def setFrom(self, value):
      self.__dsbFrom.setValue(float(value))

  def getFrom(self):
      return self.__dsbFrom.value()

  def setTo(self, value):
      self.__dsbTo.setValue(float(value))

  def getTo(self):
      return self.__dsbTo.value()

  def __connectSignals(self):
    pass
    # self.__dsbAEFrom.valueChanged.connect(self.__spbAEFrom_changed)
    # self.__dsbAETo.valueChanged.connect(self.__spbAETo_changed)
    # self.__dsbFWHM.valueChanged.connect(self.__dsbFWHM_changed)
    # self.__dsbMinSpan.valueChanged.connect(self.__dsbMinSpan_changed)
    # self.__cmdFit.clicked.connect(self.__cmdFit_clicked)
    # self.__cmdZoomToFitArea.clicked.connect(self.__cmdZoomToFitArea_clicked)
    # self.__chkDisableFit.stateChanged.connect(self.__chkDisableFit_stateChanged)
    # self.__cmdRemoveFit.clicked.connect(self.__cmdRemoveFit_clicked)

  def emitProgressUpdate(self, relation, p):
    pass
    # self.progressUpdate.emit(relation, p)

  def __initLayout(self):
    self.setCheckable(False)
    self.setChecked(True)
    self.setTitle(self.__polyFitDataInfo.getName())

    self.__mainLayout = QFormLayout()

    self.__lblFrom = QLabel("From ")
    self.__dsbFrom = QDoubleSpinBox()
    self.__dsbFrom.setRange(0, sys.float_info.max)
    self.__dsbFrom.setValue(0)
    self.__dsbFrom.setSingleStep(0.1)

    self.__lblTo = QLabel(" to ")
    self.__dsbTo = QDoubleSpinBox()
    self.__dsbTo.setSingleStep(0.1)

    self.__mainLayout.addRow(self.__lblFrom, self.__dsbFrom)
    self.__mainLayout.addRow(self.__lblTo, self.__dsbTo)

    self.__lblDegree = QLabel("n")
    self.__dsbDegree = QDoubleSpinBox()
    self.__dsbDegree.setSingleStep(1)
    self.__dsbDegree.setRange(0, 100) #sys.float_info.max)

    self.__cmdFit = QPushButton("Fit")
    self.__cmdZoomToFitArea = QPushButton("Zoom To Fit")

    self.__chkDisableFit = QCheckBox("Disable")
    self.__cmdRemoveFit = QPushButton("Remove")

    self.__mainLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)

    self.setLayout(self.__mainLayout)

    self.setEnabled(True)

  def isDisabled(self):
    return self.getFitDataInfo().isDisabled()

  # get-set-block
  def isFitted(self):
    return (self.__polyFitDataInfo is not None) and self.__polyFitDataInfo.isFitted()

  def getFitDataInfo(self):
    return self.__polyFitDataInfo

  def __chkDisableFit_stateChanged(self, state):

    self.getFitDataInfo().setDisabled(state == Qt.Checked)

    self.disable_fit.emit(self.getFitDataInfo(), (state == Qt.Checked))

  def __cmdRemoveFit_clicked(self):
    self.remove_fit.emit(self.getFitDataInfo())

  def _on_set_data(self, data):
    self.__polyFitDataInfo.setData(data)

    if self.__polyFitDataInfo.is_initialized():
      self.setFrom(data[0][0])
      self.setTo(data[-1][0])

      self.__dsbFrom.setMinimum(data[0][0])
      self.__dsbFrom.setMaximum(data[-1][0])

      self.__dsbTo.setMinimum(data[0][0])
      self.__dsbTo.setMaximum(data[-1][0])

  def __cmdFit_clicked(self):
    self.fitToFunction()

  def __cmdZoomToFitArea_clicked(self):
    if self.__polyFitDataInfo.isFitted():
      lb = fh.find_ev_position(self.__polyFitDataInfo.getFitData(), self.__polyFitDataInfo.getFitRelFrom())
      ub = fh.find_ev_position(self.__polyFitDataInfo.getFitData(), self.__polyFitDataInfo.getFitRelTo())

      self.zoom_to_fit.emit(lb, ub, self.__polyFitDataInfo.get_fit_index())

  def getName(self):
    return self.__polyFitDataInfo.getName()

  def get_fit_index(self):
    return self.__polyFitDataInfo.get_fit_index()

  def __spbAEFrom_changed(self):
    self.__polyFitDataInfo.setAEFrom(self.getAEFrom())
    self.AEFrom_changed.emit()

  def __spbAETo_changed(self):
    self.__polyFitDataInfo.setAETo(self.getAETo())
    self.AETo_changed.emit()

  def __dsbFWHM_changed(self):
    self.__polyFitDataInfo.setFWHM(self.getFWHM())
    self.FWHM_changed.emit()

  def __dsbMinSpan_changed(self):
    self.__polyFitDataInfo.setMinspan(self.getMinSpan())
    self.minspan_changed.emit()

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
      self.__lblFoundAE.setText(self.AEFOUNDAT.format(self.__polyFitDataInfo.getFoundAE()))
      self.__lblStdDev.setText(self.STDDEVAT.format(self.__polyFitDataInfo.getStdDeviation()))
      self.__dsbFWHM.setValue(self.__polyFitDataInfo.getFittedFWHM())
      self.__edtFitFunc.setText(self.__polyFitDataInfo.getFitFunc())
      self.__cmdZoomToFitArea.setEnabled(True)
    else:
      self.__cmdZoomToFitArea.setEnabled(False)

    return msg, self.__polyFitDataInfo
