from PyQt5 import QtWidgets

from mymodules.GlobalFunctions import getHelp


class HelpContent(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(HelpContent, self).__init__(parent)

        self.resize(800, 600)
        self.tabs = QtWidgets.QTabWidget()
        self.addTabs()
        self.tabs.setMovable(True)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.show()

    def addTabs(self):
        tabs = ['General', 'Search', 'Duplicates', 'Drives', 'Folders', 'Categories', 'Extensions', 'Preferences', 'Other']
        for tab in tabs:
            self.contentTab(tab)

    def contentTab(self, name):
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setText(self.getContent(name.lower()))
        self.tabs.addTab(text, name)

    def getContent(self, category):
        return getHelp(category)
