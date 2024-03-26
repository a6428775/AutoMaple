
from PyQt5 import QtWidgets
from src.modules import UI_setting_function


if __name__ == "__main__":

    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    ui = UI_setting_function.ui_setting_fun()
    ui.show()

    sys.exit(app.exec_())
