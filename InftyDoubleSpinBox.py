from PyQt5.QtWidgets import QDoubleSpinBox
import numpy as np

class InftyDoubleSpinBox(QDoubleSpinBox):

    def __init__(self):
        super(QDoubleSpinBox, self).__init__(self)

        self.setMinimum(-np.inf)
        self.setMaximum(np.inf)

    def setValue(self, val):


        super(QDoubleSpinBox, self).setValue(val)