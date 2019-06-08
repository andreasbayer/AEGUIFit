from PyQt5.QtWidgets import QLabel, QPushButton, QDoubleSpinBox, QFormLayout, QLineEdit, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
import customFitDataInfo as cfd
import fitHelper as fh
import fitInfoWidget as fiw


class customFitInfoWidget(fiw.fitInfoWidget):

  def __init__(self, index, shift_function, parameters=None):
    fiw.fitInfoWidget.__init__(self)

    self.__customFitDataInfo = cfd.customFitDataInfo(index)
    self.__customFitDataInfo.setProgressUpdateFunction(self.emitProgressUpdate)
    shift_function.connect(self.shiftData)

    self.__initLayout()

    #self.reset(True)

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
    pass
    #
    # self.setEnabled(enable)
    #
    # self.__AEFitDataInfo.reset()
    #
    # self.setFWHM(0.3)
    # self.setMinSpan(3)
    #
    # self.__cmdZoomToFitArea.setEnabled(False)

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
    pass
    # self.setCheckable(False)
    # self.setChecked(True)
    # self.setTitle(self.__AEFitDataInfo.getName())
    #
    # self.__mainLayout = QFormLayout()
    #
    # self.__lblAEFrom = QLabel("AE from ")
    # self.__dsbAEFrom = QDoubleSpinBox()
    # self.__dsbAEFrom.setRange(0, sys.float_info.max)
    # self.__dsbAEFrom.setValue(0)
    # self.__dsbAEFrom.setSingleStep(0.1)
    #
    # self.__lblAETo = QLabel(" to ")
    # self.__dsbAETo = QDoubleSpinBox()
    # self.__dsbAETo.setSingleStep(0.1)
    #
    # self.__mainLayout.addRow(self.__lblAEFrom, self.__dsbAEFrom)
    # self.__mainLayout.addRow(self.__lblAETo, self.__dsbAETo)
    #
    # self.__lblFWHM = QLabel("FWHM:")
    # self.__dsbFWHM = QDoubleSpinBox()
    # self.__dsbFWHM.setSingleStep(0.05)
    # self.__dsbFWHM.setRange(0, sys.float_info.max)
    #
    # self.__lblMinSpan = QLabel("Min Span:")
    # self.__dsbMinSpan = QDoubleSpinBox()
    # self.__dsbMinSpan.setSingleStep(0.05)
    # self.__dsbMinSpan.setRange(0, sys.float_info.max)
    #
    # self.__cmdFit = QPushButton("Fit")
    # self.__cmdZoomToFitArea = QPushButton("Zoom To Fit")
    #
    # self.__mainLayout.addRow(self.__lblFWHM, self.__dsbFWHM)
    # self.__mainLayout.addRow(self.__lblMinSpan, self.__dsbMinSpan)
    #
    # self.__lblFitFunc = QLabel("Fit-Funct:")
    # self.__edtFitFunc = QLineEdit("")
    # self.__edtFitFunc.setReadOnly(True)
    #
    # self.__lblFitFunc.setVisible(False)
    # self.__edtFitFunc.setVisible(False)
    #
    # self.__mainLayout.addRow(self.__lblFitFunc, self.__edtFitFunc)
    #
    # self.__lblFoundAE = QLabel(self.AEFOUNDAT.format(0))
    # self.__lblStdDev = QLabel(self.STDDEVAT.format(0))
    #
    # self.__chkDisableFit = QCheckBox("Disable")
    # self.__cmdRemoveFit = QPushButton("Remove")
    #
    # self.__mainLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)

    self.setLayout(self.__mainLayout)

    # self.__mainLayout.addWidget(self.__lblAEFrom)
    # self.__mainLayout.addWidget(self.__dsbAEFrom)
    # self.__mainLayout.addWidget(self.__lblAETo)
    # self.__mainLayout.addWidget(self.__dsbAETo)

    # self.__mainLayout.addWidget(self.__lblFWHM)
    # self.__mainLayout.addWidget(self.__dsbFWHM)

    # self.__mainLayout.addWidget(self.__lblMinSpan)
    # self.__mainLayout.addWidget(self.__dsbMinSpan)

    # self.__mainLayout.addRow(self.__lblFoundAE, self.__lblStdDev)
    # self.__mainLayout.addRow(self.__cmdZoomToFitArea, self.__cmdFit)
    # self.__mainLayout.addRow(self.__chkDisableFit, self.__cmdRemoveFit)

    self.setEnabled(True)

  def isDisabled(self):
    return self.getFitDataInfo().isDisabled()

  # get-set-block
  def isFitted(self):
    pass
    # return (self.__AEFitDataInfo is not None) and self.__AEFitDataInfo.isFitted()

  def getFitDataInfo(self):
    return self.__customFitDataInfo

  def __chkDisableFit_stateChanged(self, state):

    self.getFitDataInfo().setDisabled(state == Qt.Checked)

    self.disable_fit.emit(self.getFitDataInfo(), (state == Qt.Checked))

  def __cmdRemoveFit_clicked(self):
    self.remove_fit.emit(self.getFitDataInfo())

  def _on_set_data(self, data):
    self.__AEFitDataInfo.setData(data)

    if self.__AEFitDataInfo.is_initialized():
      self.setAEFrom(data[0][0])
      self.setAETo(data[-1][0])

      self.__dsbAEFrom.setMinimum(data[0][0])
      self.__dsbAEFrom.setMaximum(data[-1][0])

      self.__dsbAETo.setMinimum(data[0][0])
      self.__dsbAETo.setMaximum(data[-1][0])

  def __cmdFit_clicked(self):
    self.fitToFunction()

  def __cmdZoomToFitArea_clicked(self):
    if self.__AEFitDataInfo.isFitted():
      lb = fh.find_ev_position(self.__AEFitDataInfo.getFitData(), self.__AEFitDataInfo.getFitRelFrom())
      ub = fh.find_ev_position(self.__AEFitDataInfo.getFitData(), self.__AEFitDataInfo.getFitRelTo())

      self.zoom_to_fit.emit(lb, ub, self.__AEFitDataInfo.get_fit_index())

  def getName(self):
    return self.__AEFitDataInfo.getName()

  def get_fit_index(self):
    return self.__AEFitDataInfo.get_fit_index()

  def __spbAEFrom_changed(self):
    self.__AEFitDataInfo.setAEFrom(self.getAEFrom())
    self.AEFrom_changed.emit()

  def __spbAETo_changed(self):
    self.__AEFitDataInfo.setAETo(self.getAETo())
    self.AETo_changed.emit()

  def __dsbFWHM_changed(self):
    self.__AEFitDataInfo.setFWHM(self.getFWHM())
    self.FWHM_changed.emit()

  def __dsbMinSpan_changed(self):
    self.__AEFitDataInfo.setMinspan(self.getMinSpan())
    self.minspan_changed.emit()

  def resetFit(self):
    self.__AEFitDataInfo.reset()

  def shiftData(self, increment):
    self.__AEFitDataInfo.shift_fit(increment)

    self.setAEFrom(self.getAEFrom() + increment)
    self.setAETo(self.getAETo() + increment)

  def fitToFunction(self):
    msg = self.__AEFitDataInfo.fitToFunction()

    self.Post_Fit.emit(self.__AEFitDataInfo, msg)

    if msg == self.__AEFitDataInfo.SUCCESS:
      self.__lblFoundAE.setText(self.AEFOUNDAT.format(self.__AEFitDataInfo.getFoundAE()))
      self.__lblStdDev.setText(self.STDDEVAT.format(self.__AEFitDataInfo.getStdDeviation()))
      self.__dsbFWHM.setValue(self.__AEFitDataInfo.getFittedFWHM())
      self.__edtFitFunc.setText(self.__AEFitDataInfo.getFitFunc())
      self.__cmdZoomToFitArea.setEnabled(True)
    else:
      self.__cmdZoomToFitArea.setEnabled(False)

    return msg, self.__AEFitDataInfo
