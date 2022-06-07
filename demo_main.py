from demo_window import DemoWindow
from PyQt5.QtWidgets import QApplication, QStyleFactory
import sys
import watermelon.app

if __name__ == '__main__':
    watermelon.app.inst = watermelon.app.App()
    watermelon.app.inst.setStyle(QStyleFactory.create('fusion'))
    
    window = DemoWindow()
    window.show()
        
    sys.exit(app.exec_())