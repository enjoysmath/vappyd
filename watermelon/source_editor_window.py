import watermelon.window
import watermelon.source_editor
import watermelon.tab_widget
from PyQt5.QtCore import Qt, QEvent

class SourceEditorWindow(watermelon.window.Window):
    def __init__(self, new=None):
        if new is None: new = True
        super().__init__()
        self.setWindowTitle('Watermelon Source Editor')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        if new:
            self._editors = {}          # Keyed by id(ob)
            self._tabs = watermelon.tab_widget.TabWidget(parent=self)
            self._tabs.set_ignore_drag(True)
            SourceEditorWindow.watermelon_setup(self)
        
    def __setstate__(self, data):
        super().__setstate__(data)
        self._editors = {}
        editors = data['editors']
        for editor in data['editors']:
            self._editors[id(editor)] = editor
        self._tabs = data['tabs']     
        SourceEditorWindow.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['editors'] = list(self._editors.values())
        data['tabs'] = self._tabs
        return data
    
    def __deepcopy__(self, memo):
        copy = deepcopy(super(), memo)
        copy._editors = {}
        for editor in self._editors.values():
            editor_copy = deepcopy(editor, memo)
            copy._editors[id(editor_copy)] = editor_copy
        copy._tabs = deepcopy(self._tabs, memo)
        SourceEditorWindow.watermelon_setup(copy)
        return copy    
    
    def watermelon_setup(self):
        self.setCentralWidget(self._tabs)
        
    def save_all_source_codes(self):
        for editor in self._editors.values():
            editor.save_all_source_codes()
        
    def add_editor(self, ob):
        editor = watermelon.source_editor.SourceEditor(
            ob, window=self)
        editor.deleted.connect(lambda: self.remove_editor(ob))
        editor.source_changed.connect(lambda: self.set_tab_title(editor, saved=False))
        editor.source_saved.connect(lambda: self.set_tab_title(editor, saved=True))
        self._editors[id(ob)] = editor
        self._tabs.addTab(editor, editor.module_name())
        editor.installEventFilter(self)
        
    def remove_editor(self, ob):
        editor = self._editors[id(ob)]
        editor.removeEventFilter(self)
        del self._editors[id(ob)]
        
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

    def set_tab_title(self, editor, saved, title=None):
        saved = '*' if not saved else ''

        if title is None:
            title = editor.module_name() + saved
        
        k = self.find_tab_index(editor)
        if k is not None:
            self._tabs.setTabText(k, title)
            
    def find_tab_index(self, editor):
        for k in range(self._tabs.count()):
            if self._tabs.widget(k) is editor:
                return k
        return None
            
    