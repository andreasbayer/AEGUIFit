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
        self._residuals = []

    #def is_initialized(self):
    #    return (self._FitTo == sys.float_info.max)
    
    # get-set-block
    def getDegree(self):
        return self._n
    
    def setDegree(self, n):
        self._n = n

    def getFitTo(self):
        return self._FitTo

    def setFitTo(self, value):
        self._FitTo = value

    def getFitFrom(self):
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

            full_fitdata = np.array([data[:, 0], np.polyval(self._p, data[:, 0])]).transpose()
            fitdata = list()

            appendval = 0

            self.progressUpdate(0.5, '')

            for point in full_fitdata:
                if self.getFitFrom() <= point[0] <= self.getFitTo():
                    fitdata.append(point)
                    appendval = point[1]
                else:
                    fitdata.append([point[0], appendval])

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
        #fitDataInfo.shift_fit(increment)
        if self.isFitted():
            for set in self._fitData:
                set[0] += increment

            self._FitTo += increment
            self._FitFrom += increment

        for set in self._data:
            set[0] += increment
            