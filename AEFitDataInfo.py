from sys import float_info as fli
from fitDataInfo import fitDataInfo
import fitHelper as fh


class AEFitDataInfo(fitDataInfo):

    def __init__(self, index):
        fitDataInfo.__init__(self, index)
        
        self._minspan = 3.0
        self._AEFrom = 0.0
        self._AETo = fli.max
        self._p = [] * 4
        self._fitRelBounds = [0.0] * 2
        self._fittedFWHM = 0
        self._FWHM = 0
    
    def is_initialized(self):
        return (self._AETo == fli.max)
    
    # get-set-block
    def getFWHM(self):
        return self._FWHM
    
    def setFWHM(self, FWHM):
        self._FWHM = FWHM
    
    def getMinspan(self):
        return self._minspan
    
    def setMinspan(self, minspan):
        self._minspan = minspan
    
    def getAEFrom(self):
        return self._AEFrom
    
    def setAEFrom(self, AEFrom):
        self._AEFrom = AEFrom
    
    def getAETo(self):
        return self._AETo
    
    def setAETo(self, AETo):
        self._AETo = AETo
    
    def getFitRelFrom(self):
        return self._fitRelBounds[0]
    
    def setFitRelFrom(self, fitRelFrom):
        self._fitRelBounds[0] = fitRelFrom
    
    def getFitRelTo(self):
        return self._fitRelBounds[1]
    
    def setFitRelTo(self, fitRelTo):
        self._fitRelBounds[1] = fitRelTo
    
    def getParameters(self):
        return self._p
    
    def setParameters(self, value):
        self._p = value

    def getYOffset(self, digits=-1):
        if digits == -1:
            digits = 4

        return round(self._p[0], digits)

    def getYOffset_dev(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._stdDev[0], digits)

    def getFoundAE(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._p[1], digits)

    def getFoundAE_dev(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._stdDev[1], digits)

    def getScaleFactor(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._p[2], digits)

    def getScaleFactor_dev(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._stdDev[2], digits)

    def getAlpha(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._p[3], digits)

    def getAlpha_dev(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._stdDev[3], digits)

    def getFittedFWHM(self):
        return self._fittedFWHM

    def getFitFunc(self):
        return fh.str_fit_func(self._p, self._FWHM)
    
    def getName(self):
        name = "Fit #" + str(self.get_fit_index() + 1)
        
        if self.isFitted():
            name += "( = " + str(self.getFoundAE()) + ")"
        return "Fit #" + str(self.get_fit_index() + 1)
    
    def fitToFunction(self):
        
        self._p = [0.0] * 4
        self._p[1] = (self._AEFrom + self._AETo) / 2
        
        try:
            self._p, self._stdDev, self._fitRelBounds[0], self._fitRelBounds[
                1], self._fittedFWHM, self._fitFunction \
                = fh.find_best_fit(self._data, self._p, self._FWHM, self._minspan, [self._AEFrom, self._AETo],
                     self.progressUpdate)
            
            self._setFitData(fh.data_from_fit_and_parameters(self._data, self._fitFunction, self._p, self._FWHM,
                                                             continuation=True))
            
            self._msg = self.SUCCESS
        except:
            self._setFitData(None)
            self._msg = "Error while fitting."
        
        return self._msg
    
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
            