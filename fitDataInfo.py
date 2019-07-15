class fitDataInfo():
    SUCCESS = "Fit succeeded."
    
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
        pass

    def get_meta_string(self):
        pass