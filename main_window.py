import watermelon.window as window

class MainWindow(window.Window):
    def __init__(self, new=None):
        if new is None: new = True
        super().__init__(new)
        self.setWindowTitle('luna moona')
        MainWindow.watermelon_setup(self)
        
    def __setstate__(self, data):
        super().__setstate__(data)
        MainWindow.watermelon_setup(self)
        
    def __getstate__(self):
        return super().__getstate__()
    
    def __deepcopy__(self, memo):
        from copy import deecopy
        copy = deecopy(super(), memo)
        MainWindow.watermelon_setup(copy)
        return copy
    
    def watermelon_setup(self):
        pass