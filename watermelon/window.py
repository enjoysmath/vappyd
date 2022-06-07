from PyQt5.QtWidgets import QMainWindow, QMenu
from PyQt5.QtGui import QIcon, QPainter, QPen
import inspect
import watermelon.app
import sys
import types
from PyQt5.QtCore import Qt, QLineF, QPointF, QDir, QSettings, QEvent
import watermelon.watermelon
import os
import watermelon.button as button
import watermelon.drag_and_drop as drag_and_drop

class Window(QMainWindow, watermelon.watermelon.Watermelon, drag_and_drop.DragAndDrop):
    def __init__(self, new=None):
        if new is None: new = True
        super().__init__()
        watermelon.watermelon.Watermelon.__init__(self, new)
        drag_and_drop.DragAndDrop.__init__(self, new)
        self.setWindowTitle('My Watermelon App')
        self.setWindowIcon(QIcon('images/watermelon_app_icon.ico'))
        if __debug__:
            self._state = self.Neutral               
            if new:
                Window.watermelon_setup(self)
            
    def __setstate__(self, data):
        super().__setstate__(data)     
        self.load_dock_settings(data['dock settings'])
        Window.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['dock settings'] = self.save_dock_settings()
        return data
    
    def __deepcopy__(self, memo):
        from copy import deepcopy
        copy = deepcopy(super(), memo)
        copy.load_dock_settings(self.save_dock_settings())
        Window.watermelon_setup(copy)
        return copy
    
    auto_pickles = set([
        'accessibleDescription', 'documentMode', 'focusPolicy', 'centralWidget', 'dock_widget_state', 
        'acceptDrops', 'windowOpacity', 'maximumHeight', 'statusTip', 'focusProxy', 'whatsThis', 'iconSize', 
        'windowModality', 'windowRole', 'graphicsEffect', 'toolButtonStyle', 'windowIconText', 'toolTip', 
        'backgroundRole', 'minimumSize', 'objectName', 'windowFilePath', 'styleSheet', 'parent', 'accessibleName', 
        'maximumWidth', 'unifiedTitleAndToolBarOnMac', 'layoutDirection', 'autoFillBackground', 'foregroundRole', 
        'toolTipDuration', 'updatesEnabled', 'windowTitle', 'sizeIncrement', 'contextMenuPolicy', 'minimumHeight', 
        'minimumWidth', 'tabShape', 'baseSize', 'geometry', 'maximumSize'])
    
    def watermelon_setup(self):
        pass
        
    def mouseMoveEvent(self, event):
        if self._state == self.ConnectSignal:
            self._line.setP2(event.pos())
        else:
            super().mouseMoveEvent(event)
    
    def line(self):
        return self._line

    def set_watermelon_state(self, st):
        if st != self._state:
            self._state = st
            self.update()
            
    def load_dock_settings(self, dock_settings):
        settings_path = os.path.join(QDir.currentPath(), 'dock_settings.ini')
        try: 
            with open(settings_path, 'w') as settings_file:
                settings_file.write(dock_settings)
            settings = QSettings(settings_path, QSettings.IniFormat)
            self.set_dock_widget_state(settings) 
        except Exception as e:
            if __debug__:
                raise e        
            
    def save_dock_settings(self):
        settings_path = os.path.join(QDir.currentPath(), 'dock_settings.ini')
        settings = QSettings(settings_path, QSettings.IniFormat)
        self.dock_widget_state(settings)
        settings.sync()
        try:
            with open(settings_path, 'r') as settings_file:
                return settings_file.read()
        except Exception as e:
            if __debug__:
                raise e        
            
    def set_dock_widget_state(self, settings=None, geometry=True):
        if settings is None:
            settings = QSettings(self.windowTitle(), 'Dock Widget Settings')
        if geometry:
            geom = settings.value('window_geometry')
            if geom:
                self.restoreGeometry(geom)
        state = settings.value('window_dock_state')
        if state:
            self.restoreState(state)
    
    def dock_widget_state(self, settings=None, geometry=True):
        if settings is None:
            settings = QSettings(self.windowTitle(), 'Dock Widget Settings')
        if geometry:
            settings.setValue('window_geometry', self.saveGeometry())
        settings.setValue('window_dock_state', self.saveState())       
        
    def setLayout(self, lyt):
        self.watermelon_warning(msg='You cannot set a layout on a QMainWindow because it already has one, used for docks etc.')
        
    def build_context_menu(self, layout=None):
        super().build_context_menu(layout=False)    
        menu = self.context_menu
        menu.addSeparator()
        action = self.open_action = menu.addAction('Open watermelon')
        action.setIcon(QIcon('images/open_file_icon.png'))
        action.triggered.connect(lambda b: watermelon.app.inst.open_watermelon(widget=self))  
        action = self.save_action = menu.addAction('Save watermelon')
        action.setIcon(QIcon('images/save_file_icon.png'))
        action.triggered.connect(lambda b: watermelon.app.inst.save_watermelon(widget=self))
        menu.addSeparator()
        action = self.extend_watermelon_action = menu.addAction('Extend watermelon')
        action.setIcon(QIcon('images/watermelon_app_icon.ico'))
        action.triggered.connect(lambda b: watermelon.app.inst.popup_class_extension(ob=self))
                      
    def watermelon_drop(self, drop):
        self.setCentralWidget(drop)
        
    def watermelon_drag(self, dragged):
        if watermelon.app.inst.keyboardModifiers() & Qt.ControlModifier:
            dragged.setParent(None)
            dragged.deleteLater()
