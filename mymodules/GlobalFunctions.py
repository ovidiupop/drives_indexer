# this class can be only imported
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
import random

from PyQt5 import QtWidgets, QtGui, QtTest
from PyQt5.QtCore import QMimeDatabase, QDir, QStandardPaths
from PyQt5.QtGui import QIcon, QMovie
from PyQt5.QtWidgets import QMessageBox, QTabWidget, QFileDialog, QApplication, QMainWindow, QListWidgetItem

from mymodules import GDBModule as gdb

VERSION = '1.0.0'
ARCHITECTURE = 'amd64'

APP_NAME = 'Drives Indexer'
DATABASE_NAME = 'drive-indexer.sqlite'
DATABASE_DRIVER = 'QSQLITE'

CSV_COLUMN_SEPARATOR = ','
CSV_LINE_SEPARATOR = '\n'
REQUIRED_TABLES = {'drives', 'folders', 'extensions', 'files', 'categories', 'preferences'}
CATEGORIES = {'Audio': ':music.png', 'Compressed': ':compress.png',
              'Disc and media': ':cd.png', 'Data and database': ':database.png',
              'E-mail': ':email.png', 'Executable': ':lightning.png',
              'Font': ':font.png', 'Image': ':image.png',
              'Internet': ':www_page.png', 'Presentation': ':chart_pie.png',
              'Programming': ':page_white_code.png', 'Spreadsheet': ':table_multiple.png',
              'System': ':application_osx_terminal.png', 'Video': ':television.png',
              'Word': ':page_white_word.png', 'Uncategorized': ':uncategorized.png'}

HEADER_SEARCH_RESULTS_TABLE = ['Directory', 'Filename', 'Size', 'Extension', 'Drive']
HEADER_DUPLICATES_TABLE = ['Directory', 'Filename', 'Size', 'Extension', 'Drive', 'Remove']
HEADER_DRIVES_TABLE = {"serial": "Serial Number", "name": "Drive Name", "label": "Own Label", "size": "Size (GB)",
                       "active": "Active", 'path': 'Path'}

HEADER_FOLDERS_TABLE = {"id": "ID", "path": "Folder Path", "drive_id": "On Drive", 'status': 'Status'}

default_extensions = [['aif', 1, 0], ['cda', 1, 0], ['mid', 1, 0], ['midi', 1, 0], ['mp3', 1, 1],
                      ['mpa', 1, 0], ['ogg', 1, 1], ['wav', 1, 0], ['wma', 1, 0], ['wpl', 1, 0],
                      ['7z', 2, 0], ['arj', 2, 0], ['deb', 2, 0], ['pkg', 2, 0], ['rar', 2, 1],
                      ['rpm', 2, 0], ['tar.gz', 2, 0], ['z', 2, 0], ['zip', 2, 1], ['dmg', 3, 0],
                      ['iso', 3, 0], ['toast', 3, 0], ['vcd', 3, 0], ['csv', 4, 1], ['dat', 4, 0],
                      ['db', 4, 1], ['dbf', 4, 0], ['log', 4, 0], ['mdb', 4, 0], ['sav', 4, 0],
                      ['sql', 4, 1], ['tar', 4, 0], ['xml', 4, 1], ['email', 5, 0], ['eml', 5, 0],
                      ['emlx', 5, 0], ['msg', 5, 0], ['oft', 5, 0], ['ost', 5, 0], ['pst', 5, 0],
                      ['vcf', 5, 0], ['apk', 6, 0], ['bat', 6, 0], ['bin', 6, 0], ['cgi', 6, 0],
                      ['com', 6, 0], ['exe', 6, 1], ['gadget', 6, 0], ['jar', 6, 0], ['msi', 6, 1],
                      ['wsf', 6, 0], ['fnt', 7, 0], ['fon', 7, 0], ['otf', 7, 1], ['ttf', 7, 1],
                      ['ai', 8, 1], ['bmp', 8, 0], ['gif', 8, 0], ['ico', 8, 0], ['jpeg', 8, 1],
                      ['jpg', 8, 1], ['png', 8, 1], ['ps', 8, 0], ['psd', 8, 0], ['svg', 8, 0],
                      ['tif', 8, 0], ['tiff', 8, 0], ['asp', 9, 1], ['aspx', 9, 1], ['cer', 9, 0],
                      ['cfm', 9, 0], ['css', 9, 1], ['htm', 9, 0], ['html', 9, 1], ['js', 9, 1],
                      ['jsp', 9, 0], ['part', 9, 0], ['rss', 9, 0], ['xhtml', 9, 0], ['key', 10, 0],
                      ['odp', 10, 0], ['pps', 10, 0], ['ppt', 10, 1], ['pptx', 10, 1], ['c', 11, 0],
                      ['pl', 11, 0], ['class', 11, 0], ['cpp', 11, 0], ['cs', 11, 0], ['h', 11, 1],
                      ['java', 11, 1], ['php', 11, 1], ['py', 11, 1], ['sh', 11, 1], ['swift', 11, 0],
                      ['vb', 11, 0], ['json', 11, 0], ['ods', 12, 1], ['xls', 12, 1], ['xlsm', 12, 1],
                      ['xlsx', 12, 1], ['bak', 13, 0], ['cab', 13, 0], ['cfg', 13, 0], ['cpl', 13, 0],
                      ['cur', 13, 0], ['dll', 13, 0], ['dmp', 13, 0], ['drv', 13, 0], ['icns', 13, 0],
                      ['ini', 13, 0], ['lnk', 13, 0], ['sys', 13, 0], ['tmp', 13, 0], ['3g2', 14, 0],
                      ['3gp', 14, 0], ['avi', 14, 1], ['flv', 14, 0], ['h264', 14, 0], ['m4v', 14, 1],
                      ['mkv', 14, 1], ['mov', 14, 0], ['mp4', 14, 1], ['mpg', 14, 1], ['mpeg', 14, 1],
                      ['rm', 14, 0], ['swf', 14, 0], ['vob', 14, 0], ['wmv', 14, 1], ['srt', 14, 1],
                      ['sub', 14, 1], ['doc', 15, 1], ['docx', 15, 1], ['odt', 15, 1], ['pdf', 15, 1],
                      ['rtf', 15, 0], ['tex', 15, 0], ['txt', 15, 0], ['wpd', 15, 0]]

PREFERENCES = [
    ['header_to_csv', 'Add header to exported csv', '0', '0', 'bool', '1'],
    ['file_dialog_modal', 'File Information is modal', '1', '1', 'bool', '1'],
    ['indexer_autorun', 'Run indexer when new folder is added', '1', '1', 'bool', '1'],
    ['settings_tab_on_top', 'Settings tabs on top', '0', '0', 'bool', '1'],
    ['index_all_types_of_files', 'Index any types of files', '0', '0', 'bool', '1'],
    ['index_files_without_extension', 'Index files without extension', '1', '1', 'bool', '1'],
    ['index_hidden_content', 'Index hidden content', '0', '0', 'bool', '1'],
    ['forbidden_folders', 'Forbidden Folders', 'tmp,temp,cache', 'tmp,temp,cache', 'list', '0'],
    ['window_size', 'Dimension for window when start (width, height)', '1000, 800', '1000, 800', 'str', '0'],
    ['settings_tabs_order', 'Preferred order for settings tabs', 'Folders,Drives,Categories,Extensions,Preferences,Reports',
     'Folders,Drives,Categories,Extensions,Preferences,Reports', 'str', '0'],
]


def randomColor():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    rgb = (r, g, b)
    return rgb
    # return ','.join(str(v) for v in rgb)


def setStatusBarMW(message):
    mw = findMainWindow()
    mw.statusbar.showMessage(message)
    QtTest.QTest.qWait(100)
    return True


def findMainWindow():
    # Global function to find the QMainWindow in application
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None


def getMimeTypeForExtension(extension_name: str) -> str:
    """
    :param extension_name:
    :return:
    """
    mt = QMimeDatabase()
    z = mt.mimeTypeForFile(f'*.{extension_name}')
    return z.iconName()


def getIcon(item: str, size: int = 24) -> object:
    """
    :param item:
    :param size:
    :return:
    get icon for mimes
    if it is missing from theme, will load from resources
    """
    mime_for_extension = getMimeTypeForExtension(item)
    icon = QtGui.QIcon.fromTheme(mime_for_extension)
    if icon.isNull():
        icon = QtGui.QIcon(f':' + mime_for_extension + '.png')
    return icon
    # return icon.pixmap(size)


def formatDictToHuman(d: dict) -> str:
    """
    :param d:
    :return:
    return a string as list from a dict
    """
    lista = []
    for k, v in d.items():
        item = k + ' : ' + v
        lista.append(item)
    human_list = "\n".join(lista)
    return human_list


def putInFile(data: str, filename: str = 'out.txt') -> None:
    """
    :param data:
    :param filename:
    """
    with open(filename, 'w') as f:
        with redirect_stdout(f):
            print(data)


def iconForButton(name: str) -> QIcon:
    """
    :param name:
    :return:
    """
    return QtWidgets.QApplication.style().standardIcon(getattr(QtWidgets.QStyle, name))


def confirmationDialog(title: str, message: str) -> object:
    """
    :param title:
    :param message:
    :return:
    """
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle(title)
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    return msg_box.exec() == QMessageBox.Ok


def tabIndexByName(tab_widget: QTabWidget, tab_name: str) -> int:
    """
    :param tab_widget:
    :param tab_name:
    :return:
    """
    for index in range(tab_widget.count()):
        if tab_name == tab_widget.tabText(index):
            return index


def categoriesList():
    categories = gdb.getAll('categories')
    categories_list = QtWidgets.QListWidget()
    for category in categories:
        icon = QIcon(category['icon'])
        item = QListWidgetItem(icon, category['category'], categories_list)
        categories_list.addItem(item)
    return categories_list


# deprecated
def categoriesCombo():
    categories = gdb.getAll('categories')
    combo = QtWidgets.QComboBox()
    combo.addItem('Categories')
    for item in categories:
        combo.addItem(QIcon(item['icon']), item['category'])
    return combo


def getDatabaseLocation():
    return QDir(getAppLocation()).filePath(DATABASE_NAME)


def getAppLocation():
    return QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)


def getDefaultDir():
    return QStandardPaths.writableLocation(QStandardPaths.HomeLocation)


def exportDataBase():
    sqlite_file = getDatabaseLocation()
    filename_save = getDefaultDir() + os.sep + DATABASE_NAME
    filename, _ = QFileDialog.getSaveFileName(
        None,
        "EXPORT DATABASE",
        filename_save,
        "SQLITE Files (*.sqlite)"
    )
    if filename:
        shutil.copyfile(sqlite_file, filename)
        QtWidgets.QMessageBox.information(None, 'Database Export', 'Exported successfully!')
        return
    pass


def importDataBase():
    confirmation_text = f"Your database will be replaced and all indexed files will be lost!<br><br>Do you proceed?"
    confirm = confirmationDialog("Do you import database?", confirmation_text)
    if not confirm:
        return
    filename = QFileDialog.getOpenFileName(None, "Select database", getDefaultDir(),
                                           filter="SQLITE Files (*.sqlite)")

    if filename[0] and filename[1]:
        if isValidSQLiteDatabase(filename[0]):
            shutil.copyfile(filename[0], getDatabaseLocation())
            QtWidgets.QMessageBox.information(None, 'Database imported',
                                              "Database has been imported!<br><br>Please restart application!")


# https://www.sqlite.org/fileformat2.html#the_database_header
# check if header is correct
def isValidSQLiteDatabase(database_file_path):
    f = open(database_file_path, "rb")
    while b := f.read(15):
        if b.decode('ascii') == 'SQLite format 3':
            return True


def goToFileBrowser(path):
    if sys.platform == 'win32':
        subprocess.Popen(['start', path], shell=True)

    elif sys.platform == 'darwin':
        subprocess.Popen(['open', path])
    else:
        try:
            # xdg-open *should* be supported by recent Gnome, KDE, Xfce
            subprocess.Popen(['xdg-open', path])
        except OSError:
            pass
        # er, think of something else to try


def setPreferenceById(pid, checkbox):
    value = checkbox.isChecked()
    gdb.setPreferenceById(pid, int(value))


def setPreferenceByName(name, value):
    gdb.setPreferenceByName(name, value)


def getPreference(name):
    return gdb.getPreferenceByName(name)


def getForbiddenFolders():
    folders = getPreference('forbidden_folders')
    if folders:
        return folders.split(',')
    return []


def spinner(parent):
    label = QtWidgets.QLabel(parent)
    movie = QMovie(":loader.gif")
    label.setMovie(movie)
    movie.start()
    return label


def getHelp(category):
    helps = {
        'categories': "<!DOCTYPE html><html><body><h1>Categories</h1><p>Sometime is not necessary to find all files but " \
                      "some of specific type.</p><p>Here the categories are involved.</p><p>Each category have a number of " \
                      "specific extensions related to it.</p><p>For example, in Spreadsheet category there are next " \
                      "extensions: ods, xls, xlsm, xlsx. <br>If we wish to find only the files which have one of these " \
                      "extensions, we can limit the search only to Spreadsheet category.<p><p>In the Categories tab you " \
                      "can select the preferred ones. Those which will be automatically used when you search. What you will" \
                      " select here, will save to database.<p><p>In the Search tab, you can refine your categories, " \
                      "checking or unchecking some of them. That selection will be temporary and will not be saved to " \
                      "database.<p></body></html>",

        'drives': "<!DOCTYPE html><html><body><h1>Drives</h1><p>In the Drives tab, you need to set the drives that are " \
                  "connected to the computer as active.</p><p>From the list you select the drive then click Add.<br>The " \
                  "new added drive will be included in the table, and you can set for it your Own Label to easily identify " \
                  "it.</p><p>To edit a field, you have to use the form and to save the new data. You must press Save Changes" \
                  " else the changes will not be saved to database.</p><p>If you connect a new drive to your computer," \
                  " the app will be notified and automatically add the new drive to the drive list. This will be the last" \
                  " one on the list. If you want to index it, it must be added to the table!</p><p>If you disconnect a" \
                  " drive added to the table, it will be marked in the Active column with a red X and removed from the " \
                  "available drives list. Indexed folders belonging to this drive will no longer be visible in the Folder" \
                  " tab until the drive is reconnected, but indexed files will obviously be available for " \
                  "searching.</p><p>If you remove a drive from the table, belonging folders and indexed files will be " \
                  "removed also.</p></body></html>",

        'duplicates': "<!DOCTYPE html><html><body><h1>Duplicates</h1><p>In the Duplicates tab, you can find duplicates "
                      "from indexed files.</p><p>Press the 'Find' button. The duplicates will be identified based on "
                      "the file size and the filename.<br><br>The table will be populated with found duplicated. In the "
                      "last column, you can check the boxes for the duplicates you wish to remove. By default, there "
                      "will be a reference file which will not be checked and the next duplicates will be checked.<br>"
                      "After you selected the instances of the files which you wish to remove, you can export the list "
                      "as csv.</body></html>",

        'extensions': "<!DOCTYPE html><html><body><h1>Extensions</h1><p>Because is useless to index everything, there is a " \
                      "list of extensions for desired files.</p><p>These are grouped by categories.</p><p>By default there" \
                      " are 140 of extensions which will cover most preferred files. But if you will not need to find files " \
                      "related to programming for example, you can remove all the extensions from that category.</p><p>The" \
                      " number of indexed files is related to the number of extensions. If you wish to keep a small" \
                      " database, you can 'clean' unwanted extensions.<br>In this case, the indexed files with those " \
                      "extensions, will be removed from database.</p><p>Or, the other case, if you need to record and find" \
                      " a type of files with an extension which is not in the default list, you can add its extension" \
                      " anytime to the proper category.<br>After you add a new extensions, the indexer will start" \
                      " immediately and will search and reindex all the folders only for that extension and only the " \
                      "folders with connected drives. For the other drives you will have to reindex the entire folders " \
                      "after you will connect the drives.</p><p>If you remove all extensions from a category, the category" \
                      " itself will not be removed but will stay empty and available (for the case you change your " \
                      "mind).</p><p>Adding of new extension is not possible during indexing process!</p></body></html>",

        'folders': "<!DOCTYPE html><html><body><h1>Folders</h1><p>In the Folders tab happen the magic.</p><p>Here you" \
                   " need to select the folders you want to index. Click Add to add a new folder. After you select a " \
                   "folder in the File Manager, it will be added to the list and indexing will start automatically, unless" \
                   " you have changed this behavior in the Preferences tab.</p><p>If you wish to add multiple folders " \
                   "and index them in a single indexing, you have to uncheck 'Run indexer when new folder is added' " \
                   "from Preferences tab.</p><p>If you selected to index a very large folder, there will be a lag of " \
                   "some seconds until will start. You will know that the indexer is working as long as the buttons " \
                   "are disabled and the 'Stop index' button is visible.</p><p>While the files are indexed, you will " \
                   "see the progress in the status bar from any tab (and in the information area under the list in " \
                   "Folders tab).</p><p>If you decide to remove some folders, the indexed content of them will be removed " \
                   "from database, and you will not find anymore any references to them.<br>You can remove more folders " \
                   "at once. Select those folders and click on Remove.<br>If you wish to completely clean your database, " \
                   "you can use Remove All button. This will remove all folders and the files indexed.</p><p>If for any " \
                   "reason you need to reindex one or more folders, you have to select them and then click on Re/Index " \
                   "button. Previous records will be removed and the folders will be re-indexed.</p><p>During the indexing" \
                   " process, all operations which can affect the result will be blocked. You will not be able to " \
                   "add/remove folders, and also you will not be able to remove/add extensions.</p><p>If for any reason" \
                   " you need to stop the indexer while it is indexing, you will have to reindex the folder. In the " \
                   "Status column a red exclamation sign will be shown!</p></body></html>",

        'general': "<!DOCTYPE html><html><body><h1>General</h1><p>If you are like me and have a big collection of old " \
                   "drives where you keep all your history, documents, work, pictures, favorite music and movies, then " \
                   "you never know exactly where to find them when you needs.</p><p>That's why Drives Indexer was created." \
                   " Now, you can find anything in a second!</p><p>How it works?</p><ul><li>Mount your drive in your " \
                   "computer or using an externally USB adapter or a docking station. And yes, you can index also Flash " \
                   "drives! The application will identify your newly added drive when it will be connected to " \
                   "computer.</li><li>In the Drives tab, you have to add each indexable drive. Select it from list and push" \
                   " the Add button.</li><li>Add your desired folders (or the entire drive) in the Folders tab. When you " \
                   "add the folder, the indexer will automatically start to scan your drive and index its files. In the " \
                   "Preferences tab you can set to manually start the indexing.</li></ul><p>Important! If the folder to " \
                   "be scanned is very large or if the drive is idle, will take few moments before it starts! Don't" \
                   " worry!</p><ol><li>You have to index each drive of your collection.<ul><li>Application is set to " \
                   "index by default only the files with most usual extensions, grouped by categories. But also you can " \
                   "add any other extension as you prefer. Or you can set to index anything in the Preferences " \
                   "tab!</li><li>Even if you will have same folders structure on more drives, the application will" \
                   " identify them individual. In this way you will know always the right place where your " \
                   "files are.</li></ul></li><li>You will search for the term which identify your files. The results " \
                   "are displayed in the Search Results Table. Here you can sort them in the way you like.<ul><li>The " \
                   "details of each file is easily to see, some of them having also a preview. Just double-click on the " \
                   "line!</li></ul></li><li>If you wish to export the results in a csv file, you have two " \
                   "options:<ul><li>Export all the results</li><li>Export only selected " \
                   "results</li></ul></li></ol><p>That's all!</p><p>Happy searching!</p></body></html>",

        'other':  "<!DOCTYPE html><html><body><h1>Other</h1><p>The database will be saved in the local folder of " \
                "active user.</p><p>In Linux systems this will be located in ~/.local/share/Drives Indexer</p><p>In " \
                "Windows systems this will be located in C:\\Users\\user\\AppData\\Roaming\\Drives Indexer</p><p>When you import " \
                "a database, the old one is removed, so be cautions! Before import a database, back-up it (export) " \
                "the old one.</p></body></html>",

        'preferences': "<!DOCTYPE html><html><body><h1>Preferences</h1><p>Here you can set some preferences</p><p><ul><li>" \
                       "Add header to exported csv</li></ul>If is checked, in exported csv will be added the header of each " \
                       "column.</p><p><ul><li>File information is modal</li></ul>If is checked, when you double-clicked on " \
                       "a row from search results, you will be able to open only a single file at a time. This will prevent " \
                       "to have a lot of small windows opened which will need then to be closed.<br>But if you need to " \
                       "compare more files, you can uncheck this option.</p><p><ul><li>Run indexer when new folder is " \
                       "added</li></ul>If is checked, when you add a new folder, the indexer will begin instantly. In this " \
                       "case you can add only a single folder at time. If is unchecked, you can add multiple folders, then " \
                       "you have to select them and press the Re/Index button to index all of them!<p><ul><li>Settings " \
                       "tabs on top</li></ul>If is checked, the tabs in the Settings section will be displayed at the top. " \
                       "If is unchecked, the tabs in the Settings section will be displayed on the left.</p><p><ul><li>Index" \
                       " all types of files</li></ul>If is checked, will be indexed all the found files, regardless of the " \
                       "extension they have. The new found extensions will be added to Uncategorized category. If is " \
                       "unchecked, will be indexed only the files having registered extensions. If you previously indexed " \
                       "with checked option, you have to remove the extensions from Uncategorized category. This will remove " \
                       "also files with those extensions, and the next index will avoid them.</p><p><ul><li>Index files " \
                       "without extension</li></ul>If is checked, the files without extensions will also be " \
                       "indexed.</p><p><ul><li>Index hidden content</li></ul>If is checked, the files and folders hidden " \
                       "by system, will be scanned and indexed.</p></body></html>",

        'search': "<!DOCTYPE html><html><body><h1>Search</h1><p>In the Search tab you can find the files you want!</p><p>If " \
                  "you have indexed your folders, enter your search term, press Enter, or click the Search button.</p><p>If " \
                  "you wish to search only for a specific category of files, you can uncheck the rest of categories.</p><p>" \
                  "You can sort results as you wish, clicking on the table's header.</p><p>If some of the results belong to" \
                  " a drive which is not mounted, the name of that drive will be red.</p><p>If the results belong to a " \
                  "mounted drive, with a double click on the table line you can quickly see information about each file. " \
                  "Many files also have preview.</p></body></html>"

        }
    return helps[category]