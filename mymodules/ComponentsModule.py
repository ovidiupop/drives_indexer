from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QListView, QAbstractItemView, QTreeView, QListWidgetItem

from mymodules import GDBModule as gdb
from mymodules.GlobalFunctions import getIcon


class TableViewAutoCols(QtWidgets.QTableView):
    """ Override QTableView to override resizeEvent method
    """

    delete_key_pressed = QtCore.pyqtSignal()

    def __init__(self, model, selection='Single', parent=None):
        super(TableViewAutoCols, self).__init__(parent)
        self.columns = []
        self.selection = selection

        rowHeight = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(rowHeight)
        self.setModel(model)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        if self.selection == 'Single':
            self.setSelectionMode(QtWidgets.QTableView.SingleSelection)
        else:
            self.setSelectionMode(QtWidgets.QTableView.MultiSelection)

    def setColumns(self, columns):
        self.columns = columns

    def resizeEvent(self, event):
        width = event.size().width()
        for index, size in enumerate(self.columns):
            self.setColumnWidth(index, int(width * size))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_key_pressed.emit()
        else:
            super().keyPressEvent(event)


class TableReports(QtWidgets.QTableWidget):
    def __init__(self, data, header, column_size, parent=None):
        super(TableReports, self).__init__(parent)
        self.header = header
        self._data = data
        self.rows_count = len(data)
        self.columns_count = len(header)
        self.column_size = column_size
        self.setRowCount(self.rows_count)
        self.setColumnCount(self.columns_count)
        self.setHorizontalHeaderLabels(header)
        self.setData()
        self.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setSortingEnabled(True)

    def setData(self):
        for i, data in enumerate(self._data):
            for j in range(self.columns_count):
                item = QtWidgets.QTableWidgetItem()
                item.setData(QtCore.Qt.DisplayRole, data[j])
                self.setItem(i, j, item)

    def resizeEvent(self, event):
        width = event.size().width()
        for index, size in enumerate(self.column_size):
            self.setColumnWidth(index, width * size)


class PushButton(QtWidgets.QPushButton):
    """
    Push button supporting icon to left/right
    """
    def __init__(self, *args, **kwargs):
        super(PushButton, self).__init__(*args, **kwargs)
        self.styleSheet = "QPushButton { text-align: left; padding: 5}"
        self.setStyleSheet(self.styleSheet)

    def setTextCenter(self):
        self.setStyleSheet("QPushButton {text-align: center; padding: 5}")

    def setMyIcon(self, icon, icon_size=QtCore.QSize(16, 16), position=QtCore.Qt.AlignLeft):
        self.icon = icon
        self.icon_size = icon_size
        icon_alignment = QtCore.Qt.AlignLeft
        if position == 'right':
            icon_alignment = QtCore.Qt.AlignRight
        self.setIcon(QtGui.QIcon())
        label_icon = QtWidgets.QLabel()
        label_icon.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        label_icon.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(label_icon, alignment=icon_alignment)
        label_icon.setPixmap(self.icon.pixmap(icon_size))


class ListWidget(QtWidgets.QListWidget):
    delete_key_pressed = QtCore.pyqtSignal()

    def __init__(self,  parent=None):
        super(ListWidget, self).__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_key_pressed.emit()
        else:
            super().keyPressEvent(event)


class getExistingDirectories(QFileDialog):
    def __init__(self, *args, **kwargs):
        super(getExistingDirectories, self).__init__(*args, **kwargs)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.Directory)
        self.setOption(self.ShowDirsOnly, True)
        self.findChildren(QListView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.findChildren(QTreeView)[0].setSelectionMode(QAbstractItemView.ExtendedSelection)


class CategoriesList(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(CategoriesList, self).__init__(parent)
        self.setFixedWidth(300)

        categories = gdb.getAll('categories')
        for category in categories:
            icon = QIcon(category['icon'])
            item = QListWidgetItem(icon, category['category'], self)
            self.addItem(item)


class ExtensionsListWidget(QtWidgets.QListWidget):

    delete_key_pressed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ExtensionsListWidget, self).__init__(parent)
        self.setFixedWidth(300)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_key_pressed.emit()
        else:
            super().keyPressEvent(event)

    def setItems(self, extensions):
        for extension in extensions:
            icon = getIcon(extension, 32)
            item = QListWidgetItem(icon, extension, self)
            self.addItem(item)
