from PyQt5 import QtCore

import resources
from mymodules import TabsModule
from mymodules.GlobalFunctions import *
from mymodules.MenuModule import IMenu


class IndexerWindow(QMainWindow):
    kill_device_monitor_runner = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(IndexerWindow, self).__init__(parent)
        # instantiate database
        gdb.GDatabase()
        # load resources
        # resources
        # create gui
        self.init_UI()
        # instantiate menu
        IMenu(self)
        self.show()

    def closeEvent(self, _ev):
        sizes = [str(self.size().width()), str(self.size().height())]
        preference = ', '.join(sizes)
        # save last window size as preferred
        setPreferenceByName('window_size', preference)

        self.kill_device_monitor_runner.emit()

    def setStatusBar(self, text):
        self.statusbar.showMessage(text)

    def _createTabs(self):
        self.tabs_view = TabsModule.TabsWidget(self)
        self.tabs = self.tabs_view.tabs_main

    def _createStatusBar(self):
        self.statusbar = self.statusBar()

    def init_UI(self):
        self._createTabs()
        self.setCentralWidget(self.tabs)
        window_size = getPreference('window_size').split(', ')
        self.resize(int(window_size[0]), int(window_size[1]))
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(":app_logo_32.png"))
        self._createStatusBar()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(APP_NAME)
    mw = IndexerWindow()
    sys.exit(app.exec())

