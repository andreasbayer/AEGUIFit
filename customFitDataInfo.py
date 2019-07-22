import sys
from fitDataInfo import fitDataInfo
import numpy as np


class customFitDataInfo(fitDataInfo):

    def __init__(self, index):
        fitDataInfo.__init__(self, index)

        self._function_str = ''
        self._function = None
        self._domainTo = sys.float_info.max
        self._domainFrom = 0

    # def is_initialized(self):
    #    return (self._FitTo == sys.float_info.max)

    # get-set-block

    def getDomainTo(self):
        return self._domainTo

    def setDomainTo(self, value):
        self._domainTo = value

    def getDomainFrom(self):
        return self._domainFrom

    def setDomainFrom(self, value):
        self._domainFrom = value

    def setFunctionStr(self, value):
        self._function_str = value

    def getFunctionStr(self):
        return self._function_str

    def getFitFunc(self):
        return self.getFunctionStr()

    def evaluateFunction(self):
        try:
            self._function = eval('lambda x: ' + self._function_str)
            return 1
        except:
            return 0

    def getFunction(self):
        return self._function

    def callFunction(self, data, domain):
        x = data[:, 0]
        space = list()

        if self._function is not None:
            try:
                y = self._function(x)

                for i in range(0, len(x)):

                    if domain is None or domain[0] <= x[i] <= domain[1]:
                        space.append([x[i], y[i]])
                    else:
                        space.append([x[i], 0])
            except:
                print("calling function failed.")

        else:
            print("custom function not set.")

        return np.array(space)


    def getName(self):
        return "Function #" + str(self.get_fit_index() + 1)

    def fitToFunction(self):
        data = self.get_data()

        self.progressUpdate(0, '')

        try:
            self.evaluateFunction()

            self._setFitData(self.callFunction(data, (self.getDomainFrom(), self.getDomainTo())))

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
        # fitDataInfo.shift_fit(increment)
        if self.isFitted():
            for set in self._fitData:
                set[0] += increment

            self._domainFrom += increment
            self._domainTo += increment

        for set in self._data:
            set[0] += increment
