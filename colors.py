from color_dialog import ColorDialog

class Colors:
    Color, Dialog = range(2)
    
    def __init__(self, init=None):
        if new in [None, True]:
            self._colors = {}   
        
    def __setstate__(self, data):
        self._colors = data['colors']
        
    def __getstate__(self, data=None):
        if data is None:
            data = {}
        data['colors'] = self._colors
        return data
    
    def __deepcopy__(self, memo, copy):
        from copy import deepcopy
        copy._colors = deepcopy(self._colors, memo)
        
    def color(self, name):
        return self._colors[name][self.Color]
    
    def addColor(self, name, col=None):
        if col is None:
            col = QColor(255, 0, 0)
        dlg = ColorDialog(col)
        self._colors[name] = (col, dlg)
        dlg.currentColorChanged.connect(lambda col: self.setColor(name, col))
        
    def setColor(self, name, col):
        pair = self._colors[name]
        dlg = pair[self.Dialog]
        self._colors[name] = (col, dlg)
        dlg.setCurrentColor(col)
        
    def dialog(self, name):
        return self._colors[name][self.Dialog]