from PyQt5.QtWidgets import QDialog
import watermelon.watermelon as watermelon

class Dialog(QDialog, watermelon.Watermelon):
    def __init__(self, parent=None, new=None):
        if new is None: new = True
        super().__init__(parent)
        watermelon.Watermelon.__init__(new)
        
    