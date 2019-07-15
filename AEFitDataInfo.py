from sys import float_info as fli
from fitDataInfo import fitDataInfo
import fitHelper as fh
import numpy as np


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
        self._shift = 0
        self._weighted = True
    
    def is_initialized(self):
        return (self._AETo == fli.max)

    def is_weighted(self):
        return self._weighted

    def set_weighted(self, value):
        self._weighted = value

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
            
        try:
            return round(self._stdDev[0], digits)
        except:
            return np.nan

    def getFoundAE(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._p[1], digits)

    def getFoundAE_dev(self, digits=-1):

        if digits == -1:
            digits = 4

        try:
            return round(self._stdDev[1], digits)
        except:
            return np.nan

    def getScaleFactor(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._p[2], digits)

    def getScaleFactor_dev(self, digits=-1):

        if digits == -1:
            digits = 4
        try:
            return round(self._stdDev[2], digits)
        except:
            return np.nan

    def getAlpha(self, digits=-1):

        if digits == -1:
            digits = 4

        return round(self._p[3], digits)

    def getAlpha_dev(self, digits=-1):

        if digits == -1:
            digits = 4
        
        try:
            return round(self._stdDev[3], digits)
        except:
            return np.nan

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

        weights = None

        if self.is_weighted():
            weights = self._stdErr

        try:
            self._p, self._stdDev, self._fitRelBounds[0], self._fitRelBounds[
                1], self._fittedFWHM, self._fitFunction \
                = fh.find_best_fit(self._data, weights, self._p, self._FWHM, self._minspan, [self._AEFrom, self._AETo],
                     self.progressUpdate)
            
            self._setFitData(fh.data_from_fit_and_parameters(self._data, self._fitFunction, self._p, self._FWHM,
                                                             continuation=True))
            
            self._msg = self.SUCCESS
        except:
            self._setFitData(None)
            self._msg = "Error while fitting."
        
        return self._msg
    
    
    def testGoodnessOfMinSpan(self):
        spacing = 0.1
        pm_range = 1
        
        # todo consider data range too
        test_minspan = self._minspan - pm_range
        
        y_offsets = np.array([])
        aes = np.array([])
        scale_factors = np.array([])
        alphas = np.array([])
        
        y_offset_errs = np.array([])
        ae_errs = np.array([])
        scale_factor_errs = np.array([])
        alpha_errs = np.array([])
        
        minspans = np.array([])
        
        weights = None

        if self.is_weighted():
            weights = self._stdErr
        
        while test_minspan <= self._minspan + pm_range:
            
            p, stdDev, fitRelBounds_x, fitRelBounds_y, fittedFWHM, fitfunc = \
                fh.find_best_fit(self._data, weights, self._p, self._FWHM, test_minspan,
                                 [self._AEFrom, self._AETo], self.progressUpdate)
            
            y_offsets = np.append(y_offsets, p[0])
            y_offset_errs = np.append(y_offset_errs, stdDev[0])
            
            aes = np.append(aes, p[1])
            ae_errs = np.append(ae_errs, stdDev[1])
            
            scale_factors = np.append(scale_factors, p[2])
            scale_factor_errs = np.append(scale_factor_errs, stdDev[2])
            
            alphas = np.append(alphas, p[3])
            alpha_errs = np.append(alpha_errs, stdDev[3])
            
            minspans = np.append(minspans, test_minspan)
            
            test_minspan += spacing
            
        return minspans, y_offsets, aes, scale_factors, alphas, y_offset_errs, ae_errs, scale_factor_errs, alpha_errs
            
    
    def progressUpdate(self, relation, info):
        if self._passProgressUpdate is not None:
            self._passProgressUpdate(relation, info.tolist())
    
    def shift_fit(self, increment):
        
        self._shift += increment
        #fitDataInfo.shift_fit(increment)
        if self.isFitted():
            for set in self._fitData:
                set[0] += increment

            self._p[1] += increment
            self._fitRelBounds[0] += increment
            self._fitRelBounds[1] += increment

        for set in self._data:
            set[0] += increment


    def get_meta_string(self):
        metastring = 'y-offset = ' + str(self.getYOffset()) + '±' + str(self.getYOffset_dev()) + ' '
        metastring += 'AE = ' + str(self.getFoundAE()) + '±' + str(self.getFoundAE_dev()) + ' '
        metastring += 'Scale Factor = ' + str(self.getScaleFactor()) + '±' + str(self.getScaleFactor_dev()) + ' '
        metastring += 'Alpha = ' + str(self.getAlpha()) + '±' + str(self.getAlpha_dev())

        return metastring

