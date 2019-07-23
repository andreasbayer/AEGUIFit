from PyQt5.QtWidgets import QWidget, QTabWidget
from PyQt5.QtCore import pyqtSignal


class tabFits(QTabWidget):
    
    fit_index_changed = pyqtSignal(int)
    
    def __init__(self):
        QTabWidget.__init__(self)
        self.reset()
    
    def reset(self):
        self.clear()
        self.addTab(QWidget(), "General")
        self.setFixedHeight(20)
        self.currentChanged.connect(self.current_changed)
        
    def addFit(self, p_fitDataInfo):
        #if fiw.get_fit_index() == -1:
        #    fiw.get_fit_index() = self.count()
        
        #if self.isVisible() == False and index > 0:
        #    self.setVisible(True)
        
        self.addTab(QWidget(), p_fitDataInfo.getName())
        
    def removeFit(self, fit_index):
        self.removeTab(fit_index+1)
    
    def current_changed(self, p_int):
        print('tab count', p_int)
        if self.count() >= 1:
            self.fit_index_changed.emit(p_int-1)
