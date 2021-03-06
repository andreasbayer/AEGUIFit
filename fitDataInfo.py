import numpy as np

class fitDataInfo():
    SUCCESS = "Fit succeeded."
    FAILURE = "Fit failed."
    
    def __init__(self, index):
        self._fitData = None
        self._data = None
        self._stdDev = 1
        self._stdErr = None
        self._fitFunction = None
        self._msg = ""
        self._passProgressUpdate = None
        self._fitFunction = None
        self._fit_index = index
        self._isDisabled = False
        self._weighted = True
        self._shift = 0

    def is_initialized(self):
        return self._data is not None

    def progressUpdate(self, relation, info):
        pass
        
    def getName(self):
        pass

    def isDisabled(self):
        return self._isDisabled
    
    def setDisabled(self, disabled):
        self._isDisabled = disabled
        
    def isFitted(self):
        return (self._getFitData() is not None)

    def is_weighted(self):
        return self._weighted

    def set_weighted(self, value):
        self._weighted = value
        
    def get_fit_index(self):
        return self._fit_index
    
    def set_fit_index(self, p_index):
        self._fit_index = p_index
        
    def setProgressUpdateFunction(self, updateFunction):
        self._passProgressUpdate = updateFunction
        
    def getFitFunc(self):
        pass
    
    def get_msg(self):
        return self._msg
    
    def setData(self, data):
        self._data = data
        
    def setStdErr(self, std_err):
        self._stdErr = std_err
    
    def emitProgressUpdate(self, relation):
        self.progressUpdate.emit(relation)
    
    def reset(self):
        self._fitData = None
        self._data = None
        self._stdErr = None
        
    def _getFitData(self):
        return self._fitData
    
    def _setFitData(self, newFitData):
        self._fitData = newFitData
    
    def getStdDeviation(self):
        return self._stdDev
    
    def getFitData(self):
        return self._fitData

    def get_data(self):
        return self._data
    
    def get_std_err(self):
        return self._stdErr
    
    def fitToFunction(self):
        pass
    
    def shift_fit(self, increment):
        self._shift += increment
        
        if self.isFitted():
            for set in self._fitData:
                set[0] += increment
        
        for set in self._data:
            set[0] += increment

    def get_meta_string(self):
        pass
    
    def get_shift(self):
        return self._shift