from PyQt5 import QtWidgets, QtCore

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton, CategoriesList, ExtensionsListWidget
from mymodules.GlobalFunctions import iconForButton, confirmationDialog, categoriesCombo


class Extensions(QtWidgets.QWidget):
    extension_added = QtCore.pyqtSignal()
    reindex_for_new_extension = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Extensions, self).__init__(parent)
        # temporary set True after adding a new extension
        # to set indexer prevent to remove already indexed folders
        # and index only files for new extension
        self.added_new_extension = False
        self.last_added_extension = None

        # categories list
        self.categories_list = CategoriesList()
        layout_categories_column = QtWidgets.QVBoxLayout()
        layout_categories_column.addWidget(self.categories_list)

        # extensions list
        self.settings_extensions_list = ExtensionsListWidget()
        self.settings_extensions_list.setMaximumWidth(300)

        # add section
        self.label_add = QtWidgets.QLabel('Add extension to active category:')
        self.add_extension_input = QtWidgets.QLineEdit()
        self.add_extension_input.setPlaceholderText('Insert new extension in selected category')
        self.add_extension_button = PushButton('Add')
        self.add_extension_button.setIcon(iconForButton('SP_FileDialogNewFolder'))

        hlay_add_row = QtWidgets.QHBoxLayout()
        hlay_add_row.addWidget(self.add_extension_input)
        hlay_add_row.addWidget(self.add_extension_button)

        vlay_add = QtWidgets.QVBoxLayout()
        vlay_add.addWidget(self.label_add)
        vlay_add.addLayout(hlay_add_row)

        self.add_group = QtWidgets.QGroupBox()
        self.add_group.setMaximumWidth(300)
        self.add_group.setVisible(False)
        self.add_group.setLayout(vlay_add)

        # move and remove section
        self.label_move = QtWidgets.QLabel('Move selected to category:')
        self.move_categories_cmb = categoriesCombo()
        self.move_button = QtWidgets.QPushButton('Move')
        self.move_button.setIcon(iconForButton('SP_DialogOkButton'))
        hlay_move = QtWidgets.QHBoxLayout()
        hlay_move.addWidget(self.move_categories_cmb)
        hlay_move.addWidget(self.move_button)

        self.label_remove = QtWidgets.QLabel('Remove extension:')
        self.remove_extension_button = PushButton('Remove')
        self.remove_extension_button.setIcon(iconForButton('SP_DialogDiscardButton'))
        hlay_remove = QtWidgets.QHBoxLayout()
        hlay_remove.addWidget(self.remove_extension_button)
        vlay_move_remove = QtWidgets.QVBoxLayout()
        vlay_move_remove.addWidget(self.label_move)
        vlay_move_remove.addLayout(hlay_move)
        vlay_move_remove.addSpacing(20)
        vlay_move_remove.addWidget(self.label_remove)
        vlay_move_remove.addLayout(hlay_remove)

        self.move_remove_group = QtWidgets.QGroupBox()
        self.move_remove_group.setMaximumWidth(300)
        self.move_remove_group.setVisible(False)
        self.move_remove_group.setLayout(vlay_move_remove)

        layout_extensions_column = QtWidgets.QVBoxLayout()
        layout_extensions_column.addWidget(self.settings_extensions_list)
        layout_extensions_column.addWidget(self.add_group)
        layout_extensions_column.addWidget(self.move_remove_group)
        # layout_extensions_column.addStretch()

        self.layout_tab_extensions = QtWidgets.QHBoxLayout()
        self.layout_tab_extensions.addLayout(layout_categories_column)
        self.layout_tab_extensions.addLayout(layout_extensions_column)
        self.layout_tab_extensions.addStretch()

        self.categories_list.currentRowChanged.connect(self.loadExtensionsForCategory)
        self.categories_list.currentRowChanged.connect(self.visibleAddGroup)
        self.categories_list.clicked.connect(self.visibleAddGroup)

        self.settings_extensions_list.clicked.connect(self.visibleMoveRemoveGroup)
        self.settings_extensions_list.currentRowChanged.connect(self.visibleMoveRemoveGroup)

        self.add_extension_input.returnPressed.connect(lambda: self.addNewExtension())
        self.add_extension_button.clicked.connect(lambda: self.addNewExtension())

        self.settings_extensions_list.delete_key_pressed.connect(lambda: self.removeExtension())
        self.remove_extension_button.clicked.connect(lambda: self.removeExtension())
        self.move_button.clicked.connect(lambda: self.moveExtension())

    @QtCore.pyqtSlot(int)
    def loadExtensionsForCategory(self, category_id):
        category_id = category_id + 1
        extensions = gdb.getExtensionsForCategoryId(category_id)
        self.settings_extensions_list.clear()
        self.settings_extensions_list.setItems(extensions)
        # self.settings_extensions_list.setModel(ExtensionsModel(extensions))
        self.settings_extensions_list.setSelectionMode(QtWidgets.QListView.ExtendedSelection)

    @QtCore.pyqtSlot()
    def addNewExtension(self):
        new_extension = self.add_extension_input.text()
        selected_row = self.categories_list.currentRow()
        category_id = selected_row + 1
        if not new_extension:
            QtWidgets.QMessageBox.information(None, 'No Extension', 'Please insert the name of new extension!')
            return
        if gdb.extensionExists(new_extension):
            QtWidgets.QMessageBox.information(None, 'Extension exists', 'The extension already exists!')
            return
        if gdb.addNewExtension(new_extension, category_id):
            self.last_added_extension = new_extension
            self.reindex_for_new_extension.emit()
            self.add_extension_input.setText('')
            self.loadExtensionsForCategory(selected_row)

        else:
            QtWidgets.QMessageBox.critical(None, 'Not added', 'The extension has not been added!')

    def removeExtension(self):
        selected_ex = self.settings_extensions_list.selectedIndexes()
        if len(selected_ex):
            confirmation_text = "If you remove selected extensions, all indexed files belonging to them, " \
                                "will also be removed!<br><br>Do you proceed? "
            confirm = confirmationDialog("Do you remove?", confirmation_text)
            if not confirm:
                return
            extensions = []
            if len(selected_ex):
                extensions = []
                for extension in selected_ex:
                    extensions.append(extension.data())
            if extensions:
                gdb.removeExtensions(extensions)
                self.loadExtensionsForCategory(self.categories_list.currentRow())

    def visibleAddGroup(self):
        selected_category = self.categories_list.selectedItems()
        self.add_group.setVisible(len(selected_category))

    def visibleMoveRemoveGroup(self):
        selected_extension = self.settings_extensions_list.selectedItems()
        self.move_remove_group.setVisible(len(selected_extension))

    def moveExtension(self):
        selected_category = self.move_categories_cmb.currentText()
        if selected_category == 'Categories':
            QtWidgets.QMessageBox.information(self.parent(),
                                              'Error!',
                                              f"If you wish to move extension(s), please select a target category?")
            return None

        selected_ex = self.settings_extensions_list.selectedIndexes()
        if len(selected_ex):
            confirmation_text = "Do you move selected extension(s)!<br><br>Do you proceed? "
            confirm = confirmationDialog("Do you move selected extension(s)?", confirmation_text)
            if not confirm:
                return
            extensions = []
            if len(selected_ex):
                extensions = []
                for extension in selected_ex:
                    extensions.append(extension.data())
            if extensions:
                active_category = self.categories_list.currentIndex().data()
                if active_category:
                    active_cat_id = gdb.getCategoryId(active_category)
                    target_category = gdb.getCategoryId(selected_category)
                    if target_category:
                        if gdb.moveExtensions(target_category, extensions):
                            self.loadExtensionsForCategory(active_cat_id - 1)
