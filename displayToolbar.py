from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import pyqtSignal

from sys import float_info as fli
from fitDataInfo import fitDataInfo
import fitHelper as fh
import numpy as np


class displayToolbar(NavigationToolbar):

    show_all = pyqtSignal()

    def __init__(self, canvas_, parent_):

        # self.toolitems = (
        #     ('Home', 'Show all data', 'home', 'home'),
        #     # ('Back', 'consectetuer adipiscing elit', 'back', 'back'),
        #     # ('Forward', 'sed diam nonummy nibh euismod', 'forward', 'forward'),
        #     # (None, None, None, None),
        #     ('Pan', 'Pan axes with', 'move', 'pan'),
        #     ('Zoom', 'dolore magna aliquam', 'zoom_to_rect', 'zoom'),
        #     (None, None, None, None),
        #     ('Subplots', 'putamus parum claram', 'subplots', 'configure_subplots'),
        #     ('Save', 'sollemnes in futurum', 'filesaver', 'save_figurea'))

        NavigationToolbar.__init__(self, canvas_, parent_)

        self.reset(enabled=False)

    def reset(self, enabled=True):

        self.setEnabled(enabled)

    def zoom(self, *args):
        super().zoom(args)
        print(args)


    def save_figurea(self, *args):
        pass

    def home(self, *args):
        self.show_all.emit()

    #def drag_zoom(self, event):
    #    pass

    def release_zoom(self, event):
        print(event)
        e = super().release_zoom(event)
        print(e)