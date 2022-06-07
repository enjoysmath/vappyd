import watermelon.watermelon as watermelon
import watermelon.geometry_editable as geometry
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush

class Widget(QWidget, watermelon.Watermelon): #, geometry.GeometryEditable):
    def __init__(self, parent=None, new=None):
        if new is None: new = True
        QWidget.__init__(self, parent)
        watermelon.Watermelon.__init__(self, new)
        #geometry.GeometryEditable.__init__(self, new)
        if new:
            self._toolrep = False
            
    def __setstate__(self, data):
        super().__setstate__(data)
        self._toolrep = data['is tool rep']
        lyt = data['layout']
        if lyt: self.setLayout(lyt)
        Widget.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['is tool rep'] = self._toolrep
        data['layout'] = self.layout()
        return data
        
    def __deepcopy__(self, memo):
        if self._toolrep:
            copy = type(self)(new=True)
        else:
            copy = deepcopy(super(), memo)
            copy._toolrep = False
            copy.setLayout(deepcopy(self.layout(), memo))
        return copy
    
    auto_pickles = set(['ignore_drag'])
            
    def paintEvent(self, event):
        if self._toolrep:
            painter = QPainter(self)
            painter.fillRect(event.rect(), Qt.gray)
        super().paintEvent(event)
        
    @staticmethod
    def toolbox_representation(cls):
        #from watermelon.vbox_layout import VBoxLayout
        from PyQt5.QtWidgets import QVBoxLayout
        widget = cls()
        widget._toolrep = True
        widget.setLayout(QVBoxLayout())
        label = QLabel('Widget')
        label.setAlignment(Qt.AlignCenter)
        widget.layout().addWidget(label)
        return widget
           
    