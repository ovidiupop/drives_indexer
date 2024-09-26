from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QAction, QShortcut

from mymodules.GlobalFunctions import exportDataBase, importDataBase, tabIndexByName, VERSION
from mymodules.HelpContent import HelpContent


class IMenu(QtWidgets.QWidget):
    def __init__(self, parent):
        super(IMenu, self).__init__(parent)
        self.tabs_view = self.parent().tabs_view
        self.menu_bar = self.parent().menuBar()

        self._createActions()
        self._createMenuBar()
        self._connectActions()
        # self._createShortCuts()

    def _createActions(self):
        # # Creating action using the first constructor
        self.export_all_action = QAction(QIcon(":all-results.svg"), "&All Search Results", self)
        self.export_all_action.setShortcut("Ctrl+E")
        self.export_all_action.setShortcutVisibleInContextMenu(True)

        self.export_selected_action = QAction(QIcon(":selected-results.svg"), "&Selected Search Results", self)
        self.export_selected_action.setShortcut("Ctrl+Shift+E")
        self.export_selected_action.setShortcutVisibleInContextMenu(True)

        # # Creating action using the first constructor
        self.export_database_action = QAction(QIcon(":export.svg"), "&Export database", self)
        self.export_database_action.setShortcut("Ctrl+D")
        self.export_database_action.setShortcutVisibleInContextMenu(True)

        self.import_database_action = QAction(QIcon(":import.svg"), "&Import database", self)
        self.import_database_action.setShortcut("Ctrl+Shift+D")
        self.import_database_action.setShortcutVisibleInContextMenu(True)

        self.exit_action = QAction(QIcon(":application-exit.svg"), "E&xit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.setShortcutVisibleInContextMenu(True)

        self.settings_drives_action = QAction(QIcon(":drives.svg"), "&Drives", self)
        self.settings_drives_action.setShortcut("Ctrl+Alt+D")
        self.settings_drives_action.setShortcutVisibleInContextMenu(True)

        self.settings_categories_action = QAction(QIcon(":categories.svg"), "&Categories", self)
        self.settings_categories_action.setShortcut("Ctrl+Alt+C")
        self.settings_categories_action.setShortcutVisibleInContextMenu(True)

        self.settings_folders_action = QAction(QIcon(":folders.svg"), "&Folders", self)
        self.settings_folders_action.setShortcut("Ctrl+Alt+F")
        self.settings_folders_action.setShortcutVisibleInContextMenu(True)

        self.settings_extensions_actions = QAction(QIcon(":extensions.svg"), "&Extensions", self)
        self.settings_extensions_actions.setShortcut("Ctrl+Alt+E")
        self.settings_extensions_actions.setShortcutVisibleInContextMenu(True)

        self.settings_preferences_actions = QAction(QIcon(":preferences.svg"), "&Preferences", self)
        self.settings_preferences_actions.setShortcut("Ctrl+Alt+P")
        self.settings_preferences_actions.setShortcutVisibleInContextMenu(True)

        self.help_content_action = QAction(QIcon(":help-contents.svg"), "&Help Content", self)
        self.help_content_action.setShortcut("Ctrl+H")
        self.help_content_action.setShortcutVisibleInContextMenu(True)

        self.about_action = QAction(QIcon(":help-about.svg"), "&About", self)
        self.about_action.setShortcut("Ctrl+Shift+H")
        self.about_action.setShortcutVisibleInContextMenu(True)

    def _connectActions(self):
        # Connect File actions
        self.export_all_action.triggered.connect(self.exportAllResults)
        self.export_selected_action.triggered.connect(self.exportSelectedResults)
        self.export_database_action.triggered.connect(exportDataBase)
        self.import_database_action.triggered.connect(importDataBase)
        self.exit_action.triggered.connect(self.parent().close)
        # Connect Settings actions
        self.settings_drives_action.triggered.connect(lambda: self.switchTab('Drives'))
        self.settings_categories_action.triggered.connect(lambda: self.switchTab('Categories'))
        self.settings_folders_action.triggered.connect(lambda: self.switchTab('Folders'))
        self.settings_extensions_actions.triggered.connect(lambda: self.switchTab('Extensions'))
        self.settings_preferences_actions.triggered.connect(lambda: self.switchTab('Preferences'))
        # Connect Help actions
        self.help_content_action.triggered.connect(self.helpContent)
        self.about_action.triggered.connect(self.about)

    def _createMenuBar(self):

        self.file_menu = self.menu_bar.addMenu("&File")
        self.export_menu = self.file_menu.addMenu(QIcon(":export.svg"), "CSV &Export")
        self.export_menu.addAction(self.export_all_action)
        self.export_menu.addAction(self.export_selected_action)
        self.file_menu.addSeparator()
        self.export_database_menu = self.file_menu.addMenu(QIcon(":database.svg"), "&Database")
        self.export_database_menu.addAction(self.export_database_action)
        self.export_database_menu.addAction(self.import_database_action)

        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.settings_menu = self.menu_bar.addMenu("&Settings")
        self.settings_menu.addAction(self.settings_drives_action)
        self.settings_menu.addAction(self.settings_categories_action)
        self.settings_menu.addAction(self.settings_folders_action)
        self.settings_menu.addAction(self.settings_extensions_actions)
        self.settings_menu.addAction(self.settings_preferences_actions)

        self.help_menu = self.menu_bar.addMenu('&Help')
        self.help_menu.addAction(self.help_content_action)
        self.help_menu.addAction(self.about_action)

    def _createShortCuts(self):
        self.export_all_results = QShortcut(QKeySequence("Ctrl+E"), self)
        self.export_all_results.activated.connect(self.exportAllResults)
        self.export_selected_results = QShortcut(QKeySequence("Ctrl+Shift+E"), self)
        self.export_selected_results.activated.connect(self.exportSelectedResults)

    def exportAllResults(self):
        self.tabs_view.search.export_all_results_signal.emit()

    def exportSelectedResults(self):
        self.tabs_view.search.export_selected_results_signal.emit()

    def switchTab(self, tab):
        tabs_main_index = tabIndexByName(self.tabs_view.tabs_main, "Settings")
        self.tabs_view.tabs_main.setCurrentIndex(tabs_main_index)
        tab_settings_index = tabIndexByName(self.tabs_view.tabs_settings, tab)
        self.tabs_view.tabs_settings.setCurrentIndex(tab_settings_index)

    def helpContent(self):
        HelpContent(self)

    def about(self):
        QtWidgets.QMessageBox.about(self, 'About Drives Indexer',
                                    f"<h4>Find all your files in a single place</h4>v.{VERSION}<br><br>"
                                    "Index your entire drive collection in one place and find anything in a "
                                    "second!<br><br> "
                                    "© 2022 Ovidiu Pop")

