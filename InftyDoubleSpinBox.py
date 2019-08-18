from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5 import QtGui, QtCore
import numpy as np

class InftyDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, min=-np.inf, max=np.inf, default=0):
        super(QDoubleSpinBox, self).__init__()

        self.setMinimum(min)
        self.setMaximum(max)
        self.setDefault(default)

    def default(self):
        return self.__default

    def setDefault(self, value: np.float):
        self.__default = value

    def __is_key_del(self, key):
        return key == QtCore.Qt.Key_Delete or key == QtCore.Qt.Key_Backspace

    def __is_set_inf(self):
        return self.value() == np.inf or self.value() == -np.inf

    def keyPressEvent(self, e: QtGui.QKeyEvent):
        if e.key() == QtCore.Qt.Key_Home:
            self.setValue(self.maximum())
        elif e.key() == QtCore.Qt.Key_End:
            self.setValue(self.minimum())
        elif self.__is_key_del(e.key()) and self.__is_set_inf():
            self.setValue(self.default())
        else:
            super(QDoubleSpinBox, self).keyPressEvent(e)

