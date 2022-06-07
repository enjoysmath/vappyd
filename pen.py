from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt

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
    
    def __init__(self, color=None, width=None, style=None, cap=None, join=None):
        if not isinstance(color, QPen):
            if style is None:
                style = Qt.SolidLine
            if cap is None:
                cap = Qt.RoundCap
            if join is None:
                join = Qt.RoundJoin
            if color is None or color == Qt.NoPen:
                super().__init__(Qt.NoPen)
            else:
                super().__init__(color, width, style, cap, join)
        else:
            super().__init__(color)
    
    def __getstate__(self):
        return {
            'color' : self.color(), 
            'width' : self.widthF(), 
            'style' : int(self.style()), 
            'cap' : int(self.capStyle()), 
            'join' : int(self.joinStyle()),
        }
    
    def __setstate__(self, data):
        color = data['color']
        width = data['width']
        style = self.styleEnum[data['style']]
        cap = self.capEnum[data['cap']]
        join = self.joinEnum[data['join']]
        self.__init__(color, width, style, cap, join)
        
    def __deepcopy__(self, memo):
        pen = type(self)(self.color(), self.widthF(), self.style(), self.capStyle(), self.joinStyle())
        return pen
