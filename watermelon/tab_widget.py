from PyQt5.QtWidgets import QTabWidget
import watermelon.watermelon as watermelon

class TabWidget(QTabWidget, watermelon.Watermelon):
    def __init__(self, parent=None, new=None):
        if new is None: new = True
        super().__init__(parent)
        watermelon.Watermelon.__init__(self, new)
        if new:
            pass
        
    def __setstate__(self, data):
        super().__setstate__(data)    
        for text, widget in data['tabs']:
            self.addTab(widget, text)
        TabWidget.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['tabs'] = [(self.tabText(k), self.widget(k)) for k in range(self.count())]
        return data
    
    def __deepcopy__(self, memo):
        copy = deepcopy(super(), memo)
        for k in range(self.count()):
            text = self.tabText(k)
            widget = self.widget(k)
            copy.addTab(deepcopy(widget, memo), text)
        TabWidget.watermelon_setup(self)
        return copy
    
    def watermelon_setup(self):
        pass
    
    def setLayout(self, lyt):
        self.watermelon_warning(msg='You cannot set the layout on a TabWidget.')
        
    def build_context_menu(self, layout=None):
        super().build_context_menu(layout=False)
        
    @staticmethod
    def toolbox_representation(cls):
        from watermelon.widget import Widget
        widget = cls()
        widget1 = Widget()
        widget2 = Widget()
        widget1.set_drag_instead(widget)
        widget2.set_drag_instead(widget)
        widget.addTab(widget1, 'Tab 1')
        widget.addTab(widget2, 'Tab 2')
        return widget    