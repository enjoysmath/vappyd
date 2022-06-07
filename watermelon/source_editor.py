#-------------------------------------------------------------------------
# qsci_simple_pythoneditor.pyw
#
# QScintilla sample with PyQt
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtWidgets import *
import watermelon.watermelon
import watermelon.app
from watermelon.flow_layout import FlowLayout

class SourceEditor(QsciScintilla, watermelon.watermelon.Watermelon):
    ARROW_MARKER_NUM = 8
    source_changed = pyqtSignal()
    source_saved = pyqtSignal()

    def __init__(self, ob=None, window=None, new=None):
        if new is None: new = True
        super().__init__()
        watermelon.watermelon.Watermelon.__init__(self, new)
        self._previousSave = None

        if new:
            lyt = FlowLayout()
            self.setLayout(lyt)
            self._module = ob.__module__
            self._ob = ob
            
            filename = self.filename()
            with open(filename, 'r') as file:
                self.setText(file.read())  
                
            self.setTabDrawMode(QsciScintilla.TabLongArrow)
            self.setTabIndents(True)   
            self.setTabWidth(4)
            SourceEditor.watermelon_setup(self)
        
        # Set the default font
        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.marginClicked.connect(self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow,
                          self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QColor("#ee1111"),
                                      self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

        # Set Python lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        #
        lexer = QsciLexerPython()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        #self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # not too small
        self.setMinimumSize(600, 450)
    
        
        
    def __setstate__(self, data):
        super().__setstate__(data)
        self.setText(data['text'])
        self._module = data['module']
        self._ob = data['ob']
        SourceEditor.watermelon_setup(self)
        
    def __getstate__(self):
        data = super().__getstate__()
        data['text'] = self.text()
        data['module'] = self._module
        data['ob'] = self._ob
        return data
    
    def __deepcopy__(self, memo):
        from copy import deepcopy
        copy = deepcopy(super(), memo)
        copy.setText(self.text())
        copy._module = self._module
        copy._ob = deepcopy(self._ob, memo)
        return copy
    
    def watermelon_setup(self):
        self.textChanged.connect(self.source_code_maybe_changed)
        self._ob.deleted.connect(self.watermelon_delete)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)
    
    def module_name(self):
        return self._module
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            watermelon.app.inst.restart_from_pickle()
        super().keyPressEvent(event)
        
    def filename(self):
        return sys.modules[self._module].__file__
    
    def save_all_source_codes(self):
        filename = self.filename()
        with open(filename, 'w') as source_file:
            text = self.text()
            self._previousSave = text
            source_file.write(text)
        self.source_saved.emit()
        
    def source_code_maybe_changed(self):
        source_code = self.text()
        if self._previousSave != source_code:
            self.source_changed.emit()