from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QDrag, QPixmap, QPainter, QColor
from PyQt5.QtCore import (Qt, QByteArray, QDataStream, QPoint, QIODevice, 
                          QMimeData, QSize, QRect)
import dill as pickle

class DragAndDrop:
    mime_type = 'application/x-dnd-watermelon-0.0'
    
    def __init__(self, new=None):
        if new is None: new = True
        self.setMinimumSize(200, 200)
        self.setAcceptDrops(True)
     
    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        try:
            if child:
                if hasattr(child, 'ignore_drag') and child.ignore_drag():
                    return
                if hasattr(child, 'drag_instead'):
                    child = child.drag_instead()
                if pickle.pickles(child):
                    pixmap = child.grab(QRect(QPoint(0,0), QSize(-1, -1)))
                    item_data = QByteArray(pickle.dumps(child))
                    mime_data = QMimeData()
                    mime_data.setData(self.mime_type, item_data)
                    drag = QDrag(self)
                    drag.setMimeData(mime_data)
                    drag.setPixmap(pixmap)
                    drag.setHotSpot(event.pos() - child.pos())
                    self.watermelon_drag(child)
                    #temp_pixmap = pixmap
                    #painter = QPainter()
                    #painter.begin(temp_pixmap)
                    #painter.fillRect(pixmap.rect(), QColor(127, 127, 127, 127))
                    #painter.end()
                    #child.setPixmap(temp_pixmap)
                    if drag.exec_(Qt.CopyAction | Qt.MoveAction, Qt.CopyAction) == Qt.MoveAction:
                        pass
                    else:
                        child.show()             
        except Exception as e:
            if __debug__:
                raise e
            self.watermelon_warning(excep=e, msg='Unable to drag and drop a ' + child.__class__.__name__)
                        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(self.mime_type):
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
            else:
                event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(self.mime_type):
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasFormat(self.mime_type):
            data = event.mimeData().data(self.mime_type).data()
            drop = pickle.loads(data)
            self.watermelon_drop(drop)
            
            if event.source() is self:
                event.setDropAction(Qt.MoveAction)
            else:
                event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()
            



        
        
        