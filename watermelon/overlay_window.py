import watermelon.window as window
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QPointF, QLineF

class OverlayWindow(window.Window):
    def __init__(self, new=None):
        if new is None: new = True
        super().__init__(new)
        
        self.setAttribute(Qt.WA_NoSystemBackground)
        #self.set_transparent_for_mouse_events(True)
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet('background-color: rgba(255,0,0,255);')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
                   

