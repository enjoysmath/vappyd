from PyQt5.QtWidgets import QGraphicsView, QWidget
from flow_layout import FlowLayout
from debug_widget import DebugWidget

use_debug_view = True

class View(QGraphicsView):
    def __new__(cls):
        if __debug__ and use_debug_view:
            return super().__new__(DebugView)
        return super().__new__(cls)
    
    
class DebugView(View):
    def __init__(self):
        super().__init__()
        lyt = FlowLayout()
        self.setLayout(lyt)
        self.debugWidget = DebugWidget(view=self)
        lyt.addWidget(self.debugWidget)
        
    def setScene(self, scene):
        scene.selectionChanged.connect(self.debugWidget.sceneSelectionChanged)
        super().setScene(scene)