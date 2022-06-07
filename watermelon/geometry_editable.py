from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu
from PyQt5.QtGui import QMouseEvent, QPainter, QCursor
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QEvent, QRect

class GeometryEditable:
    """
    A mixin class, probably for widgets.
    """
    Neutral, Move, Resize = range(3)
    
    TopLeft, Top, TopRight, Right, BottomRight, \
        Bottom, BottomLeft, Left = range(8)
    
    focused_in = pyqtSignal()
    focused_out = pyqtSignal()
    geometry_changed = pyqtSignal(QRect)
    
    def __init__(self, new=None):
        if new is None: new = True
        self._mode = self.Neutral
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setVisible(True)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()
        self._inFocus = True
        self._showingMenu = False
        self._editingGeometry = True
        self._geometryMenu = QMenu()
        self._geometryMenu.addMenu('Done editing')
        
        self.releaseMouse()
        #self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            
        if new:
            GeometryEditable.watermelon_setup(self)
    
    def __setstate__(self, data):
        self.__init__(new=False)
        
    def __getstate__(self):
        return {}
    
    def __deepcopy__(self, memo):
        copy = type(self)()
        memo[id(self)] = copy
        return copy
    
    def popup_geometry_menu(self, point):
        if self._geometryMenu.isEmpty():
            return
        point = self.mapToGlobal(point)
        self._showingMenu = True
        self._geometryMenu.exec_(point)
        self._showingMenu = False
        
    def focusInEvent(self, event):
        self._inFocus = True
        parent = self.parentWidget()
        if parent:
            parent.installEventFilter(self)
            parent.repaint()
        self.focused_in.emit()
        
    def focusOutEvent(self, event):
        if not self._editingGeometry:
            return
        if self._showingMenu:
            return
        self._mode = self.Neutral
        self.focused_out.emit()
        self._inFocus = False
        parent = self.parentWidget()
        if parent:
            parent.removeEventFilter(self)
            parent.repaint()
        self.focused_out.emit()        
        
    def eventFilter(self, obj, event):
        if self._inFocus:
            parent = self.parentWidget()
            if obj is parent and event.type() == QEvent.Paint:
                painter = QPainter(parent)
                p = self.mapTo(parent, QPoint(-3, -3))
                left_top = parent.mapFrom(parent, p)
                left_bot = parent.mapFrom(parent, QPoint(p.x(), p.y() + self.height()))
                right_bot = parent.mapFrom(parent, QPoint(p.x() + self.width(), p.y() + self.height()))
                right_top = parent.mapFrom(parent, QPoint(p.x() + self.width(), p.y()))
                
                painter.fillRect(left_top.x(), left_top.y(), 6, 6, Qt.black)
                painter.fillRect(left_bot.x(), left_bot.y(), 6, 6, Qt.black)
                painter.fillRect(right_bot.x(), right_bot.y(), 6, 6, Qt.black)
                painter.fillRect(right_top.x(), right_top.y(), 6, 6, Qt.black)
        return False
    
    def mousePressEvent(self, event):
        if not self._editingGeometry:
            return
        if not self._inFocus:
            return
        
        if ~event.buttons() & Qt.LeftButton:
            self.set_cursor_shape(event.pos())
            return
        
        geom = self.geometry()
        x = event.globalX()
        y = event.globalY()        
    
        #self.move(x - geom.width()/2, y - geom.height()/2)
        self.move(x, y)
        
        if event.button() == Qt.RightButton:
            self.popup_geometry_menu(event.pos())
            event.accept()
    
    def _gripsBottom(self, evt_pos, grip_size):
        return evt_pos.y() > self.y() + self.height() - grip_size
    
    def _gripsLeft(self, evt_pos, grip_size):
        return evt_pos.x() < self.x() + grip_size
    
    def _gripsRight(self, evt_pos, grip_size):
        return evt_pos.x() > self.x() + self.width() - grip_size
    
    def _gripsTop(self, evt_pos, grip_size):
        return evt_pos.y() < self.y() + grip_size
    
    def set_cursor_shape(self, pos):
        grip = 8
        cursor = None

        if self._gripsBottom(pos, grip) and self._gripsLeft(pos, grip):
            self._resizeMode = self.Left
            cursor = Qt.SizeBDiagCursor
        elif self._gripsBottom(pos, grip) and self._gripsRight(pos, grip):
            self._resizeMode = self.Right
            cursor = Qt.SizeFDiagCursor
        elif self._gripsTop(pos, grip) and self._gripsLeft(pos, grip):
            self._resizeMode = self.TopLeft
            cursor = Qt.SizeFDiagCursor
        elif self._gripsTop(pos, grip) and self._gripsRight(pos, grip):
            self._resizeMode = self.TopRight
            cursor = Qt.SizeBDiagCursor
        elif self._gripsLeft(pos, grip):
            self._resizeMode = self.Left
            cursor = Qt.SizeHorCursor
        elif self._gripsRight(pos, grip):
            self._resizeMode = self.Right
            cursor = Qt.SizeHorCursor
        elif self._gripsTop(pos, grip):
            self._resizeMode = self.Bottom
            cursor = Qt.SizeVerCursor
        elif self._gripsBottom(pos, grip):
            self._resizeMode = self.Top
            cursor = Qt.SizeVerCursor
        else:
            self._resizeMode = None
            self.setCursor(QCursor(Qt.OpenHandCursor))
            self._mode = self.Move
        
        if cursor is not None:   
            self.setCursor(QCursor(cursor))
            self._mode = self.Resize

    def mouseMoveEvent(self, event):
        QWidget.mouseMoveEvent(self, event)
        if not self._editingGeometry:
            return 
        if not self._inFocus:
            return
        geom = self.geometry()
        parent = self.parentWidget()
        pos = self.pos()
        x = event.globalX()
        y = event.globalY()
        delta = event.globalPos() - pos
               
        if ~event.buttons() & Qt.LeftButton:
            p = QPoint(event.x() + self.x(), event.y() + geom.y())
            self.set_cursor_shape(p)
            return
        
        if self._mode == self.Move:
            self.move(event.globalPos())
            if parent:
                parent.repaint()
            self.geometry_changed.emit(self.geometry())
            return
        
        if self._mode == self.Resize and event.buttons() & Qt.LeftButton:
            w = event.globalX() - pos.x() - geom.x()
            h = event.globalY() - pos.y() - geom.y()            
            if self._resizeMode == self.TopLeft:
                self.resize(geom.width() - w, geom.height() - h)
                self.move(delta.x(), delta.y())
            elif self._resizeMode == self.TopRight:             
                self.resize(event.x(), geom.height() - h)
                self.move(self.x(), delta.y())
            elif self._resizeMode == self.BottomLeft:
                delta = event.globalPos() - pos
                self.resize(geom.width() - w, event.y())
                self.move(delta.x(), delta.y())
            elif self._resizeMode == self.Bottom:
                self.resize(self.width(), event.y())
            elif self._resizeMode == self.Left:
                self.resize(geom.width() - w, self.height())
                self.move(delta.x(), self.y())
            elif self._resizeMode == self.Top:
                self.resize(self.width(), geom.height() - h)
                self.move(self.x(), delta.y())
            elif self._resizeMode == self.Right:
                self.resize(event.x(), self.height())
            elif self._resizeMode == self.BottomRight:
                self.resize(event.x(), event.y())
            
            parent.repaint()
            self.geometry_changed.emit(self.geometry())
        
    def watermelon_setup(self):
        pass