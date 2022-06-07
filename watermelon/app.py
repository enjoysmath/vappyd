from PyQt5.QtWidgets import QApplication, QStyleFactory
import watermelon.source_editor_window
import watermelon.toolbox_window as toolbox
import watermelon.signal_overlay_window as overlay
import sys
import psutil
import logging
import os
import watermelon.watermelon
from PyQt5.QtCore import Qt, QProcess
from collections import OrderedDict
import dill as pickle

class App(QApplication, watermelon.watermelon.Watermelon):
    restart_pickle_name = 'watermelon_restart.pickle'
    version_number = '0.0'
    
    def __init__(self, main=None, args=None, new=None):
        if new is None: new = True
        if args is None: args = []
        super().__init__(args)
        watermelon.watermelon.Watermelon.__init__(self, new)
        #self.setStyle(QStyleFactory.create('fusion'))
        self._windows = OrderedDict()
        self._postPickles = []
        if new:
            self._main = str(main)            
            self.editor = self.create_window(typ=watermelon.source_editor_window.SourceEditorWindow)
            self.toolbox = self.create_window(typ=toolbox.ToolboxWindow)
            self.signal_canvas = self.create_window(typ=overlay.SignalOverlayWindow)
            self._startDirs = {
                'open watermelon' : '.',
                'save watermelon' : '.',
            }
            App.watermelon_setup(self)

    def set_pickle(self, data):  
        self.editor = data['editor']
        self.load_pickled_windows(data['windows'].values())
        self._main = data['main mod']
        self._startDirs = data['start dirs']
        for callback in self._postPickles:
            callback[0](*callback[1])
        self._postPickles.clear()
        self.signal_canvas = data['signal canvas']
        App.watermelon_setup(self)
        
    def load_pickled_windows(self, windows, show=None):
        if show is None: show = False
        for window in windows:
            self._windows[id(window)] = window        
            if show: window.show()
    
    def get_pickle(self):
        data = {
            'editor' : self.editor,
            'windows' : self._windows,
            'main mod' : self._main,
            'start dirs' : self._startDirs,
            'signal canvas' : self.signal_canvas,
        }
        return data
    
    def __deepcopy__(self, memo):
        from copy import deepcopy
        copy = deepcopy(super(), memo)
        copy.editor = deepcopy(self.editor, memo)
        copy._windows = deepcopy(self._windows, memo)
        copy._main = self._main
        copy._startDirs = deepcopy(self._startDirs, memo)
        copy.signal_canvas = deepcopy(self.signal_canvas, memo)
        App.watermelon_setup(copy)
        return copy
    
    @staticmethod
    def pickle_doesnt_load(pickle_name=None):
        global inst
        
        if pickle_name is None:
            pickle_name = App.restart_pickle_name
            
        if os.path.exists(pickle_name):
            try:
                with open(pickle_name, 'rb') as pickle_file:
                    inst = App(__file__, sys.argv, new=False)
                    pickled_app = pickle.load(pickle_file)                 
                    if pickled_app:
                        inst.set_pickle(data=pickled_app)
                        return False
            except Exception as e:
                if inst:
                    inst.exit()
                if __debug__:
                    raise e
                logging.error(e)   
                
        return True
    
    def watermelon_setup(self):
        pass
    
    def close_window(self, window):
        del self._windows[id(window)]
        window.close()
        
    def create_window(self, typ):
        window = typ()
        self._windows[id(window)] = window
        return window
        
    def open_editor(self, ob):
        self.editor.add_editor(ob)
        self.editor.show()
        # HACKFIX to raise window of another app
        self.editor.setWindowState((self.editor.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        self.editor.raise_()      # Mac OSX
        self.editor.activateWindow()    # Windows
        
    def open_watermelon(self, filename=None, widget=None):
        from PyQt5.QtWidgets import QFileDialog
        if filename is None:
            filename, _ = QFileDialog.getOpenFileName(
                parent=widget, caption="Open a watermelon",
                directory=self._startDirs['open watermelon'],
                filter='Watermelon (*.pickle);; All files (*.*)')
        if filename and os.path.exists(filename):
            self._startDirs['open watermelon'] = os.path.dirname(filename)
            try:
                with open(filename, 'rb') as pickle_file:
                    data = pickle.load(pickle_file)
                windows = data['windows'].values()
                self.load_pickled_windows(windows, show=True)
            except Exception as e:
                if __debug__:
                    raise e
                logging.critical(e)
                
    def save_watermelon(self, filename=None, widget=None):
        from PyQt5.QtWidgets import QFileDialog
        if filename is None:
            filename, _ = QFileDialog.getSaveFileName(
                parent=widget, caption="Save a watermelon",
                directory=self._startDirs['save watermelon'],
                filter='Watermelon (*.pickle);; All files (*.*)')
        if filename and os.path.exists(filename):
            self._startDirs['save watermelon'] = os.path.dirname(filename)
            try:
                with open(filename, 'wb') as pickle_file:
                    pickle.dump(self.get_pickle(), pickle_file)
            except Exception as e:
                if __debug__:
                    raise e
                logging.critical(e)
        
    def restart_from_pickle(self):
        """Restarts the current program, with file objects and descriptors
           cleanup
        """   
        with open(self.restart_pickle_name, 'wb') as pickle_file:
            pickle.dump(self.get_pickle(), pickle_file)
        
        for window in self._windows.values():
            window.close()
        self._windows.clear()

        # Close this instance's open files / connections
        try:
            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            logging.error(e)
    
        python = sys.executable
        os.execl(python, python, '"{}"'.format(self.main_module())) 
        
    def connect_signal(self, ob, sig, pos):
        window = ob.window()
        window.line().setP1(pos)
        window.set_watermelon_state(window.ConnectSignal)
        
    def show_windows(self):
        for window in self._windows.values():
            window.show()

    def main_module(self):
        return self._main
    
    def popup_class_extension(self, ob=None):
        if ob is None:
            bases = []
        else:
            bases = [ob]
            
    def callback_after_pickle(self, method, *args):
        self._postPickles.append((method, args))
              
        
inst = None         # Singleton instance of a WatermelonApp

import watermelon.dialog

widget_classes = set([
    watermelon.button.Button, 
    watermelon.widget.Widget,
    watermelon.dialog.Dialog,
])
window_classes = set()
graphics_ob_classes = set()
ob_classes = set()      