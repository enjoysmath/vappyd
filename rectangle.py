from graphics import Graphics
from PyQt5.QtCore import QPointF, QRectF, pyqtSignal

class Rectangle(Graphics):
    rectangleChange = pyqtSignal(Graphics, QRectF)
    rectangleHasChanged = pyqtSignal(Graphics, QRectF)
    
    def __init__(self, x=None, y=None, w=None, h=None, pen=None, brush=None, 
                 parent=None, init=None):
        if new in [None, True]:
            super().__init__(pen, brush, parent)
            if x is None:
                x = 0
            if y is None:
                y = 0
            if w is None:
                w = 10
            if h is None:
                h = 5
            self.setPos(QPointF(x, y))
            rect = QRectF(x, y, w, h)
            self._rect = rect.translated(-w/2, -h/2)
                
    def __setstate__(self, data):
        super().__setstate__(data)
        self.setRect(data['rect'])
        self.__init__(init=False)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['rect'] = self.rect()
        return data
    
    def __deepcopy__(self, memo):
        copy = super().__deepcopy__(memo)
        copy.setRect(self.rect())
        return copy
    
    def boundingRect(self):
        w = self.pen().widthF() / 2
        return self.rect().adjusted(-w, -w, w, w)
    
    def shape(self):
        path = QPainterPath()
        w = self.pen().widthF() / 2
        path.addRect(self.rect().adjusted(-w, -w, w, w))
        return path
    
    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())
        
    def rect(self):
        return self._rect
    
    def setRect(self, rect):
        rect = rect.translated(-rect.width()/2, -rect.height()/2)
        if self._rect != rect:
            self.emitChange(self.rectangleChange, 'rect', rect)
            self._rect = rect
            self.update()
            self.emitHasChanged(self.rectangleHasChanged, 'rect', rect)