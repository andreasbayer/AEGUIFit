from PyQt5.QtWidgets import QLabel, QWidget, QGroupBox, QHBoxLayout, QPushButton, QFormLayout
from PyQt5.QtCore import pyqtSignal
import AEFitDataInfo as fd
from InftyDoubleSpinBox import InftyDoubleSpinBox
import helplib as hl
import sys
import numpy as np


class fitButtonGrid(QWidget):
  
  Fit_triggered = pyqtSignal()
  AEFrom_changed = pyqtSignal()
  AETo_changed = pyqtSignal()
  minspan_changed = pyqtSignal()
  FWHM_changed = pyqtSignal()
  
  def __init__(self):
    QWidget.__init__(self)
    
    self.__initLayout()
    self.__connectSignals()
    
    self.__AEFitDataInfo = fd.AEFitDataInfo()
  
  def __connectSignals(self):
    self.__cmdShowAll.pressed.connect(self.__cmdShowAll_pressed)
    self.__cmdShowFitRelevantData.pressed.connect(self.__cmdShowFitRelevantData_pressed)
    self.__cmdShowPM.pressed.connect(self._cmdShowPM_pressed)
    self.__dsbMinSpan.valueChanged.connect(self.__dsbMinSpan_changed)
    self.__cmdFit.clicked.connect(self.__cmdFit_clicked)
  
  def __initLayout(self):
    self.setCheckable(True)
    self.setChecked(False)
    self.setTitle("AE Fit")
    
    self.__mainLayout = QFormLayout()
    
    self.__lblAEFrom = QLabel("Estimated AE from ")
    self.__dsbAEFrom = InftyDoubleSpinBox(min=0)
    self.__dsbAEFrom.setValue(0)
    
    self.__lblAETo = QLabel(" to ")
    self.__dsbAETo = InftyDoubleSpinBox()
    
    self.__mainLayout.addRow(self.__lblAEFrom, self.__dsbAEFrom)
    self.__mainLayout.addRow(self.__lblAETo, self.__dsbAETo)
    
    self.__lblFWHM = QLabel("FWHM:")
    self.__dsbFWHM = InftyDoubleSpinBox(min=0)
    self.__dsbFWHM.setSingleStep(0.05)

    self.__lblMinSpan = QLabel("Min Span:")
    self.__dsbMinSpan = InftyDoubleSpinBox(min=0)
    self.__cmdFit = QPushButton("Fit")
    
    self.__mainLayout.addRow(self.__lblFWHM, self.__dsbFWHM)
    self.__mainLayout.addRow(self.__lblMinSpan, self.__dsbMinSpan)
    
    self.__lblFoundAE = QLabel(self.AEFOUNDAT.format(0))
    self.__lblStdDev = QLabel(self.STDDEVAT.format(0))
    
    self.__mainLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
    
    self.setLayout(self.__mainLayout)
    
  def __cmdFit_clicked(self):
    pass
