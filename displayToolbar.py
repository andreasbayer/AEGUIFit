from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from sys import float_info as fli
from fitDataInfo import fitDataInfo
import fitHelper as fh
import numpy as np


class displayToolbar(NavigationToolbar):


    def zoom(self, *args):
        super().zoom(args)
        print(args)


    #def drag_zoom(self, event):
    #    pass

    def release_zoom(self, event):
        print(event)
        e = super().release_zoom(event)
        print(e)