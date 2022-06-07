import sys
import watermelon.app as app
from main_window import MainWindow
import watermelon.button as button

if __name__ == "__main__":
    if app.App.pickle_doesnt_load():
        app.inst = app.App(__file__, sys.argv)
        app.inst.create_window(typ=MainWindow)
    
    app.inst.show_windows()
    
    #from watermelon.pyqt_pickle import determine_auto_pickleable_members
    #determine_auto_pickleable_members(MainWindow())
    
    b = button.Button('Text')
    b.setText('blah')
    
    code = b.generate_init()
    #print(b.generate_import())
    
    sys.exit(app.inst.exec_())
    
