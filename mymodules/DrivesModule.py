from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel

from mymodules import GDBModule as gdb
from mymodules.ComponentsModule import PushButton, TableViewAutoCols
from mymodules.GlobalFunctions import iconForButton, confirmationDialog
from mymodules.ModelsModule import DrivesTableModel, DrivesItemsDelegate, DrivesMapper
from mymodules.SystemModule import SystemClass

COLUMN_SIZE = [0.10, 0.30, 0.20, 0.20, 0.10, 0.10]
COLUMN_SIZE_ID_HIDDEN = [0.10, 0.40, 0.20, 0.20, 0.09, 0.10]


class Drives(QtWidgets.QWidget):
    check_add_button = QtCore.pyqtSignal()
    remove_drive = QtCore.pyqtSignal(str)
    cleaned_dead_drive = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(Drives, self).__init__(parent)

        self.drive_serial_input = QtWidgets.QLineEdit()
        self.drive_serial_input.setDisabled(True)
        self.drive_name_input = QtWidgets.QLineEdit()
        self.drive_name_input.setDisabled(True)
        self.drive_label_input = QtWidgets.QLineEdit()
        self.drive_size_input = QtWidgets.QDoubleSpinBox()
        self.drive_size_input.setRange(0, 2000000)
        self.drive_size_input.setSingleStep(100)
        self.drive_size_input.setSuffix(' GB')
        self.drive_active_input = QtWidgets.QLineEdit()
        self.drive_active_input.setDisabled(True)
        self.add_drive_button = PushButton('Add')
        self.remove_drive_button = PushButton('Remove')
        self.show_id_drive_button = PushButton('Show ID')
        self.show_id_drive_button.setCheckable(True)
        self.show_id_drive_button.setChecked(False)
        self.drive_form_close = QtWidgets.QPushButton()
        self.drive_form_close.setMaximumWidth(30)
        self.combo_active_drives = QtWidgets.QComboBox()
        # self.combo_active_drives.setFixedWidth(330)
        self.refresh_drives_combo = PushButton()
        self.refresh_drives_combo.setIcon(iconForButton('SP_BrowserReload'))

        self.drive_form_close.setIcon(iconForButton('SP_DialogCloseButton'))
        self.add_drive_button.setIcon(iconForButton('SP_DriveHDIcon'))
        self.remove_drive_button.setIcon(iconForButton('SP_TrashIcon'))
        self.show_id_drive_button.setIcon(iconForButton('SP_FileDialogListView'))


class DrivesView(Drives):
    def __init__(self, parent=None):
        super(DrivesView, self).__init__(parent)

        """settings drives section
        """
        self.comboActiveDrives()

        self.drives_table_model = DrivesTableModel()
        # self.drives_table_model.dataChanged.connect(self.validateData)

        self.drives_table_model.select()
        self.drives_table = TableViewAutoCols(None)
        self.drives_table.setColumns(COLUMN_SIZE)
        self.drives_table_model = DrivesTableModel()

        self.drives_table_model.dataChanged.connect(self.validateData)
        self.drives_table_model.select()

        self.drives_table.setModel(self.drives_table_model)
        self.drives_table.setColumnHidden(self.drives_table_model.fieldIndex("serial"), True)
        self.drives_table_model.setTableSorter(self.drives_table_model.fieldIndex('size'), self.drives_table)
        self.drives_table.setModel(self.drives_table_model)
        self.drives_table_model.select()
        self.drives_table.setItemDelegate(DrivesItemsDelegate(self))

        form_drives = QtWidgets.QFormLayout()
        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addWidget(self.drive_form_close)
        self.drive_form_close.clicked.connect(self.closeDrivesForm)
        close_layout.setAlignment(Qt.AlignRight | Qt.AlignTop)

        controls = QHBoxLayout()
        prev_rec = PushButton('Previous')
        prev_rec.setMyIcon(iconForButton('SP_MediaSeekBackward'))
        prev_rec.setTextCenter()
        prev_rec.clicked.connect(lambda: self.drive_mapper.toPrevious())

        next_rec = PushButton("Next")
        next_rec.setMyIcon(iconForButton('SP_MediaSeekForward'), position='right')
        next_rec.setTextCenter()
        next_rec.clicked.connect(lambda: self.drive_mapper.toNext())
        save_rec = PushButton("Save Changes")
        save_rec.setIcon(iconForButton('SP_DialogSaveButton'))
        save_rec.clicked.connect(lambda: self.drive_mapper.submit())

        controls.addWidget(prev_rec)
        controls.addWidget(next_rec)

        self.drives_table.doubleClicked.connect(self.showDriveForm)
        self.drives_table.clicked.connect(self.showDriveForm)
        form_drives.addRow(close_layout)
        form_drives.addRow('Navigate', controls)
        form_drives.addRow(QLabel('Serial'), self.drive_serial_input)
        form_drives.addRow(QLabel('Name'), self.drive_name_input)
        form_drives.addRow(QLabel('Own Label'), self.drive_label_input)
        form_drives.addRow(QLabel('Size (GB)'), self.drive_size_input)
        form_drives.addRow(QLabel('Active'), self.drive_active_input)
        form_drives.addRow('', save_rec)

        self.drive_mapper = DrivesMapper(self)
        self.drive_mapper.model().select()
        self.drive_mapper.toLast()
        self.group_form = QtWidgets.QGroupBox()
        # self.group_form.setMaximumWidth(330)
        self.group_form.setLayout(form_drives)
        self.group_form.hide()

        group_tools_drive = QtWidgets.QGroupBox()
        group_tools_drive.setMaximumWidth(330)

        layout_tab_drives_buttons = QtWidgets.QVBoxLayout()
        group_tools_drive.setLayout(layout_tab_drives_buttons)

        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(self.combo_active_drives)
        hlay.addWidget(self.refresh_drives_combo)
        layout_tab_drives_buttons.addLayout(hlay)
        layout_tab_drives_buttons.addSpacing(20)
        layout_tab_drives_buttons.addWidget(self.add_drive_button)
        layout_tab_drives_buttons.addWidget(self.remove_drive_button)
        layout_tab_drives_buttons.addWidget(self.show_id_drive_button)

        layout_tab_drives_buttons.addWidget(self.group_form)
        layout_tab_drives_buttons.addStretch()

        layout_tab_drives_table = QtWidgets.QVBoxLayout()
        layout_tab_drives_table.addWidget(self.drives_table)

        # for connection with app
        self.layout_tab_drives = QtWidgets.QHBoxLayout()
        self.layout_tab_drives.addWidget(group_tools_drive)
        self.layout_tab_drives.addLayout(layout_tab_drives_table)
        layout_tab_drives_table.addStretch()

        self.myActions()
        self.check_add_button.emit()

    def myActions(self):
        self.add_drive_button.clicked.connect(self.addRowDrive)
        self.remove_drive_button.clicked.connect(self.removeDrive)
        self.show_id_drive_button.clicked.connect(self.toggleIdDrive)
        self.combo_active_drives.currentIndexChanged.connect(self.check_add_button)
        self.check_add_button.connect(self.disableAddButtonForExisting)
        self.refresh_drives_combo.clicked.connect(self.comboActiveDrives)

    def validateData(self):
        pass

    def toggleIdDrive(self):
        self.drives_table.setColumnHidden(self.drives_table_model.fieldIndex("serial"),
                                          not self.show_id_drive_button.isChecked())
        if self.show_id_drive_button.isChecked():
            self.drives_table.setColumns(COLUMN_SIZE)
        else:
            self.drives_table.setColumns(COLUMN_SIZE_ID_HIDDEN)

    def removeDrive(self):
        confirmation_text = f"If you remove drive, related folders and indexed " \
                            f"content will be removed also! <br><br>Do you proceed?"
        confirm = confirmationDialog("Do you remove?", confirmation_text)
        if not confirm:
            return
        selected = self.drives_table.selectedIndexes()
        for index in selected or []:
            # clean also related folders
            serial = self.drives_table.model().data(self.drives_table.model().index(index.row(), 0))
            # emit for folders module, through tabs module
            self.remove_drive.emit(serial)
            self.drives_table_model.removeRow(index.row())
        self.drives_table_model.select()
        self.check_add_button.emit()

    def getSelectedDriveComboData(self):
        mounted_drives = SystemClass().mounted_drives
        c = self.combo_active_drives.currentText()
        parts = c.split(' ')
        serial = parts[-1]
        for drive in mounted_drives:
            if drive['serial'] == serial:
                return {
                    'serial': str(drive['serial']),
                    'name': drive['name'],
                    'label': drive['name'],
                    'size': float(drive['size']),
                    'active': int(1),
                    'path': drive['path']
                }

    def addRowDrive(self):
        drive_model = self.drives_table_model
        new_row = drive_model.record()
        defaults = self.getSelectedDriveComboData()
        for field, value in defaults.items():
            index = drive_model.fieldIndex(field)
            new_row.setValue(index, value)

        inserted = drive_model.insertRecord(-1, new_row)
        if not inserted:
            error = drive_model.lastError().text()
            print(f"Insert Failed: {error}")
        # Select the new row is editable
        drive_model.select()
        self.drive_mapper.toLast()
        self.add_drive_button.setDisabled(True)

    def closeDrivesForm(self):
        self.group_form.hide()

    def showDriveForm(self, drives_table_index):
        self.group_form.show()
        self.drive_mapper.setCurrentIndex(drives_table_index.row())

    def comboActiveDrives(self):
        self.combo_active_drives.clear()
        items = []
        active_drives = SystemClass().mounted_drives
        if active_drives:
            for drive in active_drives:
                item = drive['name']
                item += ' (' + drive['path'] + ') ' + drive['serial']
                items.append(item)
        self.combo_active_drives.addItems(items)

    def disableAddButtonForExisting(self):
        combo_text = self.combo_active_drives.currentText()
        parts = combo_text.split(' ')
        serial = parts[-1]
        self.add_drive_button.setDisabled(gdb.driveSerialExists(serial))
