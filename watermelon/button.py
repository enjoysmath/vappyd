from PyQt5.QtWidgets import QPushButton
import watermelon.watermelon as base
import watermelon.code_generator as gen

class Button(QPushButton, base.Watermelon, gen.CodeGenerator):
    def __new__(cls, *args, **kwargs):
        return gen.CodeGenerator.__new__(cls, *args, **kwargs)
        
    def __init__(self, text=None, new=None):
        if new is None: new = True
        super().__init__()
        base.Watermelon.__init__(self, new)
        gen.CodeGenerator.__init__(self, new)
        #geometry.GeometryEditable.__init__(self, new)
        if new:
            if text is not None:
                self.setText(text)
            Button.watermelon_setup(self)
            self.setMaximumWidth(100)
            self.setMaximumHeight(100)
                
    def __setstate__(self, data):
        super().__setstate__(data)
        self.setText(data['text'])
        Button.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['text'] = self.text()
        return data
    
    def __deepcopy__(self, memo):
        from copy import deepcopy
        copy = deepcopy(super(), memo)
        copy.setText(self.text())
        Button.watermelon_setup(copy)
        return copy
    
    auto_pickles = set(['graphicsEffect', 'maximumWidth', 'toolTip', 'focusPolicy', 'autoRepeat',
                        'contextMenuPolicy', 'iconSize', 'minimumSize', 'geometry', 'whatsThis', 'layoutDirection', 
                        'minimumWidth', 'styleSheet', 'maximumHeight', 'foregroundRole', 'updatesEnabled', 'menu', 
                        'autoDefault', 'toolTipDuration', 'windowOpacity', 'autoExclusive', 'maximumSize', 'windowModality', 
                        'objectName', 'backgroundRole', 'autoFillBackground', 'windowFilePath', 'statusTip', 'windowIconText', 
                        'text', 'autoRepeatInterval', 'acceptDrops', 'minimumHeight', 'windowTitle', 'focusProxy', 
                        'accessibleDescription', 'windowRole', 'sizeIncrement', 'baseSize', 'shortcut', 'autoRepeatDelay', 
                        'accessibleName'])    
    
    def watermelon_setup(self):
        super().watermelon_setup()
    
    def build_context_menu(self, layout=None):
        super().build_context_menu(layout=False)    
        
    @staticmethod
    def toolbox_representation(cls):
        widget = cls('Button')
        return widget           
    
       