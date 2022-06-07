from PyQt5.QtWidgets import QMainWindow, QGraphicsView
from PyQt5.QtGui import QIcon
from scene import Scene
from bezier_line import BezierLine
from line import Line
from bezier_line import BezierLine
from view import View

class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyQtcumber Demo App - v0.0')
        self.setWindowIcon(QIcon('images/app_icon.ico'))
        self.scene = Scene()
        self.view = View()
        self.view.setScene(self.scene)
                
        curve = Line()
        #curve.setIsBezier(False)
        
        self.scene.addItem(curve)
        self.setCentralWidget(self.view)
    