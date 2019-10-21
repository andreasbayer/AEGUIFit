from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QPlainTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
from sys import float_info as fli
import dataDisplay as dd

class metaInfoWidget(QGroupBox):
    #show_all = pyqtSignal()
    #zoom_by_increment = pyqtSignal(str, int)
    #scale_font_size_changed = pyqtSignal(float)
    #label_font_size_changed = pyqtSignal(float)
    #fig_size_changed = pyqtSignal(tuple)
    #annotation_changed = pyqtSignal(str)
    #annotation_font_size_changed = pyqtSignal(float)
    #resizing_changed = pyqtSignal(bool)

    def __init__(self):
        QWidget.__init__(self)
        
        hbox_main = QHBoxLayout()

        #self.__lblNotes = QLabel("Notes")
        self.__edtNotes = QPlainTextEdit("")
        self.__edtNotes.setFixedHeight(120)

        #hbox_main.addWidget(self.__lblNotes)
        hbox_main.addWidget(self.__edtNotes)

        self.setLayout(hbox_main)
        self.setTitle("Notes")
        
        self.setEnabled(False)

    def reset(self, enabled=True):
        self.setEnabled(enabled)
        self.setNotes('')

    def getNotes(self):
        return self.__edtNotes.toPlainText()

    def setNotes(self, value):
        self.__edtNotes.setPlainText(value)

    def load_from_meta_string(self, view_string):
        if view_string is not None:
            split_string = view_string.split('\t')

            try:
                for i in range(0, len(split_string)):
                    item = split_string[i].split('=')
                    if len(item) == 2:
                        if (item[0] == 'nts'):
                            self.setNotes(str(item[1]).replace('\\n', '\n'))
            except:
                return 'Meta data might be corrupted.'

    def get_meta_string(self):
        print('getmetastring')
        nts = self.getNotes().replace('\n', '\\n')
        return 'nts=' + nts
