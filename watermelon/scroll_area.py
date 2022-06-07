from PyQt5.QtWidgets import QScrollArea
import watermelon

class ScrollArea(QScrollArea, watermelon.watermelon.Watermelon):
    def __init__(self, parent=None, new=None):
        if new is None: new = True
        super().__init__(parent)
        watermelon.watermelon.Watermelon.__init__(self, new)
        
        if new:
            ScrollArea.watermelon_setup(self)
        
    def __setstate__(self, data):
        super().__setstate__(data)
        self.setWidget(data['widget'])
        ScrollArea.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['widget'] = self.widget()
        return data
        
    def __deepcopy__(self, memo):
        copy = deepcopy(super(), memo)
        copy.setWidget(deepcopy(self.widget(), memo))
        ScrollArea.watermelon_setup(copy)
        return copy