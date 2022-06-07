from PyQt5.QtWidgets import QMenu, QGridLayout, QPushButton, QWidget
from PyQt5.QtCore import pyqtBoundSignal, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QIcon
import sys
import watermelon.app
import inspect
from collections import OrderedDict
from watermelon.flow_layout import FlowLayout
from copy import deepcopy

class Watermelon:
    Neutral, ConnectSignal, ConnectSlot = range(3)
    auto_pickles = set()
    
    deleted = pyqtSignal()
    
    def __init__(self, new=None):           
        if new is None: new = True
        self.build_context_menu()
        Watermelon.watermelon_codegen_init(self) 
        if new:
            self._ignoreDrag = False
            self._dragInstead = self
        
    def __setstate__(self, data):
        self.__init__(new=False)
        for get_name in self.auto_pickles:
            set_name = self.setter_from_getter(get_name)
            setter = getattr(self, set_name)
            setter(data[get_name])
        if hasattr(self, 'children'):
            for child in data['children']:
                child.setParent(self)                
        Watermelon.watermelon_setup(self)
        
    def __getstate__(self):
        data = { get_name : getattr(self, get_name)() for get_name in self.auto_pickles }
        if hasattr(self, 'children'):
            data['children'] = [child for child in self.children() if isinstance(child, Watermelon)]
        return data
    
    def __deepcopy__(self, memo):
        copy = type(self)()
        memo[id(self)] = copy
        for get_name in self.auto_pickles:
            setter = getattr(copy, self.setter_from_getter(get_name))
            setter(deepcopy(getattr(self, get_name)(), memo))
        if hasattr(self, 'children'):
            for child in self.children():
                child = deepcopy(child, memo)
                child.setParent(copy)
        Watermelon.watermelon_setup(copy)
        return copy    
    
    def watermelon_setup(self):
        """
        Call with YourClassName.watermelon_setup(self).  This way, the base class doesn't
        call the subclass setup() and we can place a call at the end of __init__(new=True),
        __setstate__, __deepcopy__, both in subclass and base classes, if we follow said
        calling convention.  This is like a post __init__ method used for connecting
        signals & stuff.   Do not call super()'s watermelon_setup, it's called by __init__'s,
        __setstates__'s and __deepcopys__'s already and by convention.
        """
        if __debug__:
            if hasattr(self, 'add_menu'):
                self.add_menu.setEnabled(self.layout() is not None)
    
    def drag_instead(self):
        return self._dragInstead
    
    def set_drag_instead(self, instead):
        self._dragInstead = instead
        
    def ignore_drag(self):
        return self._ignoreDrag
    
    def set_ignore_drag(self, en):
        self._ignoreDrag = en
        
    def build_context_menu(self, layout=None):
        if layout is None:
            layout = True
        self.context_menu = QMenu()
        self.build_source_code_menu()
        if layout:
            self.build_layout_menu()
            self.build_add_menu()        
        self.build_signals_menu()
        self.build_methods_menu()
        
    def build_source_code_menu(self):
        menu = self.context_menu
        menu1 = self.source_code_menu = menu.addMenu('Source code')
        parent = self.parent()
        if parent:
            action = self.parent_source_action = menu1.addAction('parent :' + parent.__class__.__name__)
            action.triggered.connect(
                lambda b: watermelon.app.inst.open_editor(ob=parent)
            )
        action = self.self_source_action = menu1.addAction('self : ' + self.__class__.__name__)
        action.triggered.connect(
            lambda b: watermelon.app.inst.open_editor(ob=self)
        )    
        
    def build_layout_menu(self):
        menu = self.context_menu
        m = self.layoutMenu = menu.addMenu('Layout')
        m.addAction('Grid').triggered.connect(
            lambda b: self.setLayout(QGridLayout(self))
        )        
        
    def build_add_menu(self):
        menu = self.context_menu
        m = self.add_menu = menu.addMenu('Add')
        m.addAction('Button').triggered.connect(
            lambda b: self.layout().addWidget(self.create_button())
        )        
        
    def build_signals_menu(self):
        menu = self.context_menu
        m = self.signals_menu = menu.addMenu('Signals')
    
    def build_methods_menu(self):
        menu = self.context_menu        
        m = self.methods_menu = menu.addMenu('Methods')
        self.watermelon_method_menu = m.addMenu('snake_case')
        self.watermelon_method_menu.setIcon(QIcon('images/watermelon_app_icon.ico'))
        self.is_method_menu = m.addMenu('is...')
        self.set_method_menu = m.addMenu('set...')
        self.event_method_menu = m.addMenu('...event...')
        self.minmax_method_menu = m.addMenu('...min/max...')
        self.addremove_method_menu = m.addMenu('...add/remove...')
        self.window_method_menu = m.addMenu('...window...')
        self.python_method_menu = m.addMenu('__...__')
        self.child_method_menu = m.addMenu('...child...')
        self.dock_method_menu = m.addMenu('...dock...')
        self.widthheight_method_menu = m.addMenu('...width/height...')
        self.widget_method_menu = m.addMenu('...widget...')
        self.map_method_menu = m.addMenu('...map...')
        self.keybmouse_method_menu = m.addMenu('...key/mouse...')
        self.object_method_menu = m.addMenu('...object...')
        self.conndisc_method_menu = m.addMenu('...dis/connect...')
        self.menu_method_menu = m.addMenu('...menu...')
        self.geom_method_menu = m.addMenu('...geometry/size/x/y...')
        self.destroy_method_menu = m.addMenu('...destroy/delete...')
        self.show_method_menu = m.addMenu('...show...')
        self.misc_method_menu = m.addMenu('Miscellaneous')
                            
    def contextMenuEvent(self, event):
        menu = self.context_menu
        if menu:
            pos = event.pos()
            pos = self.mapToGlobal(pos)
            if __debug__:
                self.build_signals_dynamic_menu(pos)
                self.build_methods_dynamic_menu(pos)
            menu.exec_(pos)
        
    def build_signals_dynamic_menu(self, pos):
        self.signals_menu.clear()
        for member in inspect.getmembers(self):
            name = member[0]
            attr = getattr(self, name)
            if isinstance(attr, pyqtBoundSignal):
                prototype = inspect.getmembers(attr)[-1][1]
                lparen = prototype.index('(')
                argstr = prototype[lparen+1:-1]
                args = argstr.split(',')
                self.signals_menu.addAction(name).triggered.connect(
                    lambda b: self.connect_signal(name, pos)) 
                
    def build_methods_dynamic_menu(self, pos):
        self.is_method_menu.clear()
        self.set_method_menu.clear()
        self.event_method_menu.clear()
        self.minmax_method_menu.clear()
        self.addremove_method_menu.clear()
        self.window_method_menu.clear()
        self.python_method_menu.clear()
        self.child_method_menu.clear()
        self.dock_method_menu.clear()
        self.widthheight_method_menu.clear()
        self.widget_method_menu.clear()
        self.map_method_menu.clear()
        self.keybmouse_method_menu.clear()
        self.conndisc_method_menu.clear()
        self.menu_method_menu.clear()
        self.watermelon_method_menu.clear()
        self.destroy_method_menu.clear()
        self.misc_method_menu.clear()
        self.show_method_menu.clear()
        self.geom_method_menu.clear()
        
        for member in inspect.getmembers(self):
            name = member[0]
            attr = getattr(self, name)
            if not isinstance(attr, pyqtBoundSignal) and callable(attr):
                lower = name.lower()
                if self.is_snake_case(name):
                    self.watermelon_method_menu.addAction(name)                
                elif name.startswith('is'):
                    self.is_method_menu.addAction(name)
                elif name.startswith('set'):
                    self.set_method_menu.addAction(name)
                elif 'event' in lower:
                    self.event_method_menu.addAction(name)
                elif 'min' in lower or 'max' in lower:
                    self.minmax_method_menu.addAction(name)
                elif 'add' in lower or 'remove' in lower:
                    self.addremove_method_menu.addAction(name)
                elif 'window' in lower:
                    self.window_method_menu.addAction(name)
                elif name.startswith('__') and name.endswith('__'):
                    self.python_method_menu.addAction(name)
                elif 'child' in lower:
                    self.child_method_menu.addAction(name)
                elif 'dock' in lower:
                    self.dock_method_menu.addAction(name)
                elif 'width' in lower or 'height' in lower:
                    self.widthheight_method_menu.addAction(name)
                elif 'widget' in lower:
                    self.widget_method_menu.addAction(name)
                elif 'map' in lower:
                    self.map_method_menu.addAction(name)
                elif 'key' in lower or 'mouse' in lower:
                    self.keybmouse_method_menu.addAction(name)
                elif 'object' in lower:
                    self.object_method_menu.addAction(name)
                elif 'connect' in lower or 'disconnect' in lower:
                    self.conndisc_method_menu.addAction(name)
                elif 'menu' in lower:
                    self.menu_method_menu.addAction(name)
                elif lower == 'x' or lower == 'y' or 'geometry' in lower or 'size' in lower \
                     or 'position' in lower:
                    self.geom_method_menu.addAction(name)
                elif 'destroy' in lower or 'delete' in lower or 'kill' in lower:
                    self.destroy_method_menu.addAction(name)
                elif 'show' in lower:
                    self.show_method_menu.addAction(name)
                else:
                    self.misc_method_menu.addAction(name)
                #if self.is_snake_case(attr):
                    
                #prototype = inspect.getmembers(attr)
                ##print(prototype)
                #self.methods_menu.addAction(name).triggered.connect(
                    #lambda b: self.connect_slot(name, pos)
                #)
                
    def is_snake_case(self, ident):
        if ident.islower() and '_' in ident and '__' not in ident:
            return True
        return False

    def create_button(self):
        import watermelon.button as button
        button = button.Button('Button')
        return button
            
    def connect_signal(self, sig_name, global_pos):
        app.inst.connect_signal(ob=self, sig=sig_name, pos=global_pos)
        
    def connect_slot(self, slot_name, global_pos):
        print('blah')
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F4:
            watermelon.app.inst.open_editor(ob=self)
    
    def set_transparent_for_mouse_events(self, en):
        attr = Qt.WA_TransparentForMouseEvents
        if en != self.testAttribute(attr):
            self.setAttribute(attr, en)    
            
    def setLayout(self, lyt):
        if lyt is not self.layout():
            super().setLayout(lyt)
            self.add_menu.setEnabled(lyt is not None)
            
    def watermelon_warning(self, msg, excep=None):
        if excep:
            print('WATERMELON EXCEPTION: ' + str(excep))
        print('WATERMELON WARNING: ' + msg)
        
    def watermelon_drop(self, drug, dropped):
        pass

    def getter_from_setter(self, method_name):
        method_name = method_name[3:].strip('_')
        return method_name[0].lower() + method_name[1:] 
    
    def setter_from_getter(self, method_name):
        if '_' in method_name:
            return 'set_' + method_name
        return 'set' + method_name[0].upper() + method_name[1:]
            
    def is_camel_case(self, s):
        return s != s.lower() and s != s.upper() and "_" not in s    
    
    @staticmethod
    def toolbox_representation(cls):
        return cls()

    def watermelon_drag(self, dragged):
        pass
    
    def watermelon_delete(self):
        self.deleted.emit()
        self.deleteLater()
        
    def watermelon_codegen_init(self):
        """
        Do not edit any method with "codegen" in its name.  
        Gets overwritten by simple code-generation scheme.
        """
        pass