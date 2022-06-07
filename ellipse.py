from rectangle import Rectangle
from PyQt5.QtGui import QPainterPath
from graphics import Graphics

class Ellipse(Rectangle):
    def __init__(self, x=None, y=None, w=None, h=None, pen=None, brush=None,
                 parent=None, init=None):
        if new in [None, True]:
            super().__init__(x, y, w, h, pen, brush, parent)
    
    def shape(self):
        path = QPainterPath()
        w = self.pen().widthF() / 2
        path.addEllipse(self.rect().adjusted(-w, -w, w, w))
        return path
    
    def paint(self, painter, option, widget):
        Graphics.paint(self, painter, option, widget)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawEllipse(self.rect())    