from ellipse import Ellipse

class Point(Ellipse):
    def __init__(self, x=None, y=None, diam=None, pen=None, brush=None, parent=None, init=None):
        if new in [None, True]:
            return super().__init__(x, y, diam, diam, pen, brush, parent)
    
    def addControlPoint(self, point):
        raise NotImplementedError
    
    def removeControlPoint(self, point):
        raise NotImplementedError