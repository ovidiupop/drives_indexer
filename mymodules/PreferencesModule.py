from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import ListWidget
from mymodules.GlobalFunctions import setPreferenceById, getForbiddenFolders, setPreferenceByName


class Preferences(QtWidgets.QWidget):
    change_settings_tab_position = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Preferences, self).__init__(parent)
        self.preferences = gdb.getAll('preferences')

        self.forbidden_folders = []
        self.setForbiddenFolders()

        self.label_forbidden_folders = QtWidgets.QLabel('Forbidden Folders')
        self.forbidden_folders_list = ListWidget(self)
        self.forbidden_folders_list.addItems(self.forbidden_folders)
        self.input_new_forbidden_folder = QtWidgets.QLineEdit()
        self.input_new_forbidden_folder.setPlaceholderText('Use only lowercase')
        self.add_new_forbidden_button = QtWidgets.QPushButton('Add Folder')
        self.add_new_forbidden_button.setIcon(QIcon(':folder_add.png'))
        self.remove_forbidden_button = QtWidgets.QPushButton('Remove Folder')
        self.remove_forbidden_button.setIcon(QIcon(':folder_delete.png'))
        self.add_new_forbidden_button.clicked.connect(lambda: self.addNewForbiddenFolder())
        self.remove_forbidden_button.clicked.connect(lambda: self.removeForbiddenFolder())
        self.forbidden_folders_list.currentItemChanged.connect(self.activeButtonsForbiddenFolders)
        self.input_new_forbidden_folder.textChanged.connect(self.activeButtonsForbiddenFolders)
        self.input_new_forbidden_folder.returnPressed.connect(lambda: self.addNewForbiddenFolder())
        self.forbidden_folders_list.delete_key_pressed.connect(lambda: self.removeForbiddenFolder())

        self.activeButtonsForbiddenFolders()

        grid_layout = QtWidgets.QGridLayout()
        for i, preference in enumerate(self.preferences):
            if preference['editable']:
                id = preference['id']
                value = preference['value']
                type = preference['type']
                if type == 'bool':
                    input = QtWidgets.QCheckBox()
                    input.setChecked(int(value))
                    x = input
                    sid = id
                    input.stateChanged.connect(lambda checked, input=x, id=sid: self.setNewPreferences(id, input))
                elif type == 'str':
                    input = QtWidgets.QLineEdit()

                grid_layout.addWidget(input, i, 0)
                desc = QtWidgets.QLabel(preference['description'])
                grid_layout.addWidget(desc, i, 1)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addLayout(grid_layout)
        hlay.addStretch()

        vlay = QtWidgets.QVBoxLayout()
        vlay.addLayout(hlay)
        vlay.addStretch()

        v_forbidden_folders = QtWidgets.QVBoxLayout()
        v_forbidden_folders.addWidget(self.label_forbidden_folders)
        v_forbidden_folders.addWidget(self.forbidden_folders_list)
        v_forbidden_folders.addWidget(self.input_new_forbidden_folder)
        hbuttons = QtWidgets.QHBoxLayout()
        hbuttons.addWidget(self.add_new_forbidden_button)
        hbuttons.addWidget(self.remove_forbidden_button)
        v_forbidden_folders.addLayout(hbuttons)
        v_forbidden_folders.addStretch()

        self.layout_tab_preferences = QtWidgets.QHBoxLayout()
        self.layout_tab_preferences.addLayout(vlay)
        self.layout_tab_preferences.addLayout(v_forbidden_folders)

    def setForbiddenFolders(self):
        self.forbidden_folders = getForbiddenFolders()

    def addNewForbiddenFolder(self):
        new_folder = self.input_new_forbidden_folder.text()
        if new_folder:
            new_folder = new_folder.lower()
            folders = self.forbidden_folders
            if new_folder in folders:
                QtWidgets.QMessageBox.information(self.parent(), 'Exists', f"{new_folder} is already forbidden!<br>")
                return None
            folders.append(new_folder)
            fbd_folders = ','.join(folders)
            setPreferenceByName('forbidden_folders', fbd_folders)
            self.forbidden_folders_list.clear()
            self.input_new_forbidden_folder.clear()
            self.forbidden_folders_list.addItems(folders)

    def removeForbiddenFolder(self):
        if len(self.forbidden_folders):
            cit = self.forbidden_folders_list.currentItem()
            if cit:
                selected = cit.text()
                if selected:
                    new_folders = []
                    for folder in self.forbidden_folders:
                        if folder != selected:
                            new_folders.append(folder)
                    folders = ','.join(new_folders)
                    setPreferenceByName('forbidden_folders', folders)
                    self.forbidden_folders = getForbiddenFolders()
                    self.forbidden_folders_list.clear()
                    self.forbidden_folders_list.addItems(new_folders)

    def setNewPreferences(self, id, checkbox):
        setPreferenceById(id, checkbox)
        name = gdb.getPreferenceNameById(id)
        if name == 'settings_tab_on_top':
            self.change_settings_tab_position.emit()

    def activeButtonsForbiddenFolders(self):
        btn_remove_enabled = len(self.forbidden_folders) and self.forbidden_folders_list.currentItem() \
                             and self.forbidden_folders_list.currentItem().text()
        self.remove_forbidden_button.setEnabled(bool(btn_remove_enabled))
        btn_add_enabled = len(self.input_new_forbidden_folder.text())
        self.add_new_forbidden_button.setEnabled(bool(btn_add_enabled))
