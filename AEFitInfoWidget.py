from PyQt5.QtWidgets import QLabel, QPushButton, QGridLayout, QLineEdit, QCheckBox, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt
from InftyDoubleSpinBox import InftyDoubleSpinBox
import AEFitDataInfo as aef
import fitHelper as fh
import sys
import fitInfoWidget as fiw
import numpy as np
import dia_goodness_of_minspan as gom

AEFOUNDAT = "Found AE at {:f} eV"
STDDEVAT = "with a stdDev of {:f} eV"

PM = u' \u00B1 '
AEUNIT = "" #"eV"
YLABEL = "Y-Offset"
AELABEL = "AE"
SCALELABEL = "Scale Factor"
ALPHALABEL = "Alpha"


class AEFitInfoWidget(fiw.fitInfoWidget):
    FITINITIALS = "aef"

    AEFrom_changed = pyqtSignal()
    AETo_changed = pyqtSignal()
    AlphaFrom_changed = pyqtSignal()
    AlphaTo_changed = pyqtSignal()
    YFrom_changed = pyqtSignal()
    YTo_changed = pyqtSignal()
    ScaleFrom_changed = pyqtSignal()
    ScaleTo_changed = pyqtSignal()
    minspan_changed = pyqtSignal()
    FWHM_changed = pyqtSignal()
    DomainTo_changed = pyqtSignal()
    DomainFrom_changed = pyqtSignal()
    #zoom_to_fit = pyqtSignal(int, int)
    #progressUpdate = pyqtSignal(np.float64, list)
    
    def __init__(self, index, shift_function, parameters=None):
        fiw.fitInfoWidget.__init__(self)
        
        self.__AEFitDataInfo = aef.AEFitDataInfo(index)
        self.getFitDataInfo().setProgressUpdateFunction(self.emitProgressUpdate)
        shift_function.connect(self.shiftData)

        self.__initLayout()
        self.reset(True)
        self.__connectSignals()
        
        if parameters is not None:
            self.initialize_from_parameters(parameters)
    
    def initialize_from_parameters(self, parameters):
        ps = parameters.split('\v')

        for parameter in ps:
            (short, value) = parameter.split('=')
            if short == 'aef':
                self.setAEFrom(np.float64(value))
            elif short == 'aet':
                self.setAETo(np.float64(value))
            elif short == 'yfr':
                self.setYFrom(np.float64(value))
            elif short == 'yto':
                self.setYTo(np.float64(value))
            elif short == 'alf':
                self.setAlphaFrom(np.float64(value))
            elif short == 'alt':
                self.setAlphaTo(np.float64(value))
            elif short == 'scf':
                self.setScaleTo(np.float64(value))
            elif short == 'sct':
                self.setScaleFrom(np.float64(value))
            elif short == 'dof':
                self.setDomainFrom(np.float64(value))
            elif short == 'dot':
                self.setDomainTo(np.float64(value))
            elif short == 'fwh':
                self.setFWHM(np.float64(value))
            elif short == 'mns':
                self.setMinSpan(np.float64(value))
            elif short == 'wgt':
                if value == '1' or value == 'True':
                    self.setWeighted(True)
                else:
                    self.setWeighted(False)

    def get_fit_string(self):
        return self.FITINITIALS + ':' + \
               'aef=' + str(round(self.getAEFrom(adjusted_for_shift=True), 5)) + '\v' +\
               'aet=' + str(round(self.getAETo(adjusted_for_shift=True), 5)) + '\v' +\
               'yfr=' + str(round(self.getYFrom(), 5)) + '\v' +\
               'yto=' + str(round(self.getYTo(), 5)) + '\v' +\
               'alf=' + str(round(self.getAlphaFrom(), 5)) + '\v' +\
               'alt=' + str(round(self.getAlphaTo(), 5)) + '\v' +\
               'scf=' + str(round(self.getScaleFrom(), 5)) + '\v' +\
               'sct=' + str(round(self.getScaleTo(), 5)) + '\v' + \
               'dof=' + str(round(self.getDomainFrom(adjusted_for_shift=True), 5)) + '\v' + \
               'dot=' + str(round(self.getDomainTo(adjusted_for_shift=True), 5)) + '\v' + \
               'fwh=' + str(round(self.getFWHM(), 5)) + '\v' +\
               'mns=' + str(round(self.getMinSpan(), 5)) + '\v' +\
               'wgt=' + str(self.isWeighted())
    
    def reset(self, enable):
        
        self.setEnabled(enable)
        
        self.getFitDataInfo().reset()

        self.setAEFrom(-np.inf)
        self.setAETo(np.inf)
        self.setYFrom(0.0)
        self.setYTo(0.01)
        self.setScaleFrom(-np.inf)
        self.setScaleTo(np.inf)
        self.setAlphaFrom(-np.inf)
        self.setAlphaTo(np.inf)

        self.setDomainFrom(-np.inf)
        self.setDomainTo(np.inf)

        self.setFWHM(0.3)
        self.setMinSpan(3)
        self.setWeighted(True)

        self.setPostFitFunctionsEnabled(False)

        #todo: reset parameter values and std-devs
    
    def __connectSignals(self):
        self.__dsbAEFrom.editingFinished.connect(self.__AEFrom_changed)
        self.__dsbAETo.editingFinished.connect(self.__AETo_changed)
        self.__dsbAlphaFrom.editingFinished.connect(self.__AlphaFrom_changed)
        self.__dsbAlphaTo.editingFinished.connect(self.__AlphaTo_changed)
        self.__dsbScaleFrom.editingFinished.connect(self.__ScaleFrom_changed)
        self.__dsbScaleTo.editingFinished.connect(self.__ScaleTo_changed)
        self.__dsbYFrom.editingFinished.connect(self.__YFrom_changed)
        self.__dsbYTo.editingFinished.connect(self.__YTo_changed)

        self.__dsbDomainFrom.editingFinished.connect(self.__DomainFrom_changed)
        self.__dsbDomainTo.editingFinished.connect(self.__DomainTo_changed)

        self.__dsbFWHM.editingFinished.connect(self.__FWHM_changed)
        self.__dsbMinSpan.editingFinished.connect(self.__MinSpan_changed)
        self.__cmdFit.clicked.connect(self.__cmdFit_clicked)
        self.__cmdZoomToFitArea.clicked.connect(self.__cmdZoomToFitArea_clicked)
        self.__chkDisableFit.stateChanged.connect(self.__chkDisableFit_stateChanged)
        self.__chkWeightFit.stateChanged.connect(self.__chkWeightFit_stateChanged)
        self.__cmdRemoveFit.clicked.connect(self.__cmdRemoveFit_clicked)
        self.__cmdGoodnessOfMinSpan.clicked.connect(self.__cmdGoodnessOfMinSpan_clicked)

    def emitProgressUpdate(self, relation, p):
        self.progressUpdate.emit(relation, p)
    
    def __initLayout(self):

        self.setCheckable(False)
        self.setChecked(True)
        self.setTitle(self.getFitDataInfo().getName())
        
        self.__mainLayout = QGridLayout()
        self.__mainLayout.setSpacing(5)

        self.__rangeBox = QGroupBox("Fit-Parameter Ranges")
        self.__rangeLayout = QGridLayout()
        self.__rangeBox.setLayout(self.__rangeLayout)

        self.__lblYFrom = QLabel("Y-Offset:")
        self.__dsbYFrom = InftyDoubleSpinBox(min=0)
        self.__dsbYFrom.setSingleStep(0.1)
        self.__dsbYFrom.setFixedWidth(55)
        
        to_lbl_width = 15

        self.__lblYTo = QLabel("to")
        self.__lblYTo.setFixedWidth(to_lbl_width)

        self.__dsbYTo = InftyDoubleSpinBox()
        self.__dsbYTo.setSingleStep(0.1)
        self.__dsbYTo.setFixedWidth(55)

        self.__lblAEFrom = QLabel("AE:")
        self.__dsbAEFrom = InftyDoubleSpinBox(min=0)
        self.__dsbAEFrom.setSingleStep(0.1)
        self.__dsbAEFrom.setFixedWidth(55)

        self.__lblAETo = QLabel("to")
        self.__lblAETo.setFixedWidth(to_lbl_width)

        self.__dsbAETo = InftyDoubleSpinBox()
        self.__dsbAETo.setSingleStep(0.1)
        self.__dsbAETo.setFixedWidth(55)

        self.__lblScaleFrom = QLabel("Scale-Factor:")
        self.__dsbScaleFrom = InftyDoubleSpinBox()
        self.__dsbScaleFrom.setSingleStep(0.1)
        self.__dsbScaleFrom.setFixedWidth(55)

        self.__lblScaleTo = QLabel("to")
        self.__lblScaleTo.setFixedWidth(to_lbl_width)

        self.__dsbScaleTo = InftyDoubleSpinBox()
        self.__dsbScaleTo.setValue(np.inf)
        self.__dsbScaleTo.setSingleStep(0.1)
        self.__dsbScaleTo.setFixedWidth(55)

        self.__lblAlphaFrom = QLabel("Alpha:")
        #self.__lblAlphaFrom.setFixedWidth(to_lbl_width)

        self.__dsbAlphaFrom = InftyDoubleSpinBox(min=-np.inf)
        self.__dsbAlphaFrom.setSingleStep(0.1)
        self.__dsbAlphaFrom.setFixedWidth(55)

        self.__lblAlphaTo = QLabel("to")
        self.__lblAlphaTo.setFixedWidth(to_lbl_width)

        self.__dsbAlphaTo = InftyDoubleSpinBox()
        self.__dsbAlphaTo.setSingleStep(0.1)
        self.__dsbAlphaTo.setFixedWidth(55)

        line = 0
        self.__rangeLayout.addWidget(self.__lblYFrom, line, 0)
        self.__rangeLayout.addWidget(self.__dsbYFrom, line, 1)
        self.__rangeLayout.addWidget(self.__lblYTo, line, 2)
        self.__rangeLayout.addWidget(self.__dsbYTo, line, 3)

        line = 1

        self.__rangeLayout.addWidget(self.__lblAEFrom, line, 0)
        self.__rangeLayout.addWidget(self.__dsbAEFrom, line, 1)
        self.__rangeLayout.addWidget(self.__lblAETo, line, 2)
        self.__rangeLayout.addWidget(self.__dsbAETo, line, 3)

        line = 2

        self.__rangeLayout.addWidget(self.__lblScaleFrom, line, 0)
        self.__rangeLayout.addWidget(self.__dsbScaleFrom, line, 1)
        self.__rangeLayout.addWidget(self.__lblScaleTo, line, 2)
        self.__rangeLayout.addWidget(self.__dsbScaleTo, line, 3)

        line = 3

        self.__rangeLayout.addWidget(self.__lblAlphaFrom, line, 0)
        self.__rangeLayout.addWidget(self.__dsbAlphaFrom, line, 1)
        self.__rangeLayout.addWidget(self.__lblAlphaTo, line, 2)
        self.__rangeLayout.addWidget(self.__dsbAlphaTo, line, 3)

        self.__mainLayout.addWidget(self.__rangeBox, 0, 0, 1, 4)

        self.__lblMinSpan = QLabel("Fit Span:")
        self.__dsbMinSpan = InftyDoubleSpinBox(min=0)
        self.__dsbMinSpan.setSingleStep(0.05)
        self.__dsbMinSpan.setFixedWidth(55)

        self.__lblFWHM = QLabel("FWHM:")
        self.__dsbFWHM = InftyDoubleSpinBox(min=0)
        self.__dsbFWHM.setSingleStep(0.05)
        self.__dsbFWHM.setFixedWidth(55)

        self.__lblDomainFrom = QLabel("Domain from:")
        self.__dsbDomainFrom = InftyDoubleSpinBox(min=0)
        self.__dsbDomainFrom.setSingleStep(0.05)
        self.__dsbDomainFrom.setFixedWidth(55)

        self.__lblDomainTo = QLabel(" to ")
        self.__dsbDomainTo = InftyDoubleSpinBox(min=0)
        self.__dsbDomainTo.setSingleStep(0.05)
        self.__dsbDomainTo.setFixedWidth(55)
        
        self.__cmdFit = QPushButton("Fit")
        self.__cmdFit.setFixedWidth(75)
        self.__chkWeightFit = QCheckBox("Weighted")

        self.__cmdZoomToFitArea = QPushButton("Zoom To Fit")
        self.__cmdZoomToFitArea.setFixedWidth(75)

        self.__cmdGoodnessOfMinSpan = QPushButton("Test Fit Span")
        self.__cmdGoodnessOfMinSpan.setFixedWidth(75)
        self.__dsbGoodnessOfMinSpan_steps = InftyDoubleSpinBox(min=0)
        self.__dsbGoodnessOfMinSpan_steps.setValue(0)
        self.__dsbGoodnessOfMinSpan_steps.setSingleStep(0.1)
        self.__dsbGoodnessOfMinSpan_steps.setFixedWidth(60)
        self.__dsbGoodnessOfMinSpan_steps.setVisible(False)

        self.__mainLayout.addWidget(self.__lblMinSpan, 1, 0)
        self.__mainLayout.addWidget(self.__dsbMinSpan, 1, 1)
        self.__mainLayout.addWidget(self.__lblFWHM, 1, 2)
        self.__mainLayout.addWidget(self.__dsbFWHM, 1, 3)

        self.__mainLayout.addWidget(self.__lblDomainFrom, 2, 0)
        self.__mainLayout.addWidget(self.__dsbDomainFrom, 2, 1)
        self.__mainLayout.addWidget(self.__lblDomainTo, 2, 2)
        self.__mainLayout.addWidget(self.__dsbDomainTo, 2, 3)

        self.__lblFitFunc = QLabel("Fit-Funct:")
        self.__edtFitFunc = QLineEdit("")
        self.__edtFitFunc.setReadOnly(True)

        self.__lblFitFunc.setVisible(False)
        self.__edtFitFunc.setVisible(False)
        
        #self.__mainLayout.addRow(self.__lblFitFunc, self.__edtFitFunc)
        
        #self.__lblFoundAE = QLabel(AEFOUNDAT.format(0))
        #self.__lblStdDev = QLabel(STDDEVAT.format(0))

        #self.__lblYOffset = QLabel(YLABEL)
        #self.__mainLayout.addWidget(self.__lblYOffset, 2, 0, 1, 4)

        #self.__lblAE = QLabel(AELABEL)
        #self.__mainLayout.addWidget(self.__lblAE, 3, 0, 1, 4)

        #self.__lblScale = QLabel(SCALELABEL)
        #self.__mainLayout.addWidget(self.__lblScale, 4, 0, 1, 4)

        #self.__lblAlpha = QLabel(ALPHALABEL)
        #self.__mainLayout.addWidget(self.__lblAlpha, 5, 0, 1, 4)

        self.__chkDisableFit = QCheckBox("Disable")
        self.__cmdRemoveFit = QPushButton("Remove")
        self.__cmdRemoveFit.setFixedWidth(75)

        self.__lblFitParameters = QLabel("")
        self.__mainLayout.addWidget(self.__lblFitParameters, 3, 0, 1, 4)

        self.__mainLayout.addWidget(self.__chkDisableFit, 4, 0, 1, 2)
        self.__mainLayout.addWidget(self.__cmdRemoveFit, 4, 2, 1, 2)

        self.__mainLayout.addWidget(self.__chkWeightFit, 5, 0, 1, 2)
        self.__mainLayout.addWidget(self.__cmdFit, 5, 2, 1, 2)
        self.__mainLayout.addWidget(self.__cmdZoomToFitArea, 6, 0, 1, 2)
        self.__mainLayout.addWidget(self.__cmdGoodnessOfMinSpan, 6, 2, 1, 2)

        #self.__mainLayout.addRow(, )
        #self.__mainLayout.addRow(, )
        #self.__mainLayout.addRow(self.__dsbGoodnessOfMinSpan_steps, self.__cmdGoodnessOfMinSpan)
        #self.__mainLayout.addRow(self.__chkDisableFit, self.__cmdRemoveFit)

        self.setLayout(self.__mainLayout)
        self.setFixedHeight(350)

        self.setEnabled(True)

    def isDisabled(self):
        return self.getFitDataInfo().isDisabled()

    # get-set-block
    def isFitted(self):
        return (self.getFitDataInfo() is not None) and self.getFitDataInfo().isFitted()
    
    def getAEFrom(self, adjusted_for_shift=False):
        return self.getFitDataInfo().getAEFrom(adjusted_for_shift)

    def setAEFrom(self, value):
        self.__dsbAEFrom.setValue(np.float64(value))
        self.__AEFrom_changed()

    def __AEFrom_changed(self):
        self.getFitDataInfo().setAEFrom(self.__dsbAEFrom.value())
        self.AEFrom_changed.emit()

    def getAETo(self, adjusted_for_shift=False):
        return self.getFitDataInfo().getAETo(adjusted_for_shift)

    def setAETo(self, value):
        self.__dsbAETo.setValue(np.float64(value))
        self.__AETo_changed()

    def __AETo_changed(self):
        self.getFitDataInfo().setAETo(self.__dsbAETo.value())
        self.AETo_changed.emit()

    def getAlphaFrom(self,):
        return self.getFitDataInfo().getAlphaFrom()

    def setAlphaFrom(self, value):
        self.__dsbAlphaFrom.setValue(np.float64(value))
        self.__AlphaFrom_changed()

    def __AlphaFrom_changed(self):
        self.getFitDataInfo().setAlphaFrom(self.__dsbAlphaFrom.value())
        self.AlphaFrom_changed.emit()

    def getAlphaTo(self):
        return self.getFitDataInfo().getAlphaTo()

    def setAlphaTo(self, value):
        self.__dsbAlphaTo.setValue(np.float64(value))
        self.__AlphaTo_changed()

    def __AlphaTo_changed(self):
        self.getFitDataInfo().setAlphaTo(self.__dsbAlphaTo.value())
        self.AlphaTo_changed.emit()

    def getScaleFrom(self):
        return self.getFitDataInfo().getScaleFrom()

    def setScaleFrom(self, value):
        self.getFitDataInfo().setScaleFrom(np.float64(value))
        self.__ScaleFrom_changed()

    def __ScaleFrom_changed(self):
        self.getFitDataInfo().setScaleFrom(self.__dsbScaleFrom.value())
        self.ScaleFrom_changed.emit()

    def getScaleTo(self):
        return self.getFitDataInfo().getScaleTo()

    def setScaleTo(self, value):
        self.getFitDataInfo().setScaleTo(np.float64(value))
        self.__ScaleTo_changed()

    def __ScaleTo_changed(self):
        self.getFitDataInfo().setScaleTo(self.__dsbScaleTo.value())
        self.ScaleTo_changed.emit()

    def getYFrom(self):
        return self.getFitDataInfo().getYFrom()

    def setYFrom(self, value):
        self.getFitDataInfo().setYFrom(np.float64(value))
        self.__YFrom_changed()

    def __YFrom_changed(self):
        self.getFitDataInfo().setYFrom(self.__dsbYFrom.value())
        self.YFrom_changed.emit()

    def getYTo(self):
        return self.getFitDataInfo().getYTo()

    def setYTo(self, value):
        self.__dsbYTo.setValue(np.float64(value))
        self.__YTo_changed()

    def __YTo_changed(self):
        self.getFitDataInfo().setYTo(self.__dsbYTo.value())
        self.YTo_changed.emit()

    def getFWHM(self):
        return self.__dsbFWHM.value()
    
    def setFWHM(self, value):
        self.__dsbFWHM.setValue(np.float64(value))
        self.getFitDataInfo().setFWHM(value)
        self.__FWHM_changed()

    def getMinSpan(self):
        return self.__dsbMinSpan.value()
    
    def setMinSpan(self, value):
        self.__dsbMinSpan.setValue(np.float64(value))
        self.__MinSpan_changed()

    def getDomainFrom(self, adjusted_for_shift=False):
        return self.getFitDataInfo().getDomainFrom(adjusted_for_shift)

    def setDomainFrom(self, value):
        self.__dsbDomainFrom.setValue(np.float64(value))
        self.__DomainFrom_changed()

    def __DomainFrom_changed(self):
        self.getFitDataInfo().setDomainFrom(self.__dsbDomainFrom.value())
        self.DomainFrom_changed.emit()

    def getDomainTo(self, adjusted_for_shift=False):
        return self.getFitDataInfo().getDomainTo(adjusted_for_shift)

    def setDomainTo(self, value):
        self.__dsbDomainTo.setValue(np.float64(value))
        self.__DomainTo_changed()

    def __DomainTo_changed(self):
        self.getFitDataInfo().setDomainTo(self.__dsbDomainTo.value())
        self.DomainTo_changed.emit()

    def setWeighted(self, value):
        self.__chkWeightFit.setChecked(value)

    def isWeighted(self):
        return self.__chkWeightFit.isChecked()
    
    def getFitDataInfo(self):
        return self.__AEFitDataInfo

    def __chkDisableFit_stateChanged(self, state):
        self.getFitDataInfo().setDisabled(state == Qt.Checked)
        self.disable_fit.emit(self.getFitDataInfo(), (state == Qt.Checked))

    def __chkWeightFit_stateChanged(self, state):
        self.getFitDataInfo().set_weighted(state == Qt.Checked)
    
    def __cmdRemoveFit_clicked(self):
        self.remove_fit.emit(self.getFitDataInfo())
    
    def _on_set_data(self, data, std_err):
        if self.getFitDataInfo().is_initialized() is False:
            self.getFitDataInfo().setStdErr(std_err)

            self.setAEFrom(data[0][0])
            self.setAETo(data[-1][0])

            self.setDomainFrom(data[0][0])
            self.setDomainTo(data[-1][0])

            self.__dsbAEFrom.setMinimum(data[0][0])
            self.__dsbAEFrom.setMaximum(data[-1][0])

            self.__dsbAETo.setMinimum(data[0][0])
            self.__dsbAETo.setMaximum(data[-1][0])

            self.__dsbDomainFrom.setMinimum(data[0][0])
            self.__dsbDomainFrom.setMaximum(data[-1][0])

            self.__dsbDomainTo.setMinimum(data[0][0])
            self.__dsbDomainTo.setMaximum(data[-1][0])

    def __cmdFit_clicked(self):
        self.fitToFunction()

    def __cmdGoodnessOfMinSpan_clicked(self):
        self.testGoodnessOfMinSpan()
    
    def __cmdZoomToFitArea_clicked(self):
        if self.getFitDataInfo().isFitted():
            lb = self.getFitDataInfo().getFitRelFrom()
            ub = self.getFitDataInfo().getFitRelTo()
            
            self.zoom_to_fit.emit(lb, ub, self.getFitDataInfo().get_fit_index())

    def getName(self):
        return self.getFitDataInfo().getName()
            
    def __FWHM_changed(self):
        self.getFitDataInfo().setFWHM(self.getFWHM())
        self.FWHM_changed.emit()
    
    def __MinSpan_changed(self):
        self.getFitDataInfo().setMinspan(self.getMinSpan())
        self.minspan_changed.emit()
    
    def resetFit(self):
        self.getFitDataInfo().reset()
    
    def shiftData(self, increment):
        self.getFitDataInfo().shift_fit(increment)
        
        new_AEFrom = self.getAEFrom() + increment
        new_AETo = self.getAETo() + increment

        self.__dsbAEFrom.setMinimum(self.__dsbAEFrom.minimum() + increment)
        self.__dsbAEFrom.setMaximum(self.__dsbAEFrom.maximum() + increment)

        self.__dsbAETo.setMinimum(self.__dsbAETo.minimum() + increment)
        self.__dsbAETo.setMaximum(self.__dsbAETo.maximum() + increment)
        
        self.setAEFrom(new_AEFrom)
        self.setAETo(new_AETo)

        new_DomainFrom = self.getDomainFrom() + increment
        new_DomainTo = self.getDomainTo() + increment

        self.__dsbDomainFrom.setMinimum(self.__dsbDomainFrom.minimum() + increment)
        self.__dsbDomainFrom.setMaximum(self.__dsbDomainFrom.maximum() + increment)

        self.__dsbDomainTo.setMinimum(self.__dsbDomainTo.minimum() + increment)
        self.__dsbDomainTo.setMaximum(self.__dsbDomainTo.maximum() + increment)

        self.setDomainFrom(new_DomainFrom)
        self.setDomainTo(new_DomainTo)
    
    def fitToFunction(self):
        msg = self.getFitDataInfo().fitToFunction()
        
        self.Post_Fit.emit(self.getFitDataInfo(), msg)
        
        if msg == self.getFitDataInfo().SUCCESS:
            #self.__lblFoundAE.setText(AEFOUNDAT.format(self.getFitDataInfo().getFoundAE()))
            #self.__lblStdDev.setText(STDDEVAT.format(self.getFitDataInfo().getStdDeviation()))

            #how many digits to show of the error (Digits Of Error)
            doe = 2

            val, err = fh.roundToErrorStrings(self.getFitDataInfo().getYOffset(),
                                              self.getFitDataInfo().getYOffset_dev(), doe)

            fp_text = YLABEL + ':\t\t' + val + PM + err + '\n'

            val, err = fh.roundToErrorStrings(self.getFitDataInfo().getFoundAE(),
                                              self.getFitDataInfo().getFoundAE_dev(), doe)

            fp_text += AELABEL + ':\t\t' + val + PM + err + AEUNIT + '\n'

            val, err = fh.roundToErrorStrings(self.getFitDataInfo().getScaleFactor(),
                                              self.getFitDataInfo().getScaleFactor_dev(), doe)

            fp_text += SCALELABEL + ':\t' + val + PM + err + '\n'

            val, err = fh.roundToErrorStrings(self.getFitDataInfo().getAlpha(),
                                              self.getFitDataInfo().getAlpha_dev(), doe)

            fp_text += ALPHALABEL + ':\t\t' + val + PM + err + '\n'

            self.__lblFitParameters.setText(fp_text)

            #todo: set fitparameter values and errors

            self.__dsbFWHM.setValue(self.getFitDataInfo().getFittedFWHM())
            self.__edtFitFunc.setText(self.getFitDataInfo().getFitFunc())
            self.setPostFitFunctionsEnabled(True)
        else:
            self.setPostFitFunctionsEnabled(False)
        
        return msg, self.getFitDataInfo()
    
    def setPostFitFunctionsEnabled(self, enabled):
        self.__cmdZoomToFitArea.setEnabled(enabled)
        self.__cmdGoodnessOfMinSpan.setEnabled(enabled)

    def testGoodnessOfMinSpan(self):
        minspans, y_offsets, aes, scale_factors, alphas,\
        y_offset_errrs, ae_errs, scale_factor_errs, alpha_errs = self.getFitDataInfo().testGoodnessOfMinSpan()

        #print("minspans:")
        #print(minspans)

        #print("aes:")
        #print(aes)
        #print("avg:")
        #print(np.average(aes))
        #print("std deviation:")
        #print(np.std(aes))

        #print("alphas:")
        #print(alphas)
        #print("avg:")
        #print(np.average(alphas))
        #print("std deviation:")
        #print(np.std(alphas))

        dia_gom = gom.dia_goodness_of_minspan()
        
        dia_gom.setYOffset(y_offsets, y_offset_errrs)
        dia_gom.setAEs(aes, ae_errs)
        dia_gom.setScaleFactors(scale_factors, scale_factor_errs)
        dia_gom.setAlphas(alphas, alpha_errs)
        
        dia_gom.setMinSpans(minspans)
        
        dia_gom.plot()
        #dia_gom.display_statistics()
        dia_gom.show()
        dia_gom.setFocus()
        
        #try:
        #    plt.figure()
        #    plt.plot(minspans, aes)
        #    plt.plot(minspans, alphas)
        #    #plt.ylabel('')
        #    plt.show()
        #except Exception as e:
        #    print(e)
        
        
    
