from PyQt5.QtCore import QPointF, pyqtSignal
from line import Line
from point import Point

class BezierLine(Line):
    isBezierToggle = pyqtSignal(Line, bool)
    isBezierToggled = pyqtSignal(Line, bool)
    
    def __init__(self, points=None, diam=None, pen=None, 
                 point_pen=None, point_brush=None, children=None, parent=None, init=None):
        if new in [None, True]:
            if points is None:
                points = GraphicsSet(count=4, type=Point, diam=diam, pen=point_pen, brush=point_brush, parent=self)
            else:
                assert(len(points) == 4)
            super().__init__(points=points, pen=pen, parent=parent)
            self._bezier = False
                
    def __setstate__(self, data):
        """
        Super calls to __setstate__ will call parent class's __init__ method, so don't
        call them in this class's __init__.
        """        
        super().__setstate__(data)
        self.controlPoints = data['control points']
        self._bezier = data['is bezier']
        self.__init__()
        
    def __getstate__(self):
        data = super().__getstate__()
        data['control points'] = self.controlPoints
        data['is bezier'] = self._bezier
        return data
    
    def __deepcopy__(self, memo):
        copy = deepcopy(super(), memo)
        copy.controlPoints = deepcopy(self.controlPoints, memo)
        copy._bezier = self._bezier
        return copy        
        
    def pointPos(self):
        return [elem.pos() for elem in self.controlPoints.elements()]
    
    def setIsBezier(self, en):
        if en != self._bezier:
            self.emitChange(self.isBezierToggle, 'isBezier', en)
            self._bezier = True
            self.update()
            self.emitHasChanged(self.isBezierToggled, 'isBezier', en)
    
    def isBezier(self):
        return self._bezier


            
    