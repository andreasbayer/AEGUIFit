from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5 import QtGui, QtCore
import numpy as np

class InftyDoubleSpinBox(QDoubleSpinBox):

    def __init__(self, min=-np.inf, max=np.inf, default=0):
        super(QDoubleSpinBox, self).__init__()

        self.setMinimum(min)
        self.setMaximum(max)
        self.setDefault(default)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)


    # This is here to prevent value changes while scrolling through the configuration, as it removes the ability to
    # alter values with the scroll wheel. If the code below the return was to be put in place of the mere return,
    # it would be possible to still use the scroll wheel, however only, if the InftyDoubleSpinBox already has focus.
    # This seems too complex to distinguish and unnecessary as a feature, which is the reasson it is removed altogether.

    def wheelEvent(self, e: QtGui.QWheelEvent):
        return

        #if self.hasFocus():
        #    return QDoubleSpinBox.wheelEvent(self, e)


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
            self.setValue(self.minimum())
        elif e.key() == QtCore.Qt.Key_End:
            self.setValue(self.maximum())
        elif self.__is_key_del(e.key()) and self.__is_set_inf():
            self.setValue(self.default())
        else:
            super(QDoubleSpinBox, self).keyPressEvent(e)

