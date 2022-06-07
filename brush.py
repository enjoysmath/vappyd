from PyQt5.QtGui import QBrush

#TODO include gradient options

class Brush(QBrush):
    def __init__(self, color=None):
        super().__init__(color)
    
    def __setstate__(self, data):
        self.__init__(data['color'])
        
    def __getstate__(self):
        return {
            'color' : self.color(),
        }
        
    def __deepcopy__(self, memo):
        copy = type(self)(self.color())
        memo[id(self)] = self
        return copy