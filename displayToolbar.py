from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import pyqtSignal

from sys import float_info as fli
from fitDataInfo import fitDataInfo
import fitHelper as fh
import numpy as np


class displayToolbar(NavigationToolbar):

    show_all = pyqtSignal()

    def __init__(self, canvas_, parent_):

        self.toolitems = (
            #('Home', 'Reset original view', 'home', 'home')
            ('Home', 'Show all data', 'home', 'home'),
            ('Back', 'Back to previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            (None, None, None, None),
            ('Save', 'Save the figure as shown (including dimensions)', 'filesave', 'save_figure'))

        NavigationToolbar.__init__(self, canvas_, parent_)

        self.reset(enabled=False)

    def reset(self, enabled=True):

        self.setEnabled(enabled)

    def zoom(self, *args):
        super().zoom(args)
        print(args)


#    def save_figurea(self, *args):
#        pass

    def home(self, *args):
        self.show_all.emit()

#    def release_zoom(self, event):
#        print(event)
#        e = super().release_zoom(event)
#        print(e)