import sys
from fitDataInfo import fitDataInfo
import fitHelper as fh

class polyFitDataInfo(fitDataInfo):

    def __init__(self, index):
        fitDataInfo.__init__(self, index)
        
        self._n = 0
        self._To = sys.float_info.max
        self._From = 0

    def is_initialized(self):
        return (self._To == sys.float_info.max)
    
    # get-set-block
    def getDegree(self):
        return self._n
    
    def setDegree(self, n):
        self._n = n
    
    def getFitFunc(self):
        return fh.str_fit_func(self._p, self._FWHM)
    
    def getName(self):
        name = "Fit #" + str(self.get_fit_index() + 1)
        
        if self.isFitted():
            name += "( = " + str(self.getFoundAE()) + ")"
        return "Fit #" + str(self.get_fit_index() + 1)
    
    def fitToFunction(self):
        
        pass
    
    def progressUpdate(self, relation, info):
        if self._passProgressUpdate is not None:
            self._passProgressUpdate(relation, info.tolist())
    
    def shift_fit(self, increment):
        #fitDataInfo.shift_fit(increment)
        if self.isFitted():
            for set in self._fitData:
                set[0] += increment

            self._p[1] += increment
            self._fitRelBounds[0] += increment
            self._fitRelBounds[1] += increment

        for set in self._data:
            set[0] += increment
            