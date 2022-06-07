import watermelon.overlay_window as window
from PyQt5.QtCore import Qt, QLineF
from PyQt5.QtGui import QPainter, QPen
import watermelon.overlay_widget as widget

class SignalOverlayWindow(window.OverlayWindow):
    def __init__(self, new=None):
        if new is None: new = True
        super().__init__(new)
        self.setWindowTitle('Signals')
        #self.showMaximized()
        self.overlay_widget = widget.OverlayWidget(parent=self)
        self.setCentralWidget(self.overlay_widget)
        
