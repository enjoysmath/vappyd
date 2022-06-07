from PyQt5.QtWidgets import QWidget
from ui.ui_debug_widget import Ui_DebugWidget
from debug_watch_widget import DebugWatchWidget

class DebugWidget(QWidget, Ui_DebugWidget):
    def __init__(self, view):
        super().__init__()
        super().__init__()
        self.setupUi(self)
        self.view = view
        self._watches = {}
        self.addWatchButton.clicked.connect(lambda b: self.addWatchItem())
        self.itemWatchTabs.tabCloseRequested.connect(self.removeWatchItem)
        
    def addWatchItem(self, item=None):
        if item is None:
            item = self.scene().selectedItems()
            if item: item = item[0]
        if item:
            tab_name = self.nextTypeName(item)
            if isinstance(tab_name, int):
                tab_name = item.__class__.__name__ + (' ' + str(tab_name) if tab_name != 0 else '')
                for k in range(self.itemWatchTabs.count()):
                    if self.itemWatchTabs.tabText(k) == tab_name:
                        self.itemWatchTabs.setCurrentIndex(k)
                        return
            self.itemWatchTabs.addTab(DebugWatchWidget(item), tab_name)    
            self._watches[item.__class__.__name__].append(item)
    
    def removeWatchItem(self, tab_index):
        name_parts = self.itemWatchTabs.tabText(tab_index).split()
        if len(name_parts) == 2:
            name_id = int(name_parts[1])
        else:
            name_id = 0
        typename = name_parts[0]
        self._watches[typename].pop(name_id)
        if len(self._watches[typename]) == 0:
            del self._watches[typename]
        self.itemWatchTabs.removeTab(tab_index)
            
    def scene(self):
        return self.view.scene()
    
    def sceneSelectionChanged(self):
        selected = self.scene().selectedItems()
        self.addWatchButton.setEnabled(len(selected) > 0)
        
    def nextTypeName(self, item):
        typename = item.__class__.__name__
        if typename not in self._watches:
            self._watches[typename] = []
            return typename
        if item in self._watches[typename]:
            return self._watches[typename].index(item)
        return typename + ' ' + str(len(self._watches[typename]))
            