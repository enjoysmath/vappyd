from PyQt5.QtWidgets import QGraphicsObject
from PyQt5.QtCore import pyqtSignal, QPointF, QObject, Qt, pyqtBoundSignal
from PyQt5.QtGui import QColor
from pen import Pen
from brush import Brush
from signal_pickler import SignalPickler
import control_points

class Graphics(QGraphicsObject, control_points.ControlPoints, SignalPickler):
    anythingHasChanged = pyqtSignal(str)
    anythingChange = pyqtSignal(str)    
    positionChange = pyqtSignal(QPointF)
    positionHasChanged = pyqtSignal(QPointF)
    parentChange = pyqtSignal(QObject)
    parentHasChanged = pyqtSignal(QObject)
    childAdded = pyqtSignal(QObject)
    childRemoved = pyqtSignal(QObject)
    brushChange = pyqtSignal(Brush)
    brushHasChanged = pyqtSignal(Brush)
    penChange = pyqtSignal(Pen)
    penHasChanged = pyqtSignal(Pen)
        
    def __init__(self, pen=None, brush=None, parent=None, init=None):
        if new in [None, True]:
            super().__init__(parent)
            super().__init__()
            super().__init__()
            if pen is None:
                pen = Pen(QColor(255, 0, 0), 1.0)
            if brush is None:
                brush = Brush(QColor(255, 0, 0))
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
            
    def __setstate__(self, data):
        super().__setstate__()
        self.setParentItem(data['parent'])
        self.setPos(data['pos'])
        self.setBrush(data['brush'])
        self.setPen(data['pen'])
        self.__init__(children=data['children'], init=False)
        
    def __getstate__(self):
        return {
            'parent' : self.parentItem(),
            'pos' : self.pos(),
            'brush' : self.brush(),
            'pen' : self.pen(),
            'children' : self.childItems(),
        }
    
    def __deepcopy__(self, memo):
        from copy import deepcopy
        copy = type(self)(children=deepcopy(self.childItems(), memo))
        memo[id(self)] = copy
        copy.setParentItem(deepcopy(self.parentItem(), memo))
        copy.setPos(self.pos())
        copy.setBrush(deepcopy(self.brush(), memo))
        copy.setPen(deepcopy(self.pen(), memo))
        return copy
        
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
    
    def setBrush(self, brush):
        self.emitChange(self.brushChange, 'brush', brush)
        self._prevBrush = self._brush
        self._brush = brush
        self.update()
        self.emitHasChanged(self.brushHasChanged, 'brush', brush)
        
    def brush(self):
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
            self.anythingChange.emit(member)
        
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
    
    def setParentItem(self, parent):
        par = self.parentItem()
        if parent is not par:
            if isinstance(par, Graphics):
                par.disconnectChild(self)
            if isinstance(parent, Graphics):
                parent.connectChild(self)
            super().setParentItem(parent)
        
    def connectChild(self, child):
        child.positionHasChanged.connect(
            lambda p: self.childPosHasChangedEvent(child)      
            # TODO: make note in documation of purpose of newline here
            # Putting this all on one line has the effect of including everything on the line in the slot_id.
            # Which might be helpful if you need to add in some contextually identifying information.
        )
        child.positionChange.connect(
            lambda p: self.childPosChangeEvent(child)
        )
        
    def disconnectChild(self, child):
        child.positionHasChanged.disconnect(
            lambda p: self.childPosHasChangedEvent(child)
        )
        child.positionChange.disconnect(
            lambda p: self.childPosChangeEvent(child)
        )

    def addedToSceneEvent(self):
        """
        Do here init things that can only be done once added to the scene.
        """        
        parent = self.parentItem()
        if isinstance(parent, Graphics):
            self.installEventFilter(parent)
        self.setTransformOriginPoint(self.boundingRect().center())
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
            
    def updateScene(self):
        if self.scene():
            self.scene().update()
        else:
            self.update()
            
    def mousePressEvent(self, event):
        self.setSignalsSurpressed(True)
        self.setPos(event.pos() - self.boundingRect().center())
        self.setSignalsSurpressed(False)        