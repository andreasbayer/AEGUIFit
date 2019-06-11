from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QSpacerItem,\
    QDoubleSpinBox, QPlainTextEdit
from PyQt5.QtCore import pyqtSignal
from sys import float_info as fli
import helplib as hl
import fitDataInfo as fdi
import numpy as np


class ZoomButtonWidget(QGroupBox):
    show_all = pyqtSignal()
    zoom_by_increment = pyqtSignal(str, int)
    font_size_changed = pyqtSignal(float)
    fig_size_changed = pyqtSignal(tuple)
    annotation_changed = pyqtSignal(str)
    
    def __init__(self):
        QWidget.__init__(self)
        
        hbox_main = QHBoxLayout()
        hbox_zoom = QHBoxLayout()
        hbox_fig_sizes = QHBoxLayout()
        hbox_annotation = QHBoxLayout()
        
        self.__cmdLDZoom = QPushButton("<-L")
        self.__cmdLUZoom = QPushButton("L->")
        self.__cmdUDZoom = QPushButton("<-U")
        self.__cmdUUZoom = QPushButton("U->")
        self.__cmdShowAll = QPushButton("Show All")

        self.__lblFontSize = QLabel("Font size:")
        self.__dsbFontSize = QDoubleSpinBox()
        self.__dsbFontSize.setRange(1, fli.max)
        self.__dsbFontSize.setValue(12)
        self.__dsbFontSize.setSingleStep(0.5)

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

        self.__lblAnnotation = QLabel("Annotation:")
        self.__edtAnnotation = QPlainTextEdit("")
        self.__edtAnnotation.setFixedHeight(100)

        self.setFixedHeight(135)


        repeat_delay = 0
        
        self._increment_by = 1
        
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

        hbox_zoom.addWidget(self.__cmdLDZoom)
        hbox_zoom.addWidget(self.__cmdLUZoom)
        hbox_zoom.addWidget(self.__cmdShowAll)
        hbox_zoom.addWidget(self.__cmdUDZoom)
        hbox_zoom.addWidget(self.__cmdUUZoom)

        hbox_fig_sizes.addWidget(self.__lblFontSize)
        hbox_fig_sizes.addWidget(self.__dsbFontSize)

        hbox_fig_sizes.addWidget(self.__lblFigWidth)
        hbox_fig_sizes.addWidget(self.__dsbFigWidth)
        hbox_fig_sizes.addWidget(self.__lblFigHeight)
        hbox_fig_sizes.addWidget(self.__dsbFigHeight)

        hbox_annotation.addWidget(self.__lblAnnotation)
        hbox_annotation.addWidget(self.__edtAnnotation)

        v_box = QVBoxLayout()
        v_box.addLayout(hbox_fig_sizes)
        v_box.addLayout(hbox_zoom)

        hbox_main.addLayout(v_box)
        hbox_main.addLayout(hbox_annotation)

        self.setLayout(hbox_main)
        self.setTitle("Figure")
        
        self.__cmdLUZoom.pressed.connect(self.on_cmdLUZoom_pressed)
        self.__cmdLDZoom.pressed.connect(self.on_cmdLDZoom_pressed)
        self.__cmdUUZoom.pressed.connect(self.on_cmdUUZoom_pressed)
        self.__cmdUDZoom.pressed.connect(self.on_cmdUDZoom_pressed)
        self.__cmdShowAll.pressed.connect(self.on_cmdShowAll_pressed)

        self.__dsbFontSize.valueChanged.connect(self.on_dsb_font_size_changed)

        self.__dsbFigWidth.valueChanged.connect(self.on_dsbFigWidth_changed)
        self.__dsbFigHeight.valueChanged.connect(self.on_dsbFigHeight_changed)

        self.__edtAnnotation.textChanged.connect(self.on_annotation_changed)

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

    def on_dsb_font_size_changed(self):
        self.font_size_changed.emit(self.__dsbFontSize.value())

    def change_fig_size(self, size):
        self.__dsbFigWidth = size[0]
        self.__dsbFigHeight = size[1]

    def on_dsbFigWidth_changed(self):
        self.fig_size_changed.emit((self.__dsbFigWidth.value(), self.__dsbFigHeight.value()))

    def on_dsbFigHeight_changed(self):
        self.fig_size_changed.emit((self.__dsbFigWidth.value(), self.__dsbFigHeight.value()))

    def on_annotation_changed(self):
        self.annotation_changed.emit(self.__edtAnnotation.toPlainText())

    # def connect_and_emit_trigger(self):
    #     # Connect the trigger signal to a slot.
    #     self.trigger.connect(self.handle_trigger)#
#
#      # Emit the signal.
#       self.trigger.emit()
