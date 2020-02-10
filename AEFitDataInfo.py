from sys import float_info as fli
from fitDataInfo import fitDataInfo
import fitHelper as fh
import numpy as np


class AEFitDataInfo(fitDataInfo):

    def __init__(self, index):
        fitDataInfo.__init__(self, index)
        
        self._minspan = 3.0

        self._AEFrom = 0.0
        self._AETo = np.inf
        self._YFrom = -np.inf
        self._YTo = np.inf
        self._ScaleFrom = -np.inf
        self._ScaleTo = np.inf
        self._AlphaFrom = -np.inf
        self._AlphaTo = np.inf

        self._DomainFrom = 0.0
        self._DomainTo = np.inf

        self._p = [] * 4
        #fit relevant bounds are the bounds for the energy interfal of the last fit that converged
        self._fitRelBounds = [0.0] * 2
        self._fittedFWHM = 0
        self._FWHM = 0

    #def is_initialized(self):
    #    return self._AETo != fli.max

    # get-set-block
    def getFWHM(self):
        return self._FWHM
    
    def setFWHM(self, FWHM):
        self._FWHM = FWHM

    def getMinspan(self):
        return self._minspan
    
    def setMinspan(self, minspan):
        self._minspan = minspan

    def getAEFrom(self, adjusted_for_shift=False):

        if adjusted_for_shift:
            return self._AEFrom - self.get_shift()
        else:
            return self._AEFrom
    
    def setAEFrom(self, AEFrom):
        print(self._AEFrom, '=', AEFrom)
        self._AEFrom = AEFrom
    
    def getAETo(self, adjusted_for_shift=False):

        if adjusted_for_shift:
            return self._AETo - self.get_shift()
        else:
            return self._AETo
    
    def setAETo(self, AETo):
        self._AETo = AETo

    def getYTo(self):
        return self._YTo

    def setYTo(self, YTo):
        self._YTo = YTo

    def getYFrom(self):
        return self._YFrom

    def setYFrom(self, YFrom):
        self._YFrom = YFrom

    def getScaleTo(self):
        return self._ScaleTo

    def setScaleTo(self, ScaleTo):
        self._ScaleTo = ScaleTo

    def getScaleFrom(self):
        return self._ScaleFrom

    def setScaleFrom(self, ScaleFrom):
        self._ScaleFrom = ScaleFrom

    def setAlphaFrom(self, AlphaFrom):
        self._AlphaFrom = AlphaFrom

    def getAlphaFrom(self):
        return self._AlphaFrom

    def setAlphaTo(self, AlphaTo):
        self._AlphaTo = AlphaTo

    def getAlphaTo(self):
        return self._AlphaTo

    def getDomainFrom(self, adjusted_for_shift=False):

        if adjusted_for_shift:
            return self._DomainFrom - self.get_shift()
        else:
            return self._DomainFrom

    def setDomainFrom(self, DomainFrom):
        print(self._DomainFrom, '=', DomainFrom)
        self._DomainFrom = DomainFrom

    def getDomainTo(self, adjusted_for_shift=False):

        if adjusted_for_shift:
            return self._DomainTo - self.get_shift()
        else:
            return self._DomainTo

    def setDomainTo(self, DomainTo):
        self._DomainTo = DomainTo
    
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

    def getYOffset(self, digits=4):
        return round(self._p[0], digits)

    def getYOffset_dev(self, digits=4):
        try:
            return round(self._stdDev[0], digits)
        except:
            return np.nan

    def getFoundAE(self, digits=4):
        return round(self._p[1], digits)

    def getFoundAE_dev(self, digits=4):
        try:
            return round(self._stdDev[1], digits)
        except:
            return np.nan

    def getScaleFactor(self, digits=4):
        return round(self._p[2], digits)

    def getScaleFactor_dev(self, digits=4):
        try:
            return round(self._stdDev[2], digits)
        except:
            return np.nan

    def getAlpha(self, digits=4):
        return round(self._p[3], digits)

    def getAlpha_dev(self, digits=4):
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

    def get_fit_bounds(self):
        lower_bounds = [-np.inf] * 4
        upper_bounds = [np.inf] * 4

        lower_bounds[0], upper_bounds[0] = self.getYFrom(), self.getYTo()
        lower_bounds[1], upper_bounds[1] = self.getAEFrom(), self.getAETo()
        lower_bounds[2], upper_bounds[2] = self.getScaleFrom(), self.getScaleTo()
        lower_bounds[3], upper_bounds[3] = self.getAlphaFrom(), self.getAlphaTo()

        return lower_bounds, upper_bounds

    def fitToFunction(self):
        
        self._p = [0.0] * 4
        self._p[1] = (self._AEFrom + self._AETo) / 2

        weights = None

        if self.is_weighted():
            weights = self._stdErr

        try:
            data, weights, cut_indexes = fh.cutarray2(self.get_data(), self.getDomainFrom(), self.getDomainTo(),
                                                      weights, returnIndexes=True)

            self._p, self._stdDev, self._fitRelBounds[0], self._fitRelBounds[1], self._fittedFWHM, self._fitFunction,\
                message \
                = fh.find_best_fit(data, weights, self._p, self._FWHM, self._minspan, *self.get_fit_bounds(),
                                   self.progressUpdate)
            
            if type(self._stdDev) is not np.ndarray and self._stdDev == -1:
                self._msg = message
                print(message)
            else:
                self._setFitData(fh.data_from_fit_and_parameters(self._data, self._fitFunction, self._p, self._FWHM,
                                                                 domain_indexes=cut_indexes))
                self._msg = self.SUCCESS
        except Exception as e:
            self._setFitData(None)
            self._msg = self.FAILURE + '\n' + str(e)

            print(e)
        
        return self._msg


    def getDomainSpan(self):
        return self.getDomainTo() - self.getDomainFrom()

    def testGoodnessOfMinSpan(self):
        spacing = 0.1
        pm_range = 1
        
        # todo consider data range too
        test_minspan = self._minspan - pm_range

        if test_minspan < 0:
            test_minspan = 0
        elif test_minspan >= self.getDomainSpan():
            test_minspan = self.getDomainSpan()
        
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

        data, weights = fh.cutarray2(self.get_data(), self.getDomainFrom(), self.getDomainTo(), weights)
        
        while test_minspan <= self._minspan + pm_range and test_minspan <= self.getDomainSpan():
            
            p, stdDev, fitRelBounds_x, fitRelBounds_y, fittedFWHM, fitfunc, msg = \
                fh.find_best_fit(data, weights, self._p, self._FWHM, test_minspan,
                                 *self.get_fit_bounds(), self.progressUpdate)
            
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
        super().shift_fit(increment)
        
        if self.isFitted():
            self._p[1] += increment
            self._fitRelBounds[0] += increment
            self._fitRelBounds[1] += increment

    def get_meta_string(self):
        metastring = ""

        if self.isFitted():
            metastring = 'Y-offset = ' + str(self.getYOffset()) + '+-' + str(self.getYOffset_dev()) + ', '
            metastring += 'AE = ' + str(self.getFoundAE()) + '+-' + str(self.getFoundAE_dev()) + ', '
            metastring += 'Scale Factor = ' + str(self.getScaleFactor()) + '+-' + str(self.getScaleFactor_dev()) + ', '
            metastring += 'Alpha = ' + str(self.getAlpha()) + '+-' + str(self.getAlpha_dev())

        return metastring

