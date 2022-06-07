from point import Point
from PyQt5.QtGui import (QPainterPath, QPainterPathStroker, QPen, QColor,
                         QTransform)
from PyQt5.QtCore import QLineF, Qt, QPointF, QEvent
from graphics import Graphics
from control_point import ControlPoint

class Line(Graphics):
    def __init__(self, points=None, pen=None, parent=None, init=None):
        #if points is None:
            #points = GraphicsSet(count=2, type=Point, diam=diam, pen=point_pen, brush=point_brush)
        if new in [None, True]:
            super().__init__(pen=pen, parent=parent)
            self.setFiltersChildEvents(True)
            if points is None:
                points = [ControlPoint(0, 0)]
            for point in points:
                self.addControlPoint(point)
        
    def __setstate__(self, data):
        super().__setstate__(data)
        self._points = data['points']
        self.__init__()
        
    def __getstate__(self):
        return {
            'parent' : self.parentItem(),
            'pos' : self.pos(),
            'control points' : self.controlPoints,
        }
    
    def __deepcopy__(self, memo):
        copy = deepcopy(super(), memo)
        copy.controlPoints = deepcopy(self.controlPoints, memo)
        return copy
    
    def line(self):
        points = self.pointPos()
        return QLineF(points[0], points[-1])        

    def shape(self):
        path = QPainterPath()
        line = self.line()
        path.moveTo(line.p1())
        path.lineTo(line.p2())
        stroker = QPainterPathStroker(QPen(Qt.black, self.pen().widthF())) 
        return stroker.createStroke(path)     
    
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if __debug__:
            painter.setPen(self.pen())
            painter.drawRect(self.boundingRect())
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawLine(self.line())
        painter.setPen(QPen(QColor(0, 0, 255), 2.0))
        painter.drawPoint(self.boundingRect().center())
        painter.setPen(QPen(QColor(0, 255, 0), 4.0))
        painter.drawPoint(self.mapFromParent(self.pos()))
        
    def controlPointPosChangeEvent(self, point):
        pass

    def controlPointPosChangedEvent(self, point):
        #"""
        #Ensures that self.line().center() == self.pos() always.
        #"""
        #child = self.controlPoints
        self.setSignalsSurpressed(True)
        c = self.boundingRect().center()
        pos = self.mapToParent(c)
        delta = self.mapFromParent(pos - self.pos())
        self.setPos(self.pos() + delta)
        self.controlPoints.setPos(QPointF())
        delta = self.controlPoints.mapFromParent(delta)
        for point in self.controlPoints.elements():
            point.setPos(point.pos() - delta)        
        self.setSignalsSurpressed(False)      
        
        ### When a control point position has changed, we should repaint the line:
        self.updateScene()
    
    def p1(self):
        return self.pointPos()[0]
    
    def p2(self):
        return self.pointPos()[-1]
    
    def setP1(self, p):
        p = self.controlPoints.mapFromParent(p)
        if self.p1() != p:
            self.controlPoints.elements()[0].setPos(p)
    
    def setP2(self, p):
        p = self.controlPoints.mapFromParent(p)
        if self.p2() != p:
            self.controlPoints.elements()[-1].setPos(p)
        
        

    