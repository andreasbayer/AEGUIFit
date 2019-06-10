from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QGroupBox, QSpacerItem,\
    QDoubleSpinBox
from PyQt5.QtCore import pyqtSignal
from sys import float_info as fli
import helplib as hl
import fitDataInfo as fdi
import numpy as np


class ZoomButtonWidget(QGroupBox):
    show_all = pyqtSignal()
    zoom_by_increment = pyqtSignal(str, int)
    font_change = pyqtSignal(int)
    fig_size_changed = pyqtSignal(tuple)
    
    def __init__(self):
        QWidget.__init__(self)
        
        hbox = QHBoxLayout()
        
        self.__cmdLDZoom = QPushButton("<-L")
        self.__cmdLUZoom = QPushButton("L->")
        self.__cmdUDZoom = QPushButton("<-U")
        self.__cmdUUZoom = QPushButton("U->")
        self.__cmdShowAll = QPushButton("Show All")

        self.__cmdFontPlus = QPushButton("Font+")
        self.__cmdFontMinus = QPushButton("Font-")

        self.__lblFigHeight = QLabel("Height: ")
        self.__lblFigWidth = QLabel("Width: ")

        self.__dsbFigHeight = QDoubleSpinBox()
        self.__dsbFigWidth = QDoubleSpinBox()

        self.__dsbFigHeight.setRange(2, fli.max)
        self.__dsbFigHeight.setValue(6)
        self.__dsbFigHeight.setSingleStep(0.1)

        self.__dsbFigWidth.setRange(2, fli.max)
        self.__dsbFigWidth.setValue(12)
        self.__dsbFigWidth.setSingleStep(0.1)

        repeat_delay = 0
        
        self._increment_by = 5
        
        self.__cmdLUZoom.setAutoRepeat(True)
        self.__cmdLUZoom.setAutoRepeatDelay(repeat_delay)
        self.__cmdLUZoom.setAutoRepeatInterval(repeat_delay)
        
        self.__cmdLDZoom.setAutoRepeat(True)
        self.__cmdLDZoom.setAutoRepeatDelay(repeat_delay)
        self.__cmdLUZoom.setAutoRepeatInterval(repeat_delay)
        
        self.__cmdUDZoom.setAutoRepeat(True)
        self.__cmdUDZoom.setAutoRepeatDelay(repeat_delay)
        self.__cmdLUZoom.setAutoRepeatInterval(repeat_delay)
        
        self.__cmdUUZoom.setAutoRepeat(True)
        self.__cmdUUZoom.setAutoRepeatDelay(repeat_delay)
        self.__cmdLUZoom.setAutoRepeatInterval(repeat_delay)

        hbox.addWidget(self.__cmdLDZoom)
        hbox.addWidget(self.__cmdLUZoom)
        hbox.addWidget(self.__cmdShowAll)
        hbox.addWidget(self.__cmdUDZoom)
        hbox.addWidget(self.__cmdUUZoom)

        hbox.addSpacerItem(QSpacerItem(10, 10))#, QSizePolicy.Expanding, QSizePolicy.Expanding))

        hbox.addWidget(self.__cmdFontMinus)
        hbox.addWidget(self.__cmdFontPlus)

        hbox.addSpacerItem(QSpacerItem(10, 10))#, QSizePolicy.Expanding, QSizePolicy.Expanding))

        hbox.addWidget(self.__lblFigWidth)
        hbox.addWidget(self.__dsbFigWidth)
        hbox.addWidget(self.__lblFigHeight)
        hbox.addWidget(self.__dsbFigHeight)
        
        self.setLayout(hbox)
        self.setTitle("View")
        
        self.__cmdLUZoom.pressed.connect(self.on_cmdLUZoom_pressed)
        self.__cmdLDZoom.pressed.connect(self.on_cmdLDZoom_pressed)
        self.__cmdUUZoom.pressed.connect(self.on_cmdUUZoom_pressed)
        self.__cmdUDZoom.pressed.connect(self.on_cmdUDZoom_pressed)
        self.__cmdShowAll.pressed.connect(self.on_cmdShowAll_pressed)

        self.__cmdFontPlus.pressed.connect(self.on_cmdFontPlus_pressed)
        self.__cmdFontMinus.pressed.connect(self.on_cmdFontMinus_pressed)

        self.__dsbFigWidth.valueChanged.connect(self.on_dsbFigWidth_changed)
        self.__dsbFigHeight.valueChanged.connect(self.on_dsbFigHeight_changed)

        self.setEnabled(False)
    
    def on_cmdLDZoom_pressed(self):
        self.zoom_by_increment.emit('l', -self._increment_by)
    
    def on_cmdLUZoom_pressed(self):
        self.zoom_by_increment.emit('l', self._increment_by)
    
    def on_cmdUDZoom_pressed(self):
        self.zoom_by_increment.emit('u', -self._increment_by)
    
    def on_cmdUUZoom_pressed(self):
        self.zoom_by_increment.emit('u', self._increment_by)
    
    def on_cmdShowAll_pressed(self):
        self.show_all.emit()

    def on_cmdFontPlus_pressed(self):
        self.font_change.emit(+1)

    def on_cmdFontMinus_pressed(self):
        self.font_change.emit(-1)

    def change_fig_size(self, size):
        self.__dsbFigWidth = size[0]
        self.__dsbFigHeight = size[1]

    def on_dsbFigWidth_changed(self):
        # self.fig_size_changed.emit((self.__dsbFigWidth.value(), self.__dsbFigHeight.value()))
        pass

    def on_dsbFigHeight_changed(self):
        # self.fig_size_changed.emit((self.__dsbFigWidth.value(), self.__dsbFigHeight.value()))
        pass

    # def connect_and_emit_trigger(self):
    #     # Connect the trigger signal to a slot.
    #     self.trigger.connect(self.handle_trigger)#
#
#      # Emit the signal.
#       self.trigger.emit()
