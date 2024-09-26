from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTextEdit


class Editor(QTextEdit):

    def __init__(self, file,  parent=None):
        super(Editor, self).__init__(parent)
        self.file = file
        self.setReadOnly(True)
        text = open(self.file).read()
        self.setText(text)

        layout_editor = QtWidgets.QHBoxLayout()
        layout_editor.addWidget(self)
        self.parent().layout.addLayout(layout_editor)
