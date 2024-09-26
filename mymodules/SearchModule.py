import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtWidgets import QAbstractItemView

from mymodules import ComponentsModule, ModelsModule
from mymodules.CategoriesModule import CategoriesSelector
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import *
from mymodules.ModelsModule import SearchResultsTableItemsDelegate
from mymodules.PreviewFileModule import FileDetailDialog


class Search(QtWidgets.QWidget):
    export_all_results_signal = QtCore.pyqtSignal()
    export_selected_results_signal = QtCore.pyqtSignal()
    double_clicked_result_row = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Search, self).__init__(parent)

        self.export_all_results_signal.connect(self.exportAllResultsToCSV)
        self.export_selected_results_signal.connect(self.exportSelectedResultsToCSV)

        self.search_input_label = QtWidgets.QLabel('Search for:')
        self.search_term_input = QtWidgets.QLineEdit()
        self.search_term_input.setPlaceholderText('Insert term to search')
        self.search_term_input.setFocus(Qt.OtherFocusReason)

        self.search_button = PushButton('Search')
        self.search_button.setMinimumWidth(200)
        self.search_button.setIcon(QIcon(':magnifier.png'))
        self.search_button.setStyleSheet("""QPushButton { text-align: center; }""")
        self.search_button.setFixedSize(100, 40)

        self.search_term_input.returnPressed.connect(self.onSubmitted)
        self.search_button.clicked.connect(self.onSubmitted)

        self.found_search_label = QtWidgets.QLabel('Found')
        self.found_search_label.hide()

        # set table for results
        self.found_results_table = ComponentsModule.TableViewAutoCols(None)
        self.found_results_table.setColumns([0.40, 0.25, 0.10, 0.10, 0.15])
        self.found_results_table.doubleClicked.connect(self.double_clicked_result_row)
        self.found_results_table.setItemDelegate(SearchResultsTableItemsDelegate(self))

        self.found_results_table_model = ModelsModule.SearchResultsTableModel(
            pd.DataFrame([], columns=HEADER_SEARCH_RESULTS_TABLE), self.found_results_table)

        # categories box
        self.categories_selector_search = CategoriesSelector(parent=self)
        self.categories_layout = self.categories_selector_search.generateBox()

        h_label = QtWidgets.QHBoxLayout()
        h_label.addWidget(self.search_input_label)

        self.spinner = spinner(parent)
        self.spinner.hide()

        h_search_row = QtWidgets.QHBoxLayout()
        h_search_row.addWidget(self.search_term_input)
        h_search_row.addWidget(self.search_button)

        h_categories_row = QtWidgets.QHBoxLayout()
        self.checkboxes_group = QtWidgets.QGroupBox()
        self.checkboxes_group.setMaximumHeight(100)
        self.checkboxes_group.setLayout(self.categories_layout)
        h_categories_row.addWidget(self.checkboxes_group)

        v_col_general = QtWidgets.QVBoxLayout()
        v_col_general.addLayout(h_label)
        v_col_general.addLayout(h_search_row)
        v_col_general.addLayout(h_categories_row)

        # search results section
        search_results_layout = QtWidgets.QVBoxLayout()
        row_over_table = QtWidgets.QHBoxLayout()
        row_over_table.addWidget(self.spinner, 0, Qt.AlignLeft)
        row_over_table.addWidget(self.found_search_label, 0, Qt.AlignLeft)
        row_over_table.addStretch()

        search_results_layout.addLayout(row_over_table)
        search_results_layout.addWidget(self.found_results_table)

        v_col_general.addLayout(search_results_layout)

        h_main = QtWidgets.QHBoxLayout()
        h_main.addLayout(v_col_general)

        self.search_tab_layout = QtWidgets.QVBoxLayout()
        self.search_tab_layout.addLayout(h_main)

        # prepare extensions for search
        self.extensions_for_search = []
        self.getExtensionsForSearch()
        self.double_clicked_result_row.connect(self.doubleClickedResultRow)

    @QtCore.pyqtSlot()
    def doubleClickedResultRow(self):
        # check if row belongs to a mounted drive
        selected = self.found_results_table.currentIndex()
        if self.found_results_table.model().hasMountedDrive(selected):
            self.prepareFileDetailDialog(self.found_results_table)
        else:
            QtWidgets.QMessageBox.information(None, 'No file preview', 'The drive is not mounted in system!')

    @QtCore.pyqtSlot()
    def onSubmitted(self):
        search_term = self.search_term_input.text()
        if not search_term:
            QtWidgets.QMessageBox.information(None, 'No term to search', 'Please write a term for search')
            return
        self.spinner.show()
        self.found_search_label.setText(f'Please wait! Searching ...')
        self.found_search_label.show()
        QtTest.QTest.qWait(1000)

        self.getExtensionsForSearch()
        extensions = self.extensions_for_search
        # searching
        results = gdb.findFiles(search_term, extensions)
        count_results = len(results) if results else 0

        self.spinner.hide()
        self.found_search_label.setText(f'Found: {count_results} results')
        self.updateResults(results)

    def updateResults(self, results):
        self.found_results_table_model = ModelsModule.SearchResultsTableModel(
            pd.DataFrame(results, columns=HEADER_SEARCH_RESULTS_TABLE), self.found_results_table)

        self.found_results_table.setModel(self.found_results_table_model)
        self.found_results_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.found_results_table.setSortingEnabled(True)
        # self.found_results_table.sortByColumn(2, Qt.DescendingOrder)

    # load extensions when the search is started
    # based on checked categories from search form
    def getExtensionsForSearch(self):
        selected_categories = []
        checkboxes = self.checkboxes_group.findChildren(QtWidgets.QCheckBox)
        for checkbox in checkboxes:
            if checkbox.isChecked():
                selected_categories.append(checkbox.text())
        # with selected categories from search form
        # take the list of extensions for selected categories
        # and set them for searching
        self.extensions_for_search = gdb.getExtensionsForCategories(selected_categories)

    # synchronize search form categories with defaults
    @QtCore.pyqtSlot()
    def setPreferredCategoriesOnSearchForm(self):
        categories = gdb.getAll('categories')
        if categories:
            selected = []
            for category in categories:
                if category['selected'] == 1:
                    selected.append(category['category'])
                checkboxes = self.checkboxes_group.findChildren(QtWidgets.QCheckBox)
                for ckb in checkboxes:
                    text = ckb.text()
                    ckb.setChecked(True) if text in selected else ckb.setChecked(False)

    @QtCore.pyqtSlot()
    def exportSelectedResultsToCSV(self):
        model = self.found_results_table.model()
        columns = model.columnCount()
        indexes = self.found_results_table.selectionModel().selectedRows()
        results = []
        for index in indexes:
            one_line = []
            for col in range(0, columns):
                val = model.data(model.index(index.row(), col), Qt.DisplayRole)
                # we have to convert values to string if we wish to concatenate them
                if not isinstance(val, str):
                    val = '%s' % val
                one_line.append(val)
            line = CSV_COLUMN_SEPARATOR.join(one_line)
            results.append(line)
        return self.putInFile(results)

    @QtCore.pyqtSlot()
    def exportAllResultsToCSV(self):
        model = self.found_results_table.model()
        columns = model.columnCount()
        rows = model.rowCount()
        results = []
        for row in range(0, rows):
            one_line = []
            for col in range(0, columns):
                val = model.data(model.index(row, col), Qt.DisplayRole)
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
            QtWidgets.QMessageBox.information(self, 'Nothing to export', "There is nothing to export<br><br>Search for "
                                                                         "something!")
            return False

        if int(getPreference('header_to_csv')):
            header = CSV_COLUMN_SEPARATOR.join(HEADER_SEARCH_RESULTS_TABLE)
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

    def prepareFileDetailDialog(self, table):
        ext_cat = gdb.getExtensionsCategories()
        data = table.model().rowData(table.currentIndex())
        file_path = data[0] + '/' + data[1]
        exists = QtCore.QFileInfo.exists(file_path)
        if exists:
            info = QFileInfo(file_path)
            extension = info.suffix()
            # if extension:
            if setStatusBarMW('Please wait while drive is initialized...'):
                if extension in ext_cat:
                    category = ext_cat[extension]
                    FileDetailDialog(category, data, self)
                else:
                    FileDetailDialog(None, data, self)

