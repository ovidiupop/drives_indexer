from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QFile

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import TableReports
from mymodules.GlobalFunctions import getDatabaseLocation
from mymodules.HumanReadableSize import HumanBytes


class Reports(QtWidgets.QWidget):
    extension_added = QtCore.pyqtSignal()
    reindex_for_new_extension = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Reports, self).__init__(parent)

        lay_main = QtWidgets.QVBoxLayout()
        lay_top = QtWidgets.QHBoxLayout()
        lay_bottom = QtWidgets.QHBoxLayout()
        lay_main.addLayout(lay_top)
        lay_main.addLayout(lay_bottom)

        self.group_drives = QtWidgets.QGroupBox()
        self.group_drives.setTitle('Drives')
        lay_top.addWidget(self.group_drives)

        self.group_categories = QtWidgets.QGroupBox()
        self.group_categories.setTitle('Categories')
        lay_top.addWidget(self.group_categories)

        self.group_extensions = QtWidgets.QGroupBox()
        self.group_extensions.setTitle('Extensions')
        lay_top.addWidget(self.group_extensions)

        self.group_database = QtWidgets.QGroupBox()
        self.group_database.setTitle('Database')
        lay_bottom.addWidget(self.group_database)
        lay_bottom.addStretch()

        self.layout_tab_reports = QtWidgets.QHBoxLayout()
        self.layout_tab_reports.addLayout(lay_main)

        self.fillReports()

    def fillReports(self):
        self.reportCategories()
        self.reportDrives()
        self.reportExtensions()
        self.reportDatabase()

    def reportDatabase(self):
        location = getDatabaseLocation()
        dbFile = QFile(location)
        size = HumanBytes.format(dbFile.size(), True)
        records = str(gdb.countFiles())

        lay_v = QtWidgets.QVBoxLayout()

        layh= QtWidgets.QHBoxLayout()
        layh.addWidget(QtWidgets.QLabel('Location:'))
        layh.addWidget(QtWidgets.QLabel(location))
        lay_v.addLayout(layh)

        layh= QtWidgets.QHBoxLayout()
        layh.addWidget(QtWidgets.QLabel('Size:'))
        layh.addWidget(QtWidgets.QLabel(size))
        lay_v.addLayout(layh)

        layh= QtWidgets.QHBoxLayout()
        layh.addWidget(QtWidgets.QLabel('Files Recorded:'))
        layh.addWidget(QtWidgets.QLabel(records))
        lay_v.addLayout(layh)

        lay_v.addStretch()
        self.group_database.setLayout(lay_v)

    def reportDrives(self):
        drives = gdb.filesOnDrive()
        if drives:
            table = TableReports(drives, ["Drive", "Indexed Files", "Active", "Size (Gb)"], [0.4, 0.2, 0.1, 0.3])
            lay_v = QtWidgets.QVBoxLayout()
            layh = QtWidgets.QHBoxLayout()
            layh.addWidget(table)
            lay_v.addLayout(layh)
            self.group_drives.setLayout(lay_v)

    def reportCategories(self):
        categories = gdb.categoryAndFiles()
        if categories:
            table = TableReports(categories, ["Category", "Files"], [0.7, 0.3])
            lay_v = QtWidgets.QVBoxLayout()
            layh = QtWidgets.QHBoxLayout()
            layh.addWidget(table)
            lay_v.addLayout(layh)
            self.group_categories.setLayout(lay_v)

    def reportExtensions(self):
        extensions = gdb.getUsedExtensions()
        if extensions:
            table = TableReports(extensions, ["Category", "Extension", "Files"], [0.4, 0.3, 0.3])
            lay_v = QtWidgets.QVBoxLayout()
            layh = QtWidgets.QHBoxLayout()
            layh.addWidget(table)
            lay_v.addLayout(layh)
            self.group_extensions.setLayout(lay_v)

