from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton
from mymodules.GlobalFunctions import iconForButton


class Categories(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Categories, self).__init__(parent)
        self.categories = gdb.getAll('categories')
        categories_layout = CategoriesSelector().generateBox()
        self.layout_tab_categories = QtWidgets.QHBoxLayout()
        self.layout_tab_categories.addLayout(categories_layout)


class CategoriesSelector(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(CategoriesSelector, self).__init__(parent=parent, *args, **kwargs)

        self.column_splitter = 3
        self.categories = gdb.getAll('categories')
        self.check_all_categories = PushButton('Check all')
        self.check_all_categories.setIcon(iconForButton('SP_DialogApplyButton'))
        self.parent_load_default_categories = PushButton('Reload preferred')
        self.parent_load_default_categories.setIcon(iconForButton('SP_BrowserReload'))

        # Only Search set the table_obj because it has different behavior than Category
        # On Search selected categories are not saved as preferred, but used only for current search
        self.parent_name = self.parent().metaObject().className() if self.parent() else None

    def generateBox(self):
        columns = []
        # Create categories checkboxes
        for idx, cat in enumerate(self.categories):
            category = cat['category']
            cat_name = QtWidgets.QCheckBox(category, self)
            cat_name.setIcon(QIcon(cat['icon']))
            cat_name.setChecked(cat['selected'])
            x = cat_name
            cat_name.stateChanged.connect(lambda checked, val=x: self.setPreferredCategory(val))
            if idx % self.column_splitter == 0:
                column_v_layout = QtWidgets.QVBoxLayout()
                columns.append(column_v_layout)
            # add cat_name to previous column_v_layout
            column_v_layout.addWidget(cat_name)

        h_cats = QtWidgets.QHBoxLayout()
        for column_v_layout in columns:
            column_v_layout.addStretch()
            h_cats.addLayout(column_v_layout)

        self.check_all_categories.setCheckable(True)
        self.check_all_categories.setChecked(gdb.allCategoriesAreSelected())
        self.check_all_categories.clicked.connect(lambda: self.checkAllCategories(self.check_all_categories.isChecked()))

        h_buttons = QtWidgets.QVBoxLayout()
        h_buttons.addWidget(self.check_all_categories)
        if self.parent_name:
            h_buttons.addWidget(self.parent_load_default_categories)
            self.parent_load_default_categories.clicked.connect(lambda: self.parent().setPreferredCategoriesOnSearchForm())

        h_cats.addLayout(h_buttons)
        v_main = QtWidgets.QVBoxLayout()
        v_main.addLayout(h_cats)
        v_main.addStretch()

        self.statusButtonCheckAll(self)

        return v_main

    def checkAllCategories(self, is_checked):
        sender_parent = self.sender().parent()
        for checkbox in sender_parent.findChildren(QtWidgets.QCheckBox):
            # this will trigger change for each button
            checkbox.setChecked(True) if is_checked else checkbox.setChecked(False)
        self.statusButtonCheckAll(sender_parent)

    def setPreferredCategory(self, checkbox):
        text = checkbox.text()
        if not self.parent_name:
            # come from settings tab
            gdb.setCategorySelected(text, checkbox.isChecked())
        self.statusButtonCheckAll(checkbox.parent())

    def statusButtonCheckAll(self, sender_parent):
        all_are_checked = True
        for checkbox in sender_parent.findChildren(QtWidgets.QCheckBox):
            if not checkbox.isChecked():
                all_are_checked = False
                break
        text = 'Uncheck All' if all_are_checked else 'Check All'
        self.check_all_categories.setText(text)
        self.check_all_categories.setChecked(all_are_checked)

