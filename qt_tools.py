from PyQt5.QtCore import QPoint, QPointF, Qt, QObject
from PyQt5.QtGui import QTransform, QBrush, QColor, QPen
from PyQt5.QtWidgets import QListWidgetItem, QListWidget, QGraphicsItem, QTreeWidgetItem, QGraphicsView
from PyQt5.QtGui import QColor
import re
from collections import OrderedDict
from PyQt5.QtGui import QPixmap, QImage, QPainter
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice


########################## COLOR TOOLS #################################

def roundedButtonCSS(bg_col, col, radius):
    return """QPushButton {
    background-color: """ + rgbaToCss(bg_col) + """; 
    color: """ + rgbaToCss(col) + """;
    border-radius: """ + str(radius) + "px;}"

cssBgColorRegex = re.compile(r'background-color:(?P<rgba>rgba\(.*\));')
cssColorRegex = re.compile(r'color:(?P<rgba>rgba\(.*\));')
cssRgbaRegex = re.compile(r'rgba\((?P<r>\d{1,3}),(?P<g>\d{1,3}),(?P<b>\d{1,3}),(?P<a>\d{1,3})\)')
cssRadiusRegex = re.compile(r'border-radius:(?P<radius>\d+(.\d+)?)px')

def cssCornerRadiusToFloat(stylesheet):
    stylesheet = stylesheet.replace(' ', '')
    match = cssRadiusRegex.search(stylesheet)
    if match:
        return float(match.group('radius'))
    return 0.0
        
def parseCSSColor(stylesheet):
    stylesheet = stylesheet.replace(' ', '')
    match = cssColorRegex.search(stylesheet)
    if match:
        return cssRgbaToColor(match.group('rgba'))
    return None

def parseCSSBgColor(stylesheet):
    stylesheet = stylesheet.replace(' ', '')
    match = cssBgColorRegex.search(stylesheet)
    if match:
        return cssRgbaToColor(match.group('rgba'))
    return None    

def simpleMaxContrastingColor(color):
    return QColor(
        0 if color.red() > 127 else 255,
        0 if color.green() > 127 else 255,
        0 if color.blue() > 127 else 255,
        color.alpha())

def colorToByteArray(color):
    return [color.red(), color.green(), color.blue(), color.alpha()]

def byteArrayToColor(byteArr):
    return QColor(byteArr[0], byteArr[1], byteArr[2], byteArr[3])

def invertColor(color):
    return QColor(255-color.red(), 255-color.blue(), 255-color.green(), color.alpha())

def cssRgbaToColor(css):
    match = cssRgbaRegex.match(css)
    r = int(match.group('r')); 
    g = int(match.group('g'))
    b = int(match.group('b')); 
    a = int(match.group('a'))
    color = QColor(r, g, b, a)
    return color

def dictToColor(dictColor):
    return QColor(dictColor["red"], dictColor["green"], dictColor["blue"], dictColor["alpha"])

def cssBgColor(color):
    return "background-color:" + rgbaToCss(color) + ";"


#########################################


def removeFromCombo(comboBox, text):
    for k in range(0, comboBox.count()):
        if comboBox.itemText(k) == text:
            comboBox.removeItem(k)
            break

def pointToStr(point, decimals=3):
    d = str(decimals)
    return (("(%." + d + "f") % point.x()) + ((", %." + d + "f") % point.y())


def collidingItems(gfxItems):
    collidingItems = []
    for item in gfxItems:
        collidingItems += item.collidingItems()
    return collidingItems


def pointFloatToPointInt(qpointF):
    return QPoint(int(qpointF.x() + 0.5), int(qpointF.y() + 0.5))


def tabIndexFromText(tabs, text):
    if tabs != None:
        for k in range(0, tabs.count()):
            if tabs.tabText(k) == text:
                return k
    return None


def textListFromComboBox(combo, exclude=[]):
    textList = []
    for k in range(0, combo.count()):
        text = combo.itemText(k)
        if text not in exclude:
            textList.append(text)
    return textList


def findListWtext(listW, text):
    for k in range(0, listW.count()):
        if listW.item(k).text() == text:
            return k
    return None


def listWtoTextList(listW):
    texts = []
    count = listW.count()
    for k in range(0, count):
        texts.append(listW.item(k).text())
    return texts


def removeTextListFromListW(listW, textList):
    if textList not in [None, []]:
        textList0 = listWtoTextList(listW)
        selected = listWselectedTextList(listW)
        for k in range(0, len(textList)):
            text = textList[k]
            if text in textList0:
                j = textList0.index(text)
                textList0.pop(j)
        listW.clear()
        listW.addItems(textList0)
        for text in selected:
            k = findListWtext(listW, text)
            if k != None:
                item = listW.item(k)
                item.setSelected(True)   
        
        
def addTextListToListW(listW, textList):
    textList0 = listWtoTextList(listW)
    selected = listWselectedTextList(listW)
    for k in range(0, len(textList)):
        text = textList[k]
        if text not in textList0:
            textList0.append(text)
    listW.clear()
    listW.addItems(textList0)
    for text in selected:
        k = findListWtext(listW, text)
        if k != None:
            item = listW.item(k)
            item.setSelected(True)        
    
    
def  listWselectedTextList(listW):
    selected = listW.selectedItems()
    return [item.text() for item in selected]


def copyTimer(timer0):
    timer = QTimer()
    timer.setInterval(timer0.interval())
    timer.setSingleShot(timer0.singleShot())
    return timer


def setBrushColor(brush, color):
    brush = SimpleBrush(color)    #TODO include gradient when we get around to it
    return brush


def rgbaToCss(color):
    string = "rgba("
    rgbChannels = [color.red(), color.green(), color.blue()]
    for chan in rgbChannels:
        string += str(chan) + ", "
    string += str(color.alpha()) + ");"
    return string


    
# For some reason QObjects can't be a parent class of a QGraphicsItem for the purpose of using pyqtSignal in the class.
# Maybe this will fix that, and result in the same useage syntax.

# Where a normal signal doesn't work, try inheriting this class and making the object an instance member of the class

class PseudoSignal(QObject):
    # In derived class:
    # signal = pyqtSignal(str)  e.g.
        
    def emit(self, *args):
        self.signal.emit(*args)
        
    def connect(self, slot):
        self.signal.connect(slot)
        
    def disconnect(self, slot):
        self.signal.disconnect(slot)
        
        
# Pickling / unpickling

class Pen(QPen):
    styleEnum = {
        int(Qt.NoPen) : Qt.NoPen,
        int(Qt.SolidLine) : Qt.SolidLine,
        int(Qt.DashLine) : Qt.DashLine,
        int(Qt.DotLine) : Qt.DotLine,
        int(Qt.DashDotLine) : Qt.DashDotLine,
        int(Qt.DashDotDotLine) : Qt.DashDotDotLine,
        int(Qt.CustomDashLine) : Qt.CustomDashLine,
    }
    
    capEnum = {
        int(Qt.FlatCap) : Qt.FlatCap,
        int(Qt.SquareCap) : Qt.SquareCap,
        int(Qt.RoundCap) : Qt.RoundCap,
    }
    
    joinEnum = {
        int(Qt.MiterJoin) : Qt.MiterJoin,
        int(Qt.BevelJoin) : Qt.BevelJoin,
        int(Qt.RoundJoin) : Qt.RoundJoin,
        int(Qt.SvgMiterJoin) : Qt.SvgMiterJoin,
    }
    
    def __init__(self, color=None, width=None, style=Qt.SolidLine, cap=Qt.RoundCap, join=Qt.RoundJoin):
        if color is None or color == Qt.NoPen:
            QPen.__init__(self, Qt.NoPen)
        else:
            QPen.__init__(self, color, width, style, cap, join)
    
    COLOR, WIDTH, STYLE, CAP, JOIN = range(5)
    def __getstate__(self):
        return [self.color(), self.widthF(), int(self.style()), int(self.capStyle()), int(self.joinStyle())]
    
    def __setstate__(self, data):
        color = data[self.COLOR]
        width = data[self.WIDTH]
        style = self.styleEnum[data[self.STYLE]]
        cap = self.capEnum[data[self.CAP]]
        join = self.joinEnum[data[self.JOIN]]
        self.__init__(color, width, style, cap, join)
        
    def __deepcopy__(self, memo):
        pen = type(self)(self.color(), self.widthF(), self.style(), self.capStyle(), self.joinStyle())
        return pen


class SimpleBrush(QBrush):
    def __init__(self, color=None):
        super().__init__(color)
    
    def __setstate__(self, data):
        self.__init__(data['color'])
        
    def __getstate__(self):
        return {
            'color' : self.color(),
        }
        
    def __deepcopy__(self, memo):
        copy = type(self)(self.color())
        memo[id(self)] = self
        return copy
    
    
graphicsItemFlagsEnum = {
    int(QGraphicsItem.ItemIsMovable) : QGraphicsItem.ItemIsMovable,
    int(QGraphicsItem.ItemIsSelectable) : QGraphicsItem.ItemIsSelectable,
    int(QGraphicsItem.ItemIsFocusable) : QGraphicsItem.ItemIsFocusable,
    int(QGraphicsItem.ItemClipsToShape) : QGraphicsItem.ItemClipsToShape,
    int(QGraphicsItem.ItemClipsChildrenToShape) : QGraphicsItem.ItemClipsChildrenToShape,
    int(QGraphicsItem.ItemIgnoresTransformations) : QGraphicsItem.ItemIgnoresTransformations,
    int(QGraphicsItem.ItemIgnoresParentOpacity) : QGraphicsItem.ItemIgnoresParentOpacity,
    int(QGraphicsItem.ItemDoesntPropagateOpacityToChildren) : QGraphicsItem.ItemDoesntPropagateOpacityToChildren,
    int(QGraphicsItem.ItemStacksBehindParent) : QGraphicsItem.ItemStacksBehindParent,
    int(QGraphicsItem.ItemUsesExtendedStyleOption) : QGraphicsItem.ItemUsesExtendedStyleOption,
    int(QGraphicsItem.ItemHasNoContents) : QGraphicsItem.ItemHasNoContents,
    int(QGraphicsItem.ItemSendsGeometryChanges) : QGraphicsItem.ItemSendsGeometryChanges,
    int(QGraphicsItem.ItemAcceptsInputMethod) : QGraphicsItem.ItemAcceptsInputMethod,
    int(QGraphicsItem.ItemNegativeZStacksBehindParent) : QGraphicsItem.ItemNegativeZStacksBehindParent,
    int(QGraphicsItem.ItemIsPanel): QGraphicsItem.ItemIsPanel,
    int(QGraphicsItem.ItemSendsScenePositionChanges) : QGraphicsItem.ItemSendsScenePositionChanges,
}

renderHintsEnum = {
    int(QPainter.Antialiasing): QPainter.Antialiasing,
    int(QPainter.TextAntialiasing) : QPainter.TextAntialiasing,
    int(QPainter.SmoothPixmapTransform) : QPainter.SmoothPixmapTransform,
    int(QPainter.HighQualityAntialiasing) : QPainter.HighQualityAntialiasing,
    int(QPainter.NonCosmeticDefaultPen) : QPainter.NonCosmeticDefaultPen,
}

dragModeEnum = {
    int(QGraphicsView.NoDrag) : QGraphicsView.NoDrag,
    int(QGraphicsView.ScrollHandDrag): QGraphicsView.ScrollHandDrag,
    int(QGraphicsView.RubberBandDrag): QGraphicsView.RubberBandDrag,
}

focusPolicyEnum = {
    int(Qt.TabFocus) : Qt.TabFocus,
    int(Qt.ClickFocus) : Qt.ClickFocus,
    int(Qt.StrongFocus) : Qt.StrongFocus,
    int(Qt.WheelFocus): Qt.WheelFocus,
    int(Qt.NoFocus) : Qt.NoFocus,
}

def unpickleFocusPolicy(policy):
    return unpickleFlags(policy, enum=focusPolicyEnum)

def unpickleDragMode(mode):
    return unpickleFlags(mode, enum=dragModeEnum)

def unpickleRenderHints(hints):
    return unpickleFlags(hints, enum=renderHintsEnum)

def unpickleGfxItemFlags(flags):
    return unpickleFlags(flags, enum=graphicsItemFlagsEnum)
        
def unpickleFlags(flags, enum):
    if not isinstance(flags, int):
        return flags
    flags1 = None
    for k in range(0, 31):
        bits = int(flags) & (1 << k)
        if bits and bits in enum:
            if flags1 is None:
                flags1 = enum[bits]
            else:
                flags1 |= enum[bits]
    return flags1
        
        
# BUGFIX: can't set items' pen or brush alpha

def setPenAlpha(pen, alpha):
    color = pen.color()
    color.setAlpha(alpha)
    pen = Pen(color, pen.widthF(), pen.style(), pen.capStyle(), pen.joinStyle())
    return pen


def setBrushAlpha(brush, alpha):
    color = brush.color()
    color.setAlpha(alpha)
    brush = SimpleBrush(color)
    return brush


def setPenColor(pen, color):
    pen = Pen(color, pen.widthF(), pen.style(), pen.capStyle(), pen.joinStyle())
    return pen
    
def setPenWidth(pen, width):
    pen = Pen(pen.color(), width, pen.style(), pen.capStyle(), pen.joinStyle())
    return pen

def setPenStyle(pen, style):
    pen = Pen(pen.color(), pen.widthF(), style, pen.capStyle(), pen.joinStyle())
    return pen
    
# Get the oldest ancestor of a graphics item, or the item itself if it has no parent
def oldestParentObject(obj):
    parent = obj.parentItem()
    while parent is not None:
        obj = parent
        parent = obj.parentItem()
    return obj

def firstAncestorOfType(item, type_tuple):
    if item is None:
        return None
    if isinstance(item, type_tuple):
        return item
    return firstAncestorOfType(item.parentItem(), type_tuple)
    
def ancestors(obj):
    parent = obj.parentItem()
    elders = []
    while parent:
        elders.append(parent)
        parent = parent.parentItem()
    return elders

def oldestAncestorInList(obj, items):
    elders = ancestors(obj)
    for elder in elders:
        if elder in items:
            return elder
    return None

def hasAncestor(ancestor, obj):
    parent = obj.parentItem()
    if parent is None:
        return False
    if parent is ancestor:
        return True
    return hasAncestor(ancestor, parent)

def allDescendentsOfItem(item):
    items = item.childItems()
    children = set(items)
    for child in items:
        children = children.union(allDescendentsOfItem(child))
    return children

def allDescendentsOfItems(items):
    descendents = set()
    for item in items:
        descendents = descendents.union(allDescendentsOfItem(item))
    return descendents

def dictionaryFillTreeItem(item, value, expanded=False, list_delim='[list]'):
    item.setExpanded(expanded)
    if type(value) in [OrderedDict, dict]:
        for key, val in sorted(value.items()):
            child = QTreeWidgetItem()
            child.setText(0, str(key))
            item.addChild(child)
            item.setExpanded(expanded)
            dictionaryFillTreeItem(child, val, expanded, list_delim)
    elif type(value) is list:
        list_item= QTreeWidgetItem()
        list_item.setText(0, list_delim)
        item.addChild(list_item)
        for k in range(len(value)):
            val = value[k]
            child = QTreeWidgetItem()
            child.setText(0, str(k))
            list_item.addChild(child)
            dictionaryFillTreeItem(child, val, expanded, list_delim)
            child.setExpanded(expanded)    
    else:
        child = QTreeWidgetItem()
        child.setText(0, str(value))
        item.addChild(child)


def dictionaryFillTreeWidget(widget, value, expanded=False, list_delim='[list]'):
    widget.clear()
    dictionaryFillTreeItem(widget.invisibleRootItem(), value, expanded, list_delim)
    
    
# Pixmap pickling

def picklePixmap(pixmap):
    image = pixmap.toImage()
    byt_arr = QByteArray()
    buffer = QBuffer(byt_arr)
    buffer.open(QIODevice.WriteOnly);
    image.save(buffer, "PNG");
    return byt_arr

def unpicklePixmap(byt_arr):
    image = QImage.fromData(byt_arr, "PNG")
    return QPixmap.fromImage(image)

def firstAncestorOfType(type, item):
    if isinstance(item, type):
        return item
    elif item.parentItem():
        return firstAncestorOfType(type, item.parentItem())
    return None

def toCamelCase(words):
    if isinstance(words, str):
        words = words.split(' ')
    camel = words[0].strip(' ').lower()
    for word in words[1:]:
        camel += word.strip(' ').capitalize()
    return camel

def enableTaskbarIcon(appid):
    import ctypes
    #from ctypes import wintypes
    #lpBuffer = wintypes.LPWSTR()
    #AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
    #AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
    #appid = lpBuffer.value
    #ctypes.windll.kernel32.LocalFree(lpBuffer)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    
    
def pointToList(point):
    return [point.x(), point.y()]

def colorToList(col):
    return [col.red(), col.green(), col.blue(), col.alpha()]