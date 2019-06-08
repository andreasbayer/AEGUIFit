from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QGroupBox, QSpacerItem
from PyQt5.QtCore import pyqtSignal
import helplib as hl
import fitDataInfo as fdi
import numpy as np


class ZoomButtonWidget(QGroupBox):
    show_all = pyqtSignal()
    zoom_by_increment = pyqtSignal(str, int)
    font_change = pyqtSignal(int)
    
    def __init__(self):
        QWidget.__init__(self)
        
        hbox = QHBoxLayout()
        
        self.cmdLDZoom = QPushButton("<-L")
        self.cmdLUZoom = QPushButton("L->")
        self.cmdUDZoom = QPushButton("<-U")
        self.cmdUUZoom = QPushButton("U->")
        self.cmdShowAll = QPushButton("Show All")

        self.cmdFontPlus = QPushButton("Font+")
        self.cmdFontMinus = QPushButton("Font-")
        
        repeat_delay = 0
        
        self._increment_by = 5
        
        self.cmdLUZoom.setAutoRepeat(True)
        self.cmdLUZoom.setAutoRepeatDelay(repeat_delay)
        self.cmdLUZoom.setAutoRepeatInterval(repeat_delay)
        
        self.cmdLDZoom.setAutoRepeat(True)
        self.cmdLDZoom.setAutoRepeatDelay(repeat_delay)
        self.cmdLUZoom.setAutoRepeatInterval(repeat_delay)
        
        self.cmdUDZoom.setAutoRepeat(True)
        self.cmdUDZoom.setAutoRepeatDelay(repeat_delay)
        self.cmdLUZoom.setAutoRepeatInterval(repeat_delay)
        
        self.cmdUUZoom.setAutoRepeat(True)
        self.cmdUUZoom.setAutoRepeatDelay(repeat_delay)
        self.cmdLUZoom.setAutoRepeatInterval(repeat_delay)

        hbox.addWidget(self.cmdLDZoom)
        hbox.addWidget(self.cmdLUZoom)
        hbox.addWidget(self.cmdShowAll)
        hbox.addWidget(self.cmdUDZoom)
        hbox.addWidget(self.cmdUUZoom)

        hbox.addSpacerItem(QSpacerItem(10, 10))#, QSizePolicy.Expanding, QSizePolicy.Expanding))

        hbox.addWidget(self.cmdFontMinus)
        hbox.addWidget(self.cmdFontPlus)
        
        self.setLayout(hbox)
        self.setTitle("View")
        
        self.cmdLUZoom.pressed.connect(self.on_cmdLUZoom_pressed)
        self.cmdLDZoom.pressed.connect(self.on_cmdLDZoom_pressed)
        self.cmdUUZoom.pressed.connect(self.on_cmdUUZoom_pressed)
        self.cmdUDZoom.pressed.connect(self.on_cmdUDZoom_pressed)
        self.cmdShowAll.pressed.connect(self.on_cmdShowAll_pressed)

        self.cmdFontPlus.pressed.connect(self.on_cmdFontPlus_pressed)
        self.cmdFontMinus.pressed.connect(self.on_cmdFontMinus_pressed)
        
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

    # def connect_and_emit_trigger(self):
    #     # Connect the trigger signal to a slot.
    #     self.trigger.connect(self.handle_trigger)#
#
#      # Emit the signal.
#       self.trigger.emit()
