#from PyQt5 import Qt
from PyQt5.QtWidgets import QFileDialog, QCheckBox, QVBoxLayout


class flSaveFileDialog(QFileDialog):

    def __init__(self):
        QFileDialog.__init__(self)
        
        #self.setOption(QFileDialog.DontUseNativeDialog)

        #chkMeasuredData = QCheckBox('Include Measured Data')
        #chkErrors = QCheckBox('Include Errors')
        
        #self.layout().addWidget(chkMeasuredData)
        #self.layout().addWidget(chkErrors)

    #def getSaveFileName(self, "Save File", "", "*.txt")
    #def getSaveFileName(self, parent=None, caption='', directory='', filter='', initialFilter='', options=None, QFileDialog_Options=None, QFileDialog_Option=None, *args, **kwargs):
        
    #    a, b = QFileDialog.getSaveFileName(self, parent, caption, directory, filter, initialFilter, options, QFileDialog_Options, *args, **kwargs)
        #a, b = QFileDialog.getSaveFileName(self, parent, caption, directory, filter, initialFilter)
        #a, b = QFileDialog.getSaveFileName(self, parent, caption, directory, filter, initialFilter)

    #    return a, b