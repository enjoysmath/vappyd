from ui.ui_debug_watch_widget import Ui_DebugWatchWidget
from PyQt5.QtWidgets import QWidget

class DebugWatchWidget(QWidget, Ui_DebugWatchWidget):
    def __init__(self, item):
        super().__init__()
        super().__init__()
        self.setupUi(self)
        self._watched = item
        self.pythonIDLine.setText(str(id(item)))
        self.objectNameLine.setText(item.objectName())