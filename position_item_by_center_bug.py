from PyQt5.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView, 
                             QGraphicsObject, QGraphicsSceneEvent)
from PyQt5.QtGui import QBrush, QPen, QColor, QPainterPathStroker
from PyQt5.QtCore import QPointF, Qt, QRectF, pyqtSignal, QEvent
import sys

from PyQt5.QtCore import QObject, pyqtBoundSignal, QLineF
import inspect


class PickleableSignal(QObject):
    """
    Wrapper class for a single signal, returned by __getattribute__ method of SignalHelper.
    Supports, lambda, delegates, disconnection by string or by another reference / copy of the
    lambda or delegate.  Supports pickling of everything using the dill library.
    For pickling to work, sender must be pickleable on its own in the usual way.
    """
    
    Handle, Slot = range(2)
    
    def __init__(self, sender=None, signal=None, init=None):
        assert(isinstance(sender, SignalPickler))    # Requires inheritance to work
        super().__init__()
        if new in [None, True]:
            self._sender = sender
            self._signal = signal
            self._slotInfo = {}       # Keyed by string representing lambda or delegate name
    
    def __setstate__(self, data):
        """
        Standard pickle method design.  Includes slot info and connection state.
        """
        self.__init__(init=False)
        self._sender = data['sender']
        self._signal = data['signal']
        self._slotInfo = {}
        # PyQt5 is not pickle aware so we must reconnect the signals after unpickling and/or copying.
        for slot_id, (handle, slot) in data['slot info'].items():
            self.connect(slot)
            
    def __getstate__(self):
        """
        Standard pickle method design.  Includes slot info.
        """
        return {
            'sender' : self._sender,
            'signal' : self._signal,
            'slot info' : self._slotInfo,
        }
    
    def __deepcopy__(self, memo):
        """
        Standard deepcopy method design.  Includes slot info and connection state.
        """
        from copy import deepcopy
        copy = type(self)(new=False)
        memo[id(self)] = copy
        copy._sender = deepcopy(self._sender, memo)
        copy._signal = self._signal    # OK, since we treat _signal as an immutable string.
        copy._slotInfo = {}
        # Of course we need to create this copies own slot connections.
        for slot_id, (handle, slot) in self._slotInfo.items():
            copy.connect(slot)  
        return copy
    
    def connect(self, slot):
        """
        Allows a given slot signature to be connected once and only once.
        Returns the slot id to use for disconnecting; alternatively pass in the exact
        same lambda or delegate and that should do the trick.  Returns None if 
        that same lambda or delegate has already been added.
        """
        if not self._sender.isSignalRegistered(self):
            self._sender.registerSignal(self)
        slot_id = self.slotID(slot)
        if slot_id not in self._slotInfo:
            self._slotInfo[slot_id] = (self._sender.pyqtSignal(self._signal).connect(slot), slot)
            return slot_id
        return None
    
    def emit(self, *args):
        self._sender.pyqtSignal(self._signal).emit(*args)
        
    def disconnect(self, slot):
        """
        Pass in a string for the delegate / lambda or the delegate lambda itself and we'll
        generate the canonical id ourself.
        """
        if not isinstance(slot, str):
            slot = self.slotID(slot)
        handle = self._slotInfo[slot][self.Handle]
        self._sender.pyqtSignal(self._signal).disconnect(handle)
        del self._slotInfo[slot]   # Don't forget to delete its entry
    
    def signalName(self):
        return self._signal
    
    def senderObj(self):
        return self._sender
    
    def slot(self, slot_id):
        return self._slotInfo[slot_id][self.Slot]
            
    def slotID(self, slot):
        """
        This is how we generated an identifier string given a slot.
        """
        return inspect.getsource(slot).strip()
    
    def __contains__(self, slot):
        if not isinstance(slot, str):
            slot = self.slotID(slot)
        return slot in self._slotInfo
    
    
class SignalPickler:
    """
    A mixin class that helps connect / disconnect slots to member signals and pickle them (using dill).
    It should go "GraphicsBase(QGraphicsObject, SignalPickler)" as far as base class ordering goes.
    I've never found the other way around to work without compiler error or unexplicable runtime crash.
    The same goes for other classes.  Qt's raw class first, then your mixin or QObject-derived class.
    """    
    
    def __init__(self):
        self._signals = {}
        
    def __setstate__(self, data):
        """
        Subclasses must call this class's __setstate__ in order to pickle signals.
        """
        self.__init__()
        self._signals = data['signals']
        
    def __getstate__(self):
        """
        Subclasses must also call this class's __getstate__ in order to pickle signals.
        """
        return {
            'signals' : self._signals
        }
    
    def __deepcopy__(self, memo):
        """
        Want your objects / widgets copy & pasteable?  Then also call this from a subclass's __deepcopy__ method.
        """
        copy = type(self)()
        memo[id(self)] = copy
        copy._signals = deepcopy(self._signals, memo)
        return copy
    
    def __getattribute__(self, attr):
        """
        Internally, this is what SignalPickler does.  Every time you ask for a signal from the sender object,
        for example: `sender.positionChanged.connect(foo)`, instead of returning sender.positionChanged it will
        return a SignalPickler object wrapping it.
        """
        res = super().__getattribute__(attr)
        if isinstance(res, pyqtBoundSignal):
            return PickleableSignal(sender=self, signal=attr)
        return res    
    
    def registerSignal(self, signal):
        """
        For internal use only, usually.
        """
        self._signals[signal.signal_name()] = signal
        
    def isSignalRegistered(self, signal):
        """
        For internal use only, usually.
        """
        return signal.signal_name() in self._signals
    
    def pyqtSignal(self, name):
        return super().__getattribute__(name)
    
    
class Graphics(QGraphicsObject, SignalPickler):
    anythingHasChanged = pyqtSignal(str)
    changeToAnything = pyqtSignal(str)    
    positionChange = pyqtSignal(QPointF)
    positionHasChanged = pyqtSignal(QPointF)
    parentChange = pyqtSignal(QObject)
    parentHasChanged = pyqtSignal(QObject)
    childAdded = pyqtSignal(QObject)
    childRemoved = pyqtSignal(QObject)
    brushChange = pyqtSignal(QBrush)
    brushHasChanged = pyqtSignal(QBrush)
    penChange = pyqtSignal(QPen)
    penHasChanged = pyqtSignal(QPen)
        
    def __init__(self, pen=None, brush=None, children=None, parent=None, init=None):
        if new in [None, True]:
            super().__init__()
            super().__init__()
            if pen is None:
                pen = QPen(QColor(255, 0, 0), 1.0)
            if brush is None:
                brush = QBrush(QColor(255, 0, 0))
            self._brush = brush
            self._pen = pen     
            self.setParentItem(parent)
            self.setFlags(self.ItemIsFocusable | self.ItemIsMovable |
                          self.ItemIsSelectable | self.ItemSendsGeometryChanges |
                          self.ItemSendsScenePositionChanges)
        self._surpressSigs = False
        self._prevBrush = self._brush
        self._prevPen = self._pen
        self._prevParent = parent
        self._prevPos = self.pos()   
        if children is None:
            children = []
        for child in children:
            if child: child.setParentItem(self)

    def boundingRect(self):
        return self.childrenBoundingRect()

    def itemChange(self, change, value):
        if change == self.ItemParentChange:
            self._prevParent = self.parentItem()
            self.emitChange(self.parentChange, 'parentItem', value)
        elif change == self.ItemParentHasChanged:
            self.emitHasChanged(self.parentHasChanged, 'parentItem', value)
        elif change == self.ItemPositionChange:
            self._prevPos = value
            self.emitChange(self.positionChange, 'pos', value)
        elif change == self.ItemPositionHasChanged:
            self.emitHasChanged(self.positionHasChanged, 'pos', value)        
        elif change == self.ItemChildAddedChange:
            self.emitHasChanged(self.childAdded, 'childItems', value)
        elif change == self.ItemChildRemovedChange:
            self.emitHasChanged(self.childRemoved, 'childItems', value)
        elif change == self.ItemSceneChange:
            if self.scene():
                self.removedFromSceneEvent()
        elif change == self.ItemSceneHasChanged:
            if self.scene():
                self.addedToSceneEvent()
        return super().itemChange(change, value)
    
    def setBrush(self, QBrush):
        self.emitChange(self.brushChange, 'QBrush', QBrush)
        self._prevBrush = self._brush
        self._brush = QBrush
        self.update()
        self.emitHasChanged(self.brushHasChanged, 'QBrush', QBrush)
        
    def QBrush(self):
        return self._brush
    
    def setPen(self, pen):
        self.emitChange(self.penChange, 'pen', pen)
        self._prevPen = self._pen
        self._pen = pen
        self.update()
        self.emitHasChanged(self.penHasChanged, 'pen', pen)
        
    def pen(self):
        return self._pen
    
    def setSignalsSurpressed(self, en):
        if self._surpressSigs != en:
            self._surpressSigs = en
            for child in self.childItems():
                child.setSignalsSurpressed(en)
            
    def signalsSurpressed(self):
        return self._surpressSigs
    
    def emitChange(self, sig, member, *args):
        if not self._surpressSigs:
            sig.emit(*args)
            self.changeToAnything.emit(member)
        
    def emitHasChanged(self, sig, member, *args):
        if not self._surpressSigs:
            sig.emit(*args)
            self.anythingHasChanged.emit(member)        
            
    def paint(self, painter, option, widget):
        from geom_tools import paintSelectionShape
        if self.isSelected():
            paintSelectionShape(painter, self)
        painter.setRenderHints(painter.HighQualityAntialiasing | painter.Antialiasing)
        
    def childPosHasChangedEvent(self, child):
        pass
    
    def childPosChangeEvent(self, child):
        pass

    def addedToSceneEvent(self):
        """
        Do here init things that can only be done once added to the scene.
        """        
        parent = self.parentItem()
        if isinstance(parent, Graphics):
            self.installEventFilter(parent)
        for child in self.childItems():
            child.addedToSceneEvent()
                
    def removedFromSceneEvent(self):
        """
        Undo things done in the above method.
        """
        parent = self.parentItem()
        if isinstance(parent, Graphics):
            self.removeEventFilter(parent)
        for child in self.childItems():
            child.removedFromSceneEvent()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setPos(self.mapToParent(event.pos()))
        super().mousePressEvent(event)


from collections import OrderedDict

class GraphicsSet(Graphics):
    """
    Stores graphics items naturally by id() but they're also part of the same
    movable group.  They are also kept ordered (order of element addition).
    """
    
    elementPosHasChanged = pyqtSignal(Graphics)
    elementPosChange = pyqtSignal(Graphics)
    
    def __init__(self, count=None, type=None, parent=None, init=None, *args, **kwargs):
        if new in [None, True]:
            super().__init__(parent=parent)
            self._set = OrderedDict()
            if count is not None and type is not None:
                for k in range(0, count):
                    obj = type(*args, **kwargs)
                    self.add(obj)
        
    def boundingRect(self):
        return self.childrenBoundingRect()    
    
    def add(self, obj):
        self._set[id(obj)] = obj
        obj.setParentItem(self)
        
    def remove(self, obj):
        del self._set[id(obj)]
        obj.setParentItem(None)
        
    def elements(self):
        return self._set.values()
    
    def odict(self):
        return self._set
    
    def __iter__(self):
        return iter(self._set)
    
    def __len__(self):
        return len(self._set)    
            
    #def paint(self, painter, option, widget):
        #from PyQt5.QtGui import QColor, QPen
        #painter.setPen(QPen(QColor(0, 0, 255), 2.0))
        #painter.drawPoint(self.pos())
        #super().paint(painter, option, widget)
    
    def childPosChangeEvent(self, child):
        self.elementPosChange.emit(child)    
    
    def childPosHasChangedEvent(self, child):
        self.elementPosHasChanged.emit(child) 
        
        
class Rectangle(Graphics):
    rectangleChange = pyqtSignal(Graphics, QRectF)
    rectangleHasChanged = pyqtSignal(Graphics, QRectF)
    
    def __init__(self, x=None, y=None, w=None, h=None, pen=None, QBrush=None, 
                 children=None, parent=None, init=None):
        if new in [None, True]:
            super().__init__(pen, QBrush, children, parent)
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
        painter.setBrush(self.QBrush())
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
                    
                    
from PyQt5.QtGui import QPainterPath

class Ellipse(Rectangle):
    def __init__(self, x=None, y=None, w=None, h=None, pen=None, QBrush=None,
                 children=None, parent=None, init=None):
        if new in [None, True]:
            super().__init__(x, y, w, h, pen, QBrush)
    
    def shape(self):
        path = QPainterPath()
        w = self.pen().widthF() / 2
        path.addEllipse(self.rect().adjusted(-w, -w, w, w))
        return path
    
    def paint(self, painter, option, widget):
        Graphics.paint(self, painter, option, widget)
        painter.setPen(self.pen())
        painter.setBrush(self.QBrush())
        painter.drawEllipse(self.rect())    
        
        
class Point(Ellipse):
    def __init__(self, x=None, y=None, diam=None, pen=None, brush=None,
                 children=None, parent=None, init=None):
        if new in [None, True]:
            return super().__init__(x, y, diam, diam, pen, brush, children, parent)
        

class Line(Graphics):
    def __init__(self, points=None, diam=None, pen=None, 
                 point_pen=None, point_brush=None, parent=None, init=None):
        if points is None:
            points = GraphicsSet(count=2, type=Point, diam=diam, pen=point_pen, brush=point_brush)
        if new in [None, True]:
            super().__init__(pen, children=[points], parent=parent)
            self.controlPoints = points
        self.controlPoints.elementPosHasChanged.connect(self.controlPointPosChangedEvent)
        self.setFiltersChildEvents(True)
        
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
        painter.setBrush(self.QBrush())
        painter.drawLine(self.line())

    def controlPointPosChangedEvent(self, point):
        #"""
        #Ensures that self.line().center() == self.pos() always.
        #"""
        #child = self.controlPoints
        ##self.controlPoints.setPos(self.controlPoints.pos() -
        self.setSignalsSurpressed(True)
        #parent = self.parentItem()
        transform = QTransform()
        transform.translate(-self.boundingRect().center().x(), -self.boundingRect().center().y())
        self.setTransform(transform)
        self.setSignalsSurpressed(False)      
        
        ## When a control point position has changed, we should repaint the line:
        self.updateScene()
        
    def pointPos(self):
        return [self.controlPoints.mapToParent(elem.pos()) 
                for elem in self.controlPoints.elements()]
    
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
        
    #def sceneEventFilter(self, watched, event):
        #if watched is self.controlPoints:
            #if event.type() == QEvent.GraphicsSceneMouseMove:
                #if self.scene():
                    #item = self.scene().itemAt(event.scenePos(), QTransform())
                    #if item and item in self.controlPoints:
                        #return True
                #self.setSignalsSurpressed(True)
                #delta = event.pos()
                #delta = self.mapToParent(delta)
                #self.setPos(delta)
                #self.controlPoints.setPos(-self.boundingRect().center())
                #self.setSignalsSurpressed(False)
                #return True
        #return False    
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.setSignalsSurpressed(True)
        #self.setPos(event.pos())
        #self.controlPoints.setPos(-self.boundingRect().center())
        rect = self.controlPoints.boundingRect()
        trans = QTransform()
        trans.translate(-self.boundingRect().center().x(), -self.boundingRect().center().y())
        self.controlPoints.setTransform(trans)
        self.setSignalsSurpressed(False)

        
if __name__ == '__main__':
    app = QApplication([])
    
    window = QMainWindow()
    window.view = QGraphicsView()
    window.scene = QGraphicsScene()
    window.view.setScene(window.scene)
    window.show()
    window.setCentralWidget(window.view)
    
    item = Line()
    window.scene.addItem(item)
    
    sys.exit(app.exec_())
