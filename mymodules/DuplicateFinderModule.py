import os

import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtTest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QFileDialog, QLabel

from mymodules import ComponentsModule, ModelsModule
from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import HEADER_DUPLICATES_TABLE, spinner, CSV_COLUMN_SEPARATOR, getPreference, \
    getDefaultDir, CSV_LINE_SEPARATOR


class DuplicateFinder(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(DuplicateFinder, self).__init__(parent)

        self.find_duplicate_label = QLabel('Find duplicates by name and size')
        self.find_duplicate_button = PushButton('Find')
        self.find_duplicate_button.setMinimumWidth(200)
        self.find_duplicate_button.setIcon(QIcon(':magnifier.png'))
        self.find_duplicate_button.setStyleSheet("""QPushButton { text-align: center; }""")
        self.find_duplicate_button.setFixedSize(180, 40)
        self.find_duplicate_button.clicked.connect(self.findDuplicates)

        self.export_duplicate_label = QLabel('Export duplicates to CSV')
        self.export_duplicate_button = PushButton('Export')
        self.export_duplicate_button.setMinimumWidth(200)
        self.export_duplicate_button.setIcon(QIcon(':table_export.png'))
        self.export_duplicate_button.setStyleSheet("""QPushButton { text-align: center; }""")
        self.export_duplicate_button.setFixedSize(180, 40)
        self.export_duplicate_button.clicked.connect(self.exportAllResultsToCSV)

        self.spinner = spinner(parent)
        self.spinner.hide()
        self.searching_label = QtWidgets.QLabel('Found')
        self.searching_label.hide()

        # set table for results
        self.duplicate_results_table = ComponentsModule.TableViewAutoCols(None)
        self.duplicate_results_table.setColumns([0.35, 0.25, 0.10, 0.10, 0.15, 0.05])
        self.duplicate_results_table_model = ModelsModule.DuplicateResultsTableModel(
            pd.DataFrame([], columns=HEADER_DUPLICATES_TABLE), self.duplicate_results_table)

        v_lay_find_duplicates = QtWidgets.QVBoxLayout()
        v_lay_find_duplicates.addWidget(self.find_duplicate_label)
        v_lay_find_duplicates.addWidget(self.find_duplicate_button)

        v_lay_export_duplicates = QtWidgets.QVBoxLayout()
        v_lay_export_duplicates.addWidget(self.export_duplicate_label)
        v_lay_export_duplicates.addWidget(self.export_duplicate_button)

        h_row = QtWidgets.QHBoxLayout()
        h_row.addLayout(v_lay_find_duplicates)
        h_row.addLayout(v_lay_export_duplicates)
        h_row.addStretch()

        # search results section
        duplicate_results_layout = QtWidgets.QVBoxLayout()
        row_over_table = QtWidgets.QHBoxLayout()
        row_over_table.addWidget(self.spinner, 0, Qt.AlignLeft)
        row_over_table.addWidget(self.searching_label, 0, Qt.AlignLeft)
        row_over_table.addStretch()

        duplicate_results_layout.addLayout(row_over_table)
        duplicate_results_layout.addWidget(self.duplicate_results_table)

        v_lay = QtWidgets.QVBoxLayout()
        v_lay.addLayout(h_row)
        v_lay.addLayout(duplicate_results_layout)

        self.find_duplicate_tab_layout = QtWidgets.QVBoxLayout()
        self.find_duplicate_tab_layout.addLayout(v_lay)

    @QtCore.pyqtSlot()
    def findDuplicates(self):
        self.searching_label.show()
        self.spinner.show()
        self.searching_label.setText(f'Please wait! Searching for duplicates...')
        self.searching_label.show()
        QtTest.QTest.qWait(1000)
        results = gdb.findDuplicates()
        if results:
            self.updateResults(results)

    def updateResults(self, results):
        self.duplicate_results_table.show()

        self.duplicate_results_table_model = ModelsModule.DuplicateResultsTableModel(
            pd.DataFrame(results, columns=HEADER_DUPLICATES_TABLE), self.duplicate_results_table)

        self.duplicate_results_table.setModel(self.duplicate_results_table_model)
        self.duplicate_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.spinner.hide()
        count_results = len(results) if results else 0
        self.searching_label.setText(f'Found: {count_results} results')
        self.duplicate_results_table.setSortingEnabled(True)
        self.duplicate_results_table_model.sort(2, Qt.DescendingOrder)

    @QtCore.pyqtSlot()
    def exportAllResultsToCSV(self):
        # if self.duplicate_results_table.isVisible():
        model = self.duplicate_results_table.model()

        columns = model.columnCount()
        rows = model.rowCount()
        results = []
        for row in range(0, rows):
            one_line = []
            for col in range(0, columns):
                if col != 5:
                    val = model.data(model.index(row, col), Qt.DisplayRole)
                else:
                    val = model.data(model.index(row, col), Qt.CheckStateRole)
                    val = "Remove" if val else ""

                val = val.replace(CSV_COLUMN_SEPARATOR, '_')
                # we have to convert values to string if we wish to concatenate them
                if not isinstance(val, str):
                    val = '%s' % val
                one_line.append(val)
            line = CSV_COLUMN_SEPARATOR.join(one_line)
            results.append(line)
        return self.putInFile(results)

    # we have to pass data as list
    def putInFile(self, data):
        if not data:
            QtWidgets.QMessageBox.information(self, 'Nothing to export', "There is nothing to export<br>")
            return False

        if int(getPreference('header_to_csv')):
            if self.duplicate_results_table.isVisible():
                header = CSV_COLUMN_SEPARATOR.join(HEADER_DUPLICATES_TABLE)
            else:
                header = CSV_COLUMN_SEPARATOR.join(HEADER_DUPLICATES_STRICT_TABLE)
            data.insert(0, header)

        default_dir = getDefaultDir()
        default_filename = os.path.join(default_dir, "")
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", default_filename, "CSV Files (*.csv)"
        )
        if filename:
            file = open(filename, 'w')
            text = CSV_LINE_SEPARATOR.join(data)
            file.write(text)
            file.close()
            QtWidgets.QMessageBox.information(None, 'Export CSV', 'Exported successfully!')
            return
