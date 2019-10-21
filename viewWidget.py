from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout,\
    QPlainTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
from sys import float_info as fli
import dataDisplay as dd
from InftyDoubleSpinBox import InftyDoubleSpinBox
import helplib as hl
import fitDataInfo as fdi
import numpy as np


class viewWidget(QGroupBox):

    show_all = pyqtSignal()
    zoom_by_increment = pyqtSignal(str, int)
    scale_font_size_changed = pyqtSignal(float)
    label_font_size_changed = pyqtSignal(float)
    fig_size_changed = pyqtSignal(tuple)
    annotation_changed = pyqtSignal(str)
    annotation_font_size_changed = pyqtSignal(float)
    resizing_changed = pyqtSignal(bool)

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

        self.__lblLabelFontSize = QLabel("Label font size:")
        self.__dsbLabelFontSize = InftyDoubleSpinBox(min=1)
        self.__dsbLabelFontSize.setSingleStep(0.5)
        self.__dsbLabelFontSize.setMaximumWidth(75)
        
        self.__lblScaleFontSize = QLabel("Scale font size:")
        self.__dsbScaleFontSize = InftyDoubleSpinBox(min=1)
        self.__dsbScaleFontSize.setSingleStep(0.5)
        self.__dsbScaleFontSize.setMaximumWidth(75)

        self.__lblFigHeight = QLabel("Height: ")
        self.__lblFigWidth = QLabel("Width: ")

        self.__dsbFigHeight = InftyDoubleSpinBox(min=1)
        self.__dsbFigWidth = InftyDoubleSpinBox(min=1)

        self.__dsbFigHeight.setSingleStep(0.1)
        self.__dsbFigHeight.setMaximumWidth(75)

        self.__dsbFigWidth.setSingleStep(0.1)
        self.__dsbFigWidth.setMaximumWidth(75)

        self.__edtAnnotation = QPlainTextEdit("")
        self.__edtAnnotation.setFixedHeight(90)

        self.__lblAnnotationFontSize = QLabel("Font size:")
        self.__dsbAnnotationFontSize = InftyDoubleSpinBox(min=1)
        self.__cmdRefreshAnnotation = QPushButton('Apply')

        self.__dsbAnnotationFontSize.setSingleStep(0.5)
        self.__dsbAnnotationFontSize.setMaximumWidth(75)

        #self.setFixedHeight(50)

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
        
        self.__figSizeGroupBox = QGroupBox("Figure Size (in inches)")
        self.__figSizeGroupBox.setCheckable(True)
        self.__figSizeGroupBox.clicked.connect(self.__fig_size_enabled)

        self.__figSizeLayout = QGridLayout()
        self.__figSizeGroupBox.setLayout(self.__figSizeLayout)

        self.__figSizeLayout.addWidget(self.__lblFigWidth, 0, 0)
        self.__figSizeLayout.addWidget(self.__dsbFigWidth, 0, 1)
        self.__figSizeLayout.addWidget(self.__lblFigHeight, 1, 0)
        self.__figSizeLayout.addWidget(self.__dsbFigHeight, 1, 1)

        hbox_fig_sizes.addWidget(self.__figSizeGroupBox)

        self.__labelSizeGroupBox = QGroupBox("Label Size")
        self.__labelSizeLayout = QGridLayout()
        self.__labelSizeGroupBox.setLayout(self.__labelSizeLayout)

        self.__labelSizeLayout.addWidget(self.__lblLabelFontSize, 0, 0)
        self.__labelSizeLayout.addWidget(self.__dsbLabelFontSize, 0, 1)
        self.__labelSizeLayout.addWidget(self.__lblScaleFontSize, 1, 0)
        self.__labelSizeLayout.addWidget(self.__dsbScaleFontSize, 1, 1)

        hbox_fig_sizes.addWidget(self.__labelSizeGroupBox)

        self.__annotationGroupBox = QGroupBox("Annotation")
        self.__annotationLayout = QGridLayout()
        self.__annotationGroupBox.setLayout(self.__annotationLayout)

        self.__annotationLayout.addWidget(self.__edtAnnotation, 0, 0, -1, 1)
        self.__annotationLayout.addWidget(self.__lblAnnotationFontSize, 0, 1, 1, 1)
        self.__annotationLayout.addWidget(self.__dsbAnnotationFontSize, 1, 1, 1, 1)
        self.__annotationLayout.addWidget(self.__cmdRefreshAnnotation, 2, 1, 1, 1)

        hbox_fig_sizes.addWidget(self.__annotationGroupBox)

        v_box = QVBoxLayout()
        v_box.addLayout(hbox_fig_sizes)
        #v_box.addLayout(hbox_zoom)

        hbox_main.addLayout(v_box)
        hbox_main.addLayout(hbox_annotation)
        hbox_main.setAlignment(Qt.AlignTop)

        self.setLayout(hbox_main)
        self.setTitle("Figure Settings")
        
        self.__cmdLUZoom.pressed.connect(self.on_cmdLUZoom_pressed)
        self.__cmdLDZoom.pressed.connect(self.on_cmdLDZoom_pressed)
        self.__cmdUUZoom.pressed.connect(self.on_cmdUUZoom_pressed)
        self.__cmdUDZoom.pressed.connect(self.on_cmdUDZoom_pressed)
        self.__cmdShowAll.pressed.connect(self.on_cmdShowAll_pressed)

        self.__dsbFigHeight.editingFinished.connect(self.apply_fig_size)
        self.__dsbFigWidth.editingFinished.connect(self.apply_fig_size)

        self.__dsbLabelFontSize.editingFinished.connect(self.on_dsb_label_font_size_changed)
        self.__dsbScaleFontSize.editingFinished.connect(self.on_dsb_scale_font_size_changed)
        self.__dsbAnnotationFontSize.editingFinished.connect(self.on_dsb_annotation_font_size_changed)

        #self.__dsbFigWidth.editingFinished.connect(self.on_dsbFigWidth_changed)
        #self.__dsbFigHeight.editingFinished.connect(self.on_dsbFigHeight_changed)

        self.__cmdRefreshAnnotation.pressed.connect(self.on_annotation_changed)
        
        self.setEnabled(False)

    def reset(self, enabled=True):
        self.__figSizeGroupBox.setChecked(False)
        self.set_fig_size((dd.DataDisplay.std_fig_width, dd.DataDisplay.std_fig_height))

        self.set_label_font_size(dd.DataDisplay.std_label_font_size)
        self.set_scale_font_size(dd.DataDisplay.std_scale_font_size)
        self.set_annotation_font_size(dd.DataDisplay.std_ann_font_size)

        self.set_annotation_text('')

        self.setEnabled(enabled)

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

    def on_dsb_label_font_size_changed(self):
        self.label_font_size_changed.emit(self.get_label_font_size())
    
    def on_dsb_scale_font_size_changed(self):
        self.scale_font_size_changed.emit(self.__dsbScaleFontSize.value())
    
    def on_dsb_annotation_font_size_changed(self):
        self.annotation_font_size_changed.emit(self.get_annotation_font_size())

    #def on_dsbFigWidth_changed(self):
    #    self.fig_size_changed.emit((self.__dsbFigWidth.value(), self.__dsbFigHeight.value()))

    #def on_dsbFigHeight_changed(self):
    #    self.fig_size_changed.emit((self.__dsbFigWidth.value(), self.__dsbFigHeight.value()))

    def apply_fig_size(self, enabled=True):
        if enabled:
            self.fig_size_changed.emit((self.__dsbFigWidth.value(), self.__dsbFigHeight.value()))
        else:
            self.fig_size_changed.emit((None, None))

    def __fig_size_enabled(self, enabled):

        #if checkbox is checked resizing is not enabled and vice versa
        self.resizing_changed.emit(not enabled)
        self.apply_fig_size(enabled)

    def on_annotation_changed(self):
        self.annotation_changed.emit(self.__edtAnnotation.toPlainText())

    def apply_all(self):
        self.on_annotation_changed()
        self.apply_fig_size(self.is_fig_size_enabled())

        self.label_font_size_changed.emit(self.get_label_font_size())
        self.scale_font_size_changed.emit(self.__dsbScaleFontSize.value())
        self.annotation_font_size_changed.emit(self.get_annotation_font_size())


    def load_from_view_string(self, view_string):
        if view_string is not None:
            split_string = view_string.split('\t')

            try:
                for i in range(0, len(split_string)):
                    item = split_string[i].split('=')

                    if len(item) == 2:
                        if (item[0] == 'atx'):  # annotation text
                            self.set_annotation_text(str(item[1]).replace('\\n', '\n'))
                        elif (item[0] == 'afs'):  # annotation font size
                            self.set_annotation_font_size(float(item[1]))
                        elif (item[0] == 'fiw'):  # fig size width
                            self.set_fig_size((float(item[1]), None))
                        elif (item[0] == 'fih'):  # fig size height
                            self.set_fig_size((None, float(item[1])))
                        elif (item[0] == 'lfs'):  # label font size
                            self.set_label_font_size(float(item[1]))
                        elif (item[0] == 'sfs'):  # scale font size
                            self.set_scale_font_size(float(item[1]))
                        elif (item[0] == 'fse'):  # fig size enabled
                            if item[0] == '1' or item[0] == 'True':
                                self.set_fig_size_enabled(True)
                            else:
                                self.set_fig_size_enabled(False)
                            print('fse=', item[1])

            except:
                return 'Meta data might be corrupted.'

    def get_view_string(self):
        atx = self.get_annotation_text().replace('\n', '\\n')
        afs = str(self.get_annotation_font_size())
        fiw = str(self.get_fig_size()[0])
        fih = str(self.get_fig_size()[1])
        lfs = str(self.get_label_font_size())
        sfs = str(self.get_scale_font_size())
        
        
        return 'atx=' + atx + '\t' +\
                'afs=' + afs + '\t' +\
                'fiw=' + fiw + '\t' +\
                'fih=' + fih + '\t' +\
                'lfs=' + lfs + '\t' +\
                'sfs=' + sfs + '\t' +\
                'fse=' + str(self.is_fig_size_enabled())

    def is_fig_size_enabled(self):
        return self.__figSizeGroupBox.isChecked()

    def set_fig_size_enabled(self, value):
        self.__figSizeGroupBox.setChecked(value)

    def get_annotation_text(self):
        return self.__edtAnnotation.toPlainText()
    
    def set_annotation_text(self, text):
        self.__edtAnnotation.setPlainText(text)
        
    def get_annotation_font_size(self):
        return self.__dsbAnnotationFontSize.value()
    
    def set_annotation_font_size(self, value):
        self.__dsbAnnotationFontSize.setValue(value)
    
    def get_label_font_size(self):
        return self.__dsbLabelFontSize.value()
    
    def set_label_font_size(self, value):
        self.__dsbLabelFontSize.setValue(value)
    
    def get_scale_font_size(self):
        return self.__dsbScaleFontSize.value()
    
    def set_scale_font_size(self, value):
        self.__dsbScaleFontSize.setValue(value)

    def set_fig_size(self, size):
        if size[0] != None:
            self.__dsbFigWidth.setValue(size[0])
        if size[1] != None:
            self.__dsbFigHeight.setValue(size[1])
            
    def get_fig_size(self):
        return (self.__dsbFigWidth.value(), self.__dsbFigHeight.value())

    # def connect_and_emit_trigger(self):
    #     # Connect the trigger signal to a slot.
    #     self.trigger.connect(self.handle_trigger)#
#
#      # Emit the signal.
#       self.trigger.emit()
