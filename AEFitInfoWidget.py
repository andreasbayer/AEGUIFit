from PyQt5.QtWidgets import QLabel, QPushButton, QDoubleSpinBox, QGridLayout, QLineEdit, QCheckBox, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt
import InftyDoubleSpinBox
import AEFitDataInfo as aef
import fitHelper as fh
import sys
import fitInfoWidget as fiw
import numpy as np
import matplotlib.pyplot as plt
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
    AlphaBounds_changed = pyqtSignal()
    YBounds_changed = pyqtSignal()
    ScaleBounds_changed = pyqtSignal()
    minspan_changed = pyqtSignal()
    FWHM_changed = pyqtSignal()
    #zoom_to_fit = pyqtSignal(int, int)
    #progressUpdate = pyqtSignal(float, list)
    
    def __init__(self, index, shift_function, parameters=None):
        fiw.fitInfoWidget.__init__(self)
        
        self.__AEFitDataInfo = aef.AEFitDataInfo(index)
        self.__AEFitDataInfo.setProgressUpdateFunction(self.emitProgressUpdate)
        shift_function.connect(self.shiftData)

        self.__initLayout()
        self.reset(True)
        self.__connectSignals()
        
        if parameters is not None:
            self.init_from_parameters(parameters)
    
    def initialize_from_parameters(self, parameters):
        ps = parameters.split(",")

        for parameter in ps:
            (short, value) = parameter.split('=')
            if short == 'aef':
                self.setAEFrom(float(value))
            elif short == 'aet':
                self.setAETo(float(value))
            elif short == 'fwh':
                self.setFWHM(float(value))
            elif short == 'mns':
                self.setMinSpan(float(value))
            elif short == 'wgt':
                if value == '1' or value == 'True':
                    self.setWeighted(True)
                else:
                    self.setWeighted(False)

    def get_fit_string(self):
        return self.FITINITIALS + ':' + \
               'aef=' + str(round(self.getAEFrom(), 5)) + ',' +\
               'aet=' + str(round(self.getAETo(), 5)) + ',' +\
               'fwh=' + str(round(self.getFWHM(), 5)) + ',' +\
               'mns=' + str(round(self.getMinSpan(), 5)) + ',' +\
               'wgt=' + str(self.isWeighted())
    
    def reset(self, enable):
        
        self.setEnabled(enable)
        
        self.__AEFitDataInfo.reset()
        
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
        self.setTitle(self.__AEFitDataInfo.getName())
        
        self.__mainLayout = QGridLayout()
        self.__mainLayout.setSpacing(5)

        self.__rangeBox = QGroupBox("Fit-Parameter Ranges")
        self.__rangeLayout = QGridLayout()
        self.__rangeBox.setLayout(self.__rangeLayout)

        self.__lblYFrom = QLabel("Y-Offset:")
        self.__dsbYFrom = QDoubleSpinBox()
        self.__dsbYFrom.setRange(0, sys.float_info.max)
        self.__dsbYFrom.setValue(0)
        self.__dsbYFrom.setSingleStep(0.1)
        self.__dsbYFrom.setFixedWidth(55)
        
        self.__lblYTo = QLabel("to")
        self.__dsbYTo = QDoubleSpinBox()
        self.__dsbYTo.setSingleStep(0.1)
        self.__dsbYTo.setFixedWidth(55)

        self.__lblAEFrom = QLabel("AE:")
        self.__dsbAEFrom = QDoubleSpinBox()
        self.__dsbAEFrom.setRange(0, sys.float_info.max)
        self.__dsbAEFrom.setValue(0)
        self.__dsbAEFrom.setSingleStep(0.1)
        self.__dsbAEFrom.setFixedWidth(55)

        self.__lblAETo = QLabel("to")
        self.__dsbAETo = QDoubleSpinBox()
        self.__dsbAETo.setSingleStep(0.1)
        self.__dsbAETo.setFixedWidth(55)

        self.__lblScaleFrom = QLabel("Scale-Factor:")
        self.__dsbScaleFrom = QDoubleSpinBox()
        self.__dsbScaleFrom.setRange(0, sys.float_info.max)
        self.__dsbScaleFrom.setValue(0)
        self.__dsbScaleFrom.setSingleStep(0.1)
        self.__dsbScaleFrom.setFixedWidth(55)

        self.__lblScaleTo = QLabel("to")
        self.__dsbScaleTo = QDoubleSpinBox()
        self.__dsbScaleTo.setSingleStep(0.1)
        self.__dsbScaleTo.setFixedWidth(55)

        self.__lblAlphaFrom = QLabel("Alpha:")
        self.__dsbAlphaFrom = QDoubleSpinBox()
        self.__dsbAlphaFrom.setRange(0, sys.float_info.max)
        self.__dsbAlphaFrom.setValue(0)
        self.__dsbAlphaFrom.setSingleStep(0.1)
        self.__dsbAlphaFrom.setFixedWidth(55)

        self.__lblAlphaTo = QLabel("to")
        self.__dsbAlphaTo = QDoubleSpinBox()
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

        self.__lblFWHM = QLabel("FWHM:")
        self.__dsbFWHM = QDoubleSpinBox()
        self.__dsbFWHM.setSingleStep(0.05)
        self.__dsbFWHM.setRange(0, sys.float_info.max)
        self.__dsbFWHM.setFixedWidth(55)
        
        self.__lblMinSpan = QLabel("Fit Span:")
        self.__dsbMinSpan = QDoubleSpinBox()
        self.__dsbMinSpan.setSingleStep(0.05)
        self.__dsbMinSpan.setRange(0, sys.float_info.max)
        self.__dsbMinSpan.setFixedWidth(55)
        
        self.__cmdFit = QPushButton("Fit")
        self.__cmdFit.setFixedWidth(75)
        self.__chkWeightFit = QCheckBox("Weighted")


        self.__cmdZoomToFitArea = QPushButton("Zoom To Fit")
        self.__cmdZoomToFitArea.setFixedWidth(75)

        self.__cmdGoodnessOfMinSpan = QPushButton("Test Fit Span")
        self.__cmdGoodnessOfMinSpan.setFixedWidth(75)
        self.__dsbGoodnessOfMinSpan_steps = QDoubleSpinBox()
        self.__dsbGoodnessOfMinSpan_steps.setRange(0, sys.float_info.max)
        self.__dsbGoodnessOfMinSpan_steps.setValue(0)
        self.__dsbGoodnessOfMinSpan_steps.setSingleStep(0.1)
        self.__dsbGoodnessOfMinSpan_steps.setFixedWidth(60)
        self.__dsbGoodnessOfMinSpan_steps.setVisible(False)

        self.__mainLayout.addWidget(self.__lblMinSpan, 1, 0)
        self.__mainLayout.addWidget(self.__dsbMinSpan, 1, 1)
        self.__mainLayout.addWidget(self.__lblFWHM, 1, 2)
        self.__mainLayout.addWidget(self.__dsbFWHM, 1, 3)

        self.__lblFitFunc = QLabel("Fit-Funct:")
        self.__edtFitFunc = QLineEdit("")
        self.__edtFitFunc.setReadOnly(True)

        self.__lblFitFunc.setVisible(False)
        self.__edtFitFunc.setVisible(False)
        
        #self.__mainLayout.addRow(self.__lblFitFunc, self.__edtFitFunc)
        
        #self.__lblFoundAE = QLabel(AEFOUNDAT.format(0))
        #self.__lblStdDev = QLabel(STDDEVAT.format(0))

        self.__lblFitParameters = QLabel("")
        self.__mainLayout.addWidget(self.__lblFitParameters, 2, 0, 1, 4)

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

        self.__mainLayout.addWidget(self.__chkDisableFit, 3, 0, 1, 2)
        self.__mainLayout.addWidget(self.__cmdRemoveFit, 3, 2, 1, 2)
        self.__mainLayout.addWidget(self.__chkWeightFit, 4, 0, 1, 2)
        self.__mainLayout.addWidget(self.__cmdFit, 4, 2, 1, 2)
        self.__mainLayout.addWidget(self.__cmdZoomToFitArea, 5, 0, 1, 2)
        self.__mainLayout.addWidget(self.__cmdGoodnessOfMinSpan, 5, 2, 1, 2)

        #self.__mainLayout.addRow(, )
        #self.__mainLayout.addRow(, )
        #self.__mainLayout.addRow(self.__dsbGoodnessOfMinSpan_steps, self.__cmdGoodnessOfMinSpan)
        #self.__mainLayout.addRow(self.__chkDisableFit, self.__cmdRemoveFit)

        self.setLayout(self.__mainLayout)
        self.setFixedHeight(325)

        self.setEnabled(True)

    def isDisabled(self):
        return self.getFitDataInfo().isDisabled()

    # get-set-block
    def isFitted(self):
        return (self.__AEFitDataInfo is not None) and self.__AEFitDataInfo.isFitted()
    
    def getAEFrom(self):
        return self.__AEFitDataInfo.getAEFrom()
    
    def setAEFrom(self, value):
        self.__dsbAEFrom.setValue(float(value))
        self.__AEFrom_changed()
    
    def getAETo(self):
        return self.__AEFitDataInfo.getAETo()
    
    def setAETo(self, value):
        self.__dsbAETo.setValue(float(value))
        self.__AETo_changed()

    def getAlphaBounds(self):
        return self.__AEFitDataInfo.getAlphaBounds()

    def setAlphaBounds(self, value):
        #self.__dsbAlphaFrom.setValue(float(value[0]))
        #self.__dsbAlphaTo.setValue(float(value[1]))

        self.__AlphaBounds_changed(value)

    def __AlphaFrom_changed(self, value):
        #self.__AEFitDataInfo.setAlphaBounds(value)
        #self.AlphaBounds_changed.emit()
        pass

    def __AlphaTo_changed(self, value):
        #self.__AEFitDataInfo.setAlphaBounds(value)
        #self.AlphaBounds_changed.emit()
        pass

    def getAETo(self):
        return self.__AEFitDataInfo.getAETo()

    def setAETo(self, value):
        self.__dsbAETo.setValue(float(value))
        self.__AETo_changed()

        self.__dsbAlphaTo.setValue(np.inf)

    def getFWHM(self):
        return self.__dsbFWHM.value()
    
    def setFWHM(self, value):
        self.__dsbFWHM.setValue(float(value))
        self.__AEFitDataInfo.setFWHM(value)
        self.__FWHM_changed()

    def getMinSpan(self):
        return self.__dsbMinSpan.value()
    
    def setMinSpan(self, value):
        self.__dsbMinSpan.setValue(float(value))
        self.__MinSpan_changed()

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
        self.__AEFitDataInfo.set_weighted(state == Qt.Checked)
    
    def __cmdRemoveFit_clicked(self):
        self.remove_fit.emit(self.getFitDataInfo())
    
    def _on_set_data(self, data, std_err):
        if self.__AEFitDataInfo.is_initialized() is False:
            self.__AEFitDataInfo.setStdErr(std_err)

            self.setAEFrom(data[0][0])
            self.setAETo(data[-1][0])

            self.__dsbAEFrom.setMinimum(data[0][0])
            self.__dsbAEFrom.setMaximum(data[-1][0])

            self.__dsbAETo.setMinimum(data[0][0])
            self.__dsbAETo.setMaximum(data[-1][0])

    def __cmdFit_clicked(self):
        self.fitToFunction()

    def __cmdGoodnessOfMinSpan_clicked(self):
        self.testGoodnessOfMinSpan()
    
    def __cmdZoomToFitArea_clicked(self):
        if self.__AEFitDataInfo.isFitted():
            lb = self.__AEFitDataInfo.getFitRelFrom()
            ub = self.__AEFitDataInfo.getFitRelTo()
            
            self.zoom_to_fit.emit(lb, ub, self.__AEFitDataInfo.get_fit_index())

    def getName(self):
        return self.__AEFitDataInfo.getName()
            
    def __AEFrom_changed(self):
        self.__AEFitDataInfo.setAEFrom(self.__dsbAEFrom.value())
        self.AEFrom_changed.emit()
    
    def __AETo_changed(self):
        self.__AEFitDataInfo.setAETo(self.__dsbAETo.value())
        self.AETo_changed.emit()
    
    def __FWHM_changed(self):
        self.__AEFitDataInfo.setFWHM(self.getFWHM())
        self.FWHM_changed.emit()
    
    def __MinSpan_changed(self):
        self.__AEFitDataInfo.setMinspan(self.getMinSpan())
        self.minspan_changed.emit()
    
    def resetFit(self):
        self.__AEFitDataInfo.reset()
    
    def shiftData(self, increment):
        self.__AEFitDataInfo.shift_fit(increment)
        
        new_AEFrom = self.getAEFrom() + increment
        new_AETo = self.getAETo() + increment

        self.__dsbAEFrom.setMinimum(self.__dsbAEFrom.minimum() + increment)
        self.__dsbAEFrom.setMaximum(self.__dsbAEFrom.maximum() + increment)

        self.__dsbAETo.setMinimum(self.__dsbAETo.minimum() + increment)
        self.__dsbAETo.setMaximum(self.__dsbAETo.maximum() + increment)
        
        self.setAEFrom(new_AEFrom)
        self.setAETo(new_AETo)
    
    def fitToFunction(self):
        msg = self.__AEFitDataInfo.fitToFunction()
        
        self.Post_Fit.emit(self.__AEFitDataInfo, msg)
        
        if msg == self.__AEFitDataInfo.SUCCESS:
            #self.__lblFoundAE.setText(AEFOUNDAT.format(self.__AEFitDataInfo.getFoundAE()))
            #self.__lblStdDev.setText(STDDEVAT.format(self.__AEFitDataInfo.getStdDeviation()))

            #how many digits to show of the error (Digits Of Error)
            doe = 2

            val, err = fh.roundToErrorStrings(self.__AEFitDataInfo.getFoundAE(), self.__AEFitDataInfo.getFoundAE_dev(),
                                              doe)

            fp_text = AELABEL + ':\t\t' + val + PM + err + AEUNIT + '\n'

            val, err = fh.roundToErrorStrings(self.__AEFitDataInfo.getAlpha(), self.__AEFitDataInfo.getAlpha_dev(), doe)

            fp_text += ALPHALABEL + ':\t\t' + val + PM + err + '\n'

            val, err = fh.roundToErrorStrings(self.__AEFitDataInfo.getScaleFactor(),
                                              self.__AEFitDataInfo.getScaleFactor_dev(), doe)

            fp_text += SCALELABEL + ':\t' + val + PM + err + '\n'

            val, err = fh.roundToErrorStrings(self.__AEFitDataInfo.getYOffset(), self.__AEFitDataInfo.getYOffset_dev(),
                                              doe)

            fp_text += YLABEL + ':\t\t' + val + PM + err

            self.__lblFitParameters.setText(fp_text)

            #todo: set fitparameter values and errors

            self.__dsbFWHM.setValue(self.__AEFitDataInfo.getFittedFWHM())
            self.__edtFitFunc.setText(self.__AEFitDataInfo.getFitFunc())
            self.setPostFitFunctionsEnabled(True)
        else:
            self.setPostFitFunctionsEnabled(False)
        
        return msg, self.__AEFitDataInfo
    
    def setPostFitFunctionsEnabled(self, enabled):
        self.__cmdZoomToFitArea.setEnabled(enabled)
        self.__cmdGoodnessOfMinSpan.setEnabled(enabled)

    def testGoodnessOfMinSpan(self):
        minspans, y_offsets, aes, scale_factors, alphas,\
        y_offset_errrs, ae_errs, scale_factor_errs, alpha_errs,  = self.__AEFitDataInfo.testGoodnessOfMinSpan()

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
        
        #try:
        #    plt.figure()
        #    plt.plot(minspans, aes)
        #    plt.plot(minspans, alphas)
        #    #plt.ylabel('')
        #    plt.show()
        #except Exception as e:
        #    print(e)
        
        
    
