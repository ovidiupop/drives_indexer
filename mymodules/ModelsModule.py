import numpy as np
from PyQt5 import QtCore, QtSql, QtGui
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QPersistentModelIndex
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlTableModel, QSqlRelation
from PyQt5.QtWidgets import QStyledItemDelegate, QSpinBox, QLineEdit, QDataWidgetMapper

from mymodules import GDBModule as gdb
from mymodules.GlobalFunctions import HEADER_SEARCH_RESULTS_TABLE, HEADER_DRIVES_TABLE, HEADER_FOLDERS_TABLE, \
    randomColor, HEADER_DUPLICATES_TABLE
from mymodules.HumanReadableSize import HumanBytes


class SearchResultsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent):
        super(SearchResultsTableModel, self).__init__(parent)
        self._data = np.array(data.values)
        self._cols = data.columns
        self.r, self.c = np.shape(self._data)

    def sort(self, column, order):
        """Sort table by given column number."""
        try:
            self.layoutAboutToBeChanged.emit()
            if order == Qt.DescendingOrder:
                # sort reverse n
                self._data = self._data[self._data[:, column].argsort()[::-1]]
            else:
                self._data = self._data[self._data[:, column].argsort()]
            self.layoutChanged.emit()
        except Exception as e:
            print(e)

    def hasMountedDrive(self, index):
        index_column = self.colIndexByName('Drive')
        value = str(self._data[index.row()][index_column])
        return gdb.isDriveActiveByLabel(value)

    def rowData(self, index):
        row_data = []
        for idx in enumerate(HEADER_SEARCH_RESULTS_TABLE):
            row_data.append(str(self._data[index.row()][idx[0]]))
        return row_data

    def colIndexByName(self, name):
        return [ix for ix, col in enumerate(HEADER_SEARCH_RESULTS_TABLE) if col == name][0]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value = self._data[index.row(), index.column()]
                if index.column() == 2:
                    value = HumanBytes.format(value, True)
                return str(value)
            if role == Qt.TextAlignmentRole:
                if index.column() == 2 or index.column() == 3:
                    return Qt.AlignRight

            if role == Qt.ForegroundRole:
                if index.column() == self.colIndexByName('Drive'):
                    value = str(self._data[index.row(), index.column()])
                    # value = str(self._data.iloc[index.row()][index.column()])
                    is_active = gdb.isDriveActiveByLabel(value)
                    if not is_active:
                        return QtGui.QColor('red')
        return None

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return HEADER_SEARCH_RESULTS_TABLE[section]
            if orientation == Qt.Vertical:
                return section + 1  # row numbers start from 1
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemIsEditable
        flags |= Qt.ItemIsSelectable
        flags |= Qt.ItemIsEnabled
        flags |= Qt.ItemIsDragEnabled
        flags |= Qt.ItemIsDropEnabled
        return flags


class DuplicateResultsTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent):
        super(DuplicateResultsTableModel, self).__init__(parent)

        self._data = np.array(data.values)
        self._cols = data.columns
        self.r, self.c = np.shape(self._data)
        self.last_color = None
        self.checks = {}

    def sort(self, column, order):
        """Sort table by given column number."""
        try:
            self.layoutAboutToBeChanged.emit()
            if order == Qt.DescendingOrder:
                # sort reverse n
                self._data = self._data[self._data[:, column].argsort()[::-1]]
            else:
                self._data = self._data[self._data[:, column].argsort()]
            self.layoutChanged.emit()
        except Exception as e:
            print(e)

    def hasMountedDrive(self, index):
        index_column = self.colIndexByName('Drive')
        value = str(self._data[index.row()][index_column])
        return gdb.isDriveActiveByLabel(value)

    def rowData(self, index):
        row_data = []
        for idx in enumerate(HEADER_DUPLICATES_TABLE):
            row_data.append(str(self._data[index.row()][idx[0]]))
        return row_data

    def colIndexByName(self, name):
        return [ix for ix, col in enumerate(HEADER_DUPLICATES_TABLE) if col == name][0]

    def checkState(self, index):
        if index in self.checks.keys():
            return self.checks[index]
        else:
            row = index.row()
            next_row = row + 1
            if next_row < self.rowCount():
                actual_filename = self._data[row, 1]
                next_filename = self._data[next_row, 1]
                actual_size = self._data[row, 2]
                next_size = self._data[next_row, 2]
                if actual_size == next_size and actual_filename == next_filename:
                    return Qt.Unchecked
                else:
                    return Qt.Checked
            return Qt.Unchecked

            # if self._data[index.row(), index.column()] == 0:
            #     return Qt.Checked
            # return Qt.Unchecked

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.CheckStateRole:
                if index.column() == self.colIndexByName('Remove'):
                    return self.checkState(QPersistentModelIndex(index))

            if role == Qt.DisplayRole:
                value = self._data[index.row(), index.column()]
                if index.column() == 2:
                    value = HumanBytes.format(value, True)
                if index.column() == 5:
                    return ""
                return str(value)

            if role == Qt.TextAlignmentRole:
                if index.column() == 2 or index.column() == 3:
                    return Qt.AlignRight
                if index.column() == 5:
                    return Qt.AlignCenter

            if role == Qt.ForegroundRole:
                if index.column() == self.colIndexByName('Drive'):
                    value = str(self._data[index.row(), index.column()])
                    is_active = gdb.isDriveActiveByLabel(value)
                    if not is_active:
                        return QtGui.QColor('red')
                if index.column() == self.colIndexByName('Filename'):
                    value = str(self._data[index.row(), index.column()])
                    previous_value = str(self._data[index.row() - 1, index.column()])
                    if previous_value != value:
                        self.last_color = randomColor()
                    return QtGui.QColor(*self.last_color)

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            self.checks[QPersistentModelIndex(index)] = value
            return True
        return False

    def rowCount(self, parent=None):
        return self.r

    def columnCount(self, parent=None):
        return self.c

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return HEADER_DUPLICATES_TABLE[section]
            if orientation == Qt.Vertical:
                return section + 1  # row numbers start from 1
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= Qt.ItemIsUserCheckable
        return flags


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}

    def setFilterByColumn(self, regex, column):
        self.filters[column] = regex
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        for key, regex in self.filters.items():
            ix = self.sourceModel().index(source_row, key, source_parent)
            if ix.isValid():
                text = self.sourceModel().data(ix).toString()
                if not text.contains(regex):
                    return False
        return True


def sorter(model_obj, table_obj, filter_key, order=Qt.DescendingOrder):
    # add sorting to table
    sortermodel = QSortFilterProxyModel()
    sortermodel.setSourceModel(model_obj)
    sortermodel.setFilterKeyColumn(filter_key)

    # use sorter as model for table
    table_obj.setModel(sortermodel)
    table_obj.setSortingEnabled(True)
    table_obj.sortByColumn(filter_key, order)


class FoldersModel(QtSql.QSqlRelationalTableModel):
    def __init__(self, parent=None):
        super(FoldersModel, self).__init__(parent)
        self.setTable('folders')
        self.setRelation(2, QSqlRelation("drives", "serial", "label"))
        self.setEditStrategy(self.OnRowChange)
        self.setColumnsName()
        self.setSort(self.fieldIndex("id"), Qt.AscendingOrder)
        sorter(self, self.parent(), 1)
        self.parent().setItemDelegate(FoldersItemsDelegate(self))
        self.select()

    def setColumnsName(self):
        for k, v in HEADER_FOLDERS_TABLE.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Horizontal, v)

    def nameOfColumn(self, index):
        return [col for idx, col in enumerate(HEADER_FOLDERS_TABLE) if idx == index][0]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        column_name = self.nameOfColumn(index.column())
        if role == Qt.DisplayRole:
            if column_name == 'status':
                return None

        if role == Qt.DecorationRole:
            if column_name == 'status':
                if QSqlTableModel.data(self, index) == 1:
                    return QIcon(':tick.png')
                else:
                    return QIcon(':exclamation.png')
        return QSqlTableModel.data(self, index, role)

    def selectRowByModelId(self, last_id):
        for i in range(self.rowCount()):
            if last_id == self.record(i).value("id"):
                self.parent().selectRow(i)
                break


class FoldersItemsDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        return None


class SearchResultsTableItemsDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def nameOfColumn(self, index):
        return [col for idx, col in enumerate(HEADER_SEARCH_RESULTS_TABLE) if idx == index][0]

    def createEditor(self, parent, option, index):
        return None


class DrivesTableModel(QtSql.QSqlTableModel):
    def __init__(self):
        super(DrivesTableModel, self).__init__()
        self._data = []
        self.table = 'drives'
        self.setTable(self.table)
        self.setEditStrategy(self.OnRowChange)
        self.setColumnsName()
        self.setSort(self.fieldIndex("size"), Qt.DescendingOrder)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        column_name = nameOfColumn(index.column())

        if role == Qt.DisplayRole:
            if column_name == 'active':
                return None
            if column_name == 'serial':
                return QSqlTableModel.data(self, index)

        if role == Qt.DecorationRole:
            if column_name == 'active':
                if QSqlTableModel.data(self, index) == 1:
                    return QIcon(':tick.png')
                else:
                    return QIcon(':cross.png')

        if role == Qt.TextAlignmentRole:
            if column_name == 'size':
                return Qt.AlignVCenter + Qt.AlignRight
        # default, no specific condition found
        return QSqlTableModel.data(self, index, role)

    def setColumnsName(self):
        for k, v in HEADER_DRIVES_TABLE.items():
            idx = self.fieldIndex(k)
            self.setHeaderData(idx, Qt.Horizontal, v)

    def setTableSorter(self, column_index, table):
        sort_filter = QSortFilterProxyModel()
        sort_filter.setSourceModel(self)
        sort_filter.setFilterKeyColumn(column_index)
        table.setModel(sort_filter)
        table.setSortingEnabled(True)
        table.sortByColumn(column_index, Qt.DescendingOrder)


class DrivesMapper(QDataWidgetMapper):
    def __init__(self, parent):
        super().__init__(parent)
        model = parent.drives_table_model
        self.setModel(model)
        self.addMapping(parent.drive_serial_input, model.fieldIndex('serial'))
        self.addMapping(parent.drive_name_input, model.fieldIndex('name'))
        self.addMapping(parent.drive_label_input, model.fieldIndex('label'))
        self.addMapping(parent.drive_size_input, model.fieldIndex('size'))
        self.addMapping(parent.drive_active_input, model.fieldIndex('active'))


def nameOfColumn(idx):
    names = HEADER_DRIVES_TABLE.keys()
    for index, name in enumerate(names):
        if index == idx:
            return name


class DrivesItemsDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        disabled = ['serial', 'name', 'active', 'path']
        if nameOfColumn(index.column()) in disabled:
            editor = QLineEdit(parent)
            editor.setDisabled(True)
            return editor
        elif 'label' == nameOfColumn(index.column()):
            editor = QLineEdit(parent)
            editor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            return editor
        elif 'size' == nameOfColumn(index.column()):
            spinbox = QSpinBox(parent)
            spinbox.setRange(0, 2000000)
            spinbox.setSingleStep(100)
            spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            return spinbox
        else:
            return None
