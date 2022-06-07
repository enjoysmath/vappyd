import watermelon.window as window
import watermelon.flow_layout as flow_layout
import watermelon.widget
import watermelon.scroll_area
import watermelon.watermelon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QLayoutItem, QSizePolicy, QVBoxLayout
import watermelon.farm

class ToolboxWindow(window.Window):
    unit_size = 123
    
    def __init__(self, new=None):
        if new is None: new = True
        super().__init__()
        self.setWindowTitle('Watermelon Toolbox')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        if new:
            self.scroll_area = watermelon.scroll_area.ScrollArea(parent=self)
            widget = self.container = watermelon.widget.Widget(self)
            widget.set_ignore_drag(True)
            lyt = self.flow_layout = flow_layout.FlowLayout()           
            for cls in watermelon.farm.widget_classes:
                ob = cls.toolbox_representation(cls)
                ob.setParent(self)
                ob.setMinimumWidth(self.unit_size)
                ob.setMinimumHeight(self.unit_size)
                lyt.addWidget(ob)     
            ToolboxWindow.watermelon_setup(self)
            
    def __setstate__(self, data):
        super().__setstate__(data)
        self.scroll_area = data['scroll area']
        self.container = data['container']
        self.flow_layout = data['flow layout']
        self.setLayout(self.flow_layout)
        ToolboxWindow.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['scroll area'] = self.scroll_area
        data['container'] = self.container
        data['flow layout'] = self.flow_layout
        return data
    
    def __deepcopy__(self, memo):
        copy = deepcopy(super(), memo)
        
        ##
        
        ToolboxWindow.watermelon_setup(copy)
        return copy    
    
    def watermelon_setup(self):
        self.setCentralWidget(self.scroll_area)
        self.container.setLayout(self.flow_layout)       
        self.scroll_area.setWidget(self.container)        
        self.installEventFilter(self)      
        
    def add_widget(self, widget):
        self.flow_layout.addItem(widget)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            watermelon.app.inst.restart_from_pickle()   
        else:
            super().keyPressEvent(event)
    
    def eventFilter(self, watched, event):
        if watched is self:
            if event.type() == Qt.WindowCloseButtonHint:
                self.hide()
                return True
        return super().eventFilter(watched, event)
       
    def watermelon_drop(self, drop):
        drop.setMinimumWidth(self.unit_size)
        drop.setMinimumHeight(self.unit_size)
        self.flow_layout.addWidget(drop)