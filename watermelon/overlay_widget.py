import watermelon.widget
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPointF, QLineF

class OverlayWidget(watermelon.widget.Widget):
    def __init__(self, parent=None, new=None):
        if new is None: new = True
        super().__init__(parent, new)
        
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('background-color: rgba(0,255,0,255);')
        #self.set_transparent_for_mouse_events(True)
        
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 2.0))
        painter.drawLine(QLineF(0, 0, 100, 100))

        