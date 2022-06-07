from collections import OrderedDict
from PyQt5.QtCore import QPointF
from copy import deepcopy

use_debug_feature = True

class ControlPoints:
    """
    This is a mixin class for graphics scene items.  The best editors have everything
    resizeable / transformable, thus Graphics inherits this mixin.
    Stores points naturally by id(), parents the points.  
    A control point is a little handle that if moved, causes some associated geometry to reconfigure.
    For instance a simple Bezier curve has 4 control points, while a line has 2 control points.
    It's up in the air for a rectangle; you could have a control point at each corner but also 
    in the center (with an arrow indicating "rotate me") or on its sides say.
    You can only add ControlPoint subclassed items as control points.  So if you need a custom-shaped
    handle, just subclass the most-relevant ControlPoint subclass that's in the lib.
    """
    
    def __init__(self, init=None):
        if new in [None, True]:
            self._points = OrderedDict()

    def __setstate__(self, data):
        self.__init__(init=False)
        for key, val in data['points']:
            self._points[id(val)] = val         # In case pickling doesn't respect id's         
                
    def __getstate__(self):
        return {
            'points' : self.elements(),
        }
    
    def __deepcopy__(self, memo, copy=None):
        if copy is None:
            copy = type(self)()
            memo[id(self)] = copy
        copy._points = deepcopy(self._points, memo)
        for p in copy.elements():
            copy._points[id(p)] = p
        return copy
        
    def boundingRect(self):
        return self.childrenBoundingRect()    
    
    def addControlPoint(self, point):
        self._points[id(point)] = point
        point.setParentItem(self)
        
    def removeControlPoint(self, point):
        del self._points[id(point)]
        point.setParentItem(None)
        
    def controlPoints(self):
        return self._points.values()
    
    def controlPointOdict(self):
        return self._points
    
    def __len__(self):
        return len(self._points)    
            
    def paint(self, painter, option, widget):
        painter.setPen(QPen(QColor(0, 0, 255), 2.0))
        painter.drawPoint(self.pos())
        
    def pointPos(self):
        return [point.pos() for point in self.controlPoints()]    
    