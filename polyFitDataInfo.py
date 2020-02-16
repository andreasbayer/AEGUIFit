import sys
from fitDataInfo import fitDataInfo
import fitHelper as fh
import numpy as np

class polyFitDataInfo(fitDataInfo):

    def __init__(self, index):
        fitDataInfo.__init__(self, index)
        
        self._n = 0
        self._FitTo = sys.float_info.max
        self._FitFrom = 0
        self._p = []
        self._poly_cont = []
        self._residuals = []
        self._degree_of_continuation = self._n
        #self.

    #def is_initialized(self):
    #    return (self._FitTo == sys.float_info.max)
    
    # get-set-block
    def getDegreeOfContinuation(self):
        return int(self._degree_of_continuation)
    
    def setDegreeOfContinuation(self, degree_of_continuation):
        self._degree_of_continuation = degree_of_continuation

    def getDegree(self):
        return self._n

    def setDegree(self, n):
        self._n = n

    def getFitTo(self, adjusted_for_shift=False):
        if adjusted_for_shift:
            return self._FitTo - self.get_shift()
        else:
            return self._FitTo

    def setFitTo(self, value):
        self._FitTo = value

    def getFitFrom(self, adjusted_for_shift=False):
        if adjusted_for_shift:
            return self._FitFrom - self.get_shift()
        else:
            return self._FitFrom

    def setFitFrom(self, value):
        self._FitFrom = value

    def getFitFunc(self):
        return "Poly Func" #fh.str_fit_func(self._p, self._FWHM)
    
    def getName(self):
        return "Poly-Fit #" + str(self.get_fit_index() + 1)

    def getParameters(self):
        return self._p

    def getResiduals(self):
        return self._residuals

    def fitToFunction(self):
        data = self.get_data()

        weights = None

        self.progressUpdate(0, '')

        if self.is_weighted():
            weights = fh.fix_std_errs(self.get_std_err())
            cut_data, weights = fh.cutarray2(data=data, lowerlim=self.getFitFrom(), upperlim=self.getFitTo(),
                                             data2=weights)
        else:
            cut_data = fh.cutarray2(data=data, lowerlim=self.getFitFrom(), upperlim=self.getFitTo())

        try:
            self._p, arr1, deg, self._residuals, val = \
                np.polyfit(cut_data[:, 0], cut_data[:, 1], self.getDegree(), w=weights, full=True, cov=True)

            #self._p_cont = fh.taylor(np.poly(self._p),  self.getFitTo(), self.getDegreeOfContinuation())
            self._poly_cont = fh.find_continuation_taylor_poly(self._p, self.getDegreeOfContinuation(), self.getFitTo())

            full_fitdata = np.array([data[:, 0], np.polyval(self._p, data[:, 0])]).transpose()
            full_ep_data = np.array([data[:, 0], self._poly_cont(data[:, 0])]).transpose()
            fitdata = list()

            self.progressUpdate(0.5, '')

            for i in range(0, len(full_fitdata)):
                energy = full_fitdata[i][0]

                if energy < self.getFitFrom():  # data points before fit area
                    fitdata.append([energy, 0.0])
                elif energy > self.getFitTo():  # data points after fit area
                    fitdata.append(full_ep_data[i])
                else:  # data points in fit area
                    fitdata.append(full_fitdata[i])

            fitdata = np.array(fitdata)

            self.progressUpdate(0.75, '')

            self._setFitData(fitdata)
            self._msg = self.SUCCESS

            self.progressUpdate(1, '')
        except:
            self._setFitData(None)
            self._msg = self.FAILURE

            self.progressUpdate(0, '')

        return self._msg
    
    def progressUpdate(self, relation, info):
        if self._passProgressUpdate is not None:
            self._passProgressUpdate(relation, info)
    
    def shift_fit(self, increment):
        super().shift_fit(increment)

    def get_meta_string(self):
        metastring = ""
        p = self.getParameters()
        residuals = self.getResiduals()
    
        for i in reversed(range(0, len(p))):
            digits_of_error = 2
        
            par_str, err_str = fh.roundToErrorStrings(p[i], residuals[i], digits_of_error)
        
            metastring += 'a_' + str(round(i)) + ': ' + par_str + ' +- ' + err_str
            if i >= 0:
                metastring += ", "
                
        metastring += "domain: [" + str(self.getFitFrom()) + "eV ," + str(self.getFitTo()) + "eV]"
    
        
        return metastring

    def get_fit_info_string(self):
        metastring = ""
        p = np.flip(self.getParameters())
        residuals = np.flip(self.getResiduals())
    
        for i in reversed(range(0, len(p))):
            digits_of_error = 2
        
            par_str, err_str = fh.roundToErrorStrings(p[i], residuals[i], digits_of_error)
        
            metastring += 'a<sub>' + str(round(i)) + '</sub>: ' + par_str + ' &plusmn; ' + err_str
            if i >= 1:
                metastring += "<br>"
            print(metastring)
                
        return metastring
