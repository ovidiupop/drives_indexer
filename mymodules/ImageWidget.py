from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QStatusBar


class Image(QtWidgets.QWidget):
    def __init__(self, file, parent=None):
        super(Image, self).__init__(parent)
        self.file = file
        self.file_size = self.parent().file_size
        self.resize(800, 600)
        pixmap = QPixmap(file)
        self.image_width = pixmap.width()
        self.image_height = pixmap.height()
        if self.image_height > self.width() or self.image_height > self.height():
            image = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        else:
            image = pixmap.scaled(self.image_width, self.image_height, Qt.KeepAspectRatio)
        self.label = QtWidgets.QLabel()
        self.label.setPixmap(image)
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.status_bar = QStatusBar()
        # self.status_bar.setFont(QFont("Noto Sans", 10))
        self.status_bar.setFixedHeight(14)
        image_size = str(self.image_width) + ' X ' + str(self.image_height) + '  ' + self.file_size
        status_bar_message = file + ' ' + image_size
        self.status_bar.showMessage(status_bar_message)
        self.status_bar_layout = QtWidgets.QVBoxLayout()
        self.status_bar_layout.addLayout(self.layout)
        self.status_bar_layout.addWidget(self.status_bar)

        self.parent().layout.addLayout(self.status_bar_layout)
        self.parent().resized.connect(self.parentResizeEvent)

    def parentResizeEvent(self):
        if self.image_height < self.width() or self.image_height < self.height():
            return
        # reduce size with complementary widgets (200)
        parent_width = self.parent().width() - 200
        parent_height = self.parent().height() - 200
        pixmap1 = QPixmap(self.file)
        pixmap = pixmap1.scaled(parent_width, parent_height, Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        self.label.resize(parent_width, parent_height)

