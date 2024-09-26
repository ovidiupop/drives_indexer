import os

from PyQt5 import QtCore, QtSql
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, QDir

from mymodules import GDBModule
from mymodules.GDBModule import getPreferenceByName
from mymodules.GlobalFunctions import getForbiddenFolders


def percentage(part, whole):
    """calculate percents of progress """
    result = 100 * float(part) / float(whole)
    return int(result)


class WorkerKilledException(Exception):
    pass


# we need this WorkerSignals, because QRunnable hasn't signals
# WorkerSignals is derived from Object and have signals
class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    match_found = QtCore.pyqtSignal()
    directory_changed = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal()
    status_folder_changed = QtCore.pyqtSignal()


class JobRunner(QRunnable):
    signals = WorkerSignals()

    def __init__(self):
        super().__init__()
        self.is_killed = False

        self.con = GDBModule.connection('indexer_connection')
        self.con.open()
        self.extensions = self.getExtensionsList()
        self.forbidden_folders = getForbiddenFolders()
        self.folders_to_index = []
        self.found_files = 0
        self.total_files = 0
        self.checked_files = 0
        self.percentage = 0
        self.folder_id = 0
        self.remove_indexed = True
        self.index_all_types_of_files = False
        self.index_files_without_extension = True
        self.index_hidden_content = int(getPreferenceByName('index_hidden_content'))

    def reInitializeToZero(self):
        self.found_files = 0
        self.checked_files = 0
        self.percentage = 0
        self.folder_id = 0

    @pyqtSlot()
    def run(self):
        try:
            self.reInitializeToZero()
            self.total_files = self.countTotalFiles(self.folders_to_index)

            for folder in self.folders_to_index:
                self.folder_id = self.folderId(folder)
                if self.remove_indexed:
                    self.removeFilesBeforeReindex(self.folder_id)
                self.setStatusFolder(folder, 0)
                self.signals.status_folder_changed.emit()
                self._index(folder)
                self.setStatusFolder(folder, 1)
                self.signals.status_folder_changed.emit()
            self.finishThread()
        except WorkerKilledException:
            pass

    # check if the thread is killed
    def amIKilled(self):
        if self.is_killed:
            self.finishThread()
            raise WorkerKilledException

    def _index(self, path):
        """
        recursive method for indexing files
        """
        self.amIKilled()

        # switch to new directory (root or recursive)
        directory = QtCore.QDir(path)
        directory.setFilter(directory.filter() | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks)
        if self.index_hidden_content:
            directory.setFilter(directory.filter() | QtCore.QDir.Hidden)
        self.signals.directory_changed.emit(path)

        for entry in directory.entryInfoList():
            if entry.isDir():
                dir = QDir(entry.filePath())
                actual_dir_name = dir.dirName()
                if self.folderExists(entry.filePath()) or self.folderIsForbidden(actual_dir_name):
                    continue

                self._index(entry.filePath())

            if entry.isFile():
                self.addFileByExtension(entry, path)

    def countTotalFiles(self, roots):
        """ count the files in directories roots is array of folders
        """
        count = 0
        for root in roots:
            for root_dir, cur_dir, files in os.walk(root, topdown=True):
                dir = QDir(root_dir)
                actual_dir_name = dir.dirName()
                if actual_dir_name not in self.forbidden_folders:
                    count += len(files)
        return count

    def extensionIdForFile(self, entry):
        # suppose the file has no extension
        extension_id = 'no_extension'

        # check if file has any extension
        ext = entry.suffix() or entry.completeSuffix()
        file_ext = ext.lower()
        # extension of file is in usual list's of extensions
        if file_ext in self.extensions.values():
            # is a listed extension; assign it id as extension_id to file
            extension_id = self.extensionId(file_ext)

        # file hasn't extension in usual list (previously checked), but must index all types of files
        elif file_ext and self.index_all_types_of_files and extension_id == 'no_extension':
            # save new extension and get its id and assign to file
            extension_id = self.addNewExtension(file_ext)
            # re-assign usual extensions to indexed to include the newly added extension
            self.reAssignExtensions()
        # file has extension but is not an allowed extension type
        elif file_ext and not self.index_all_types_of_files:
            extension_id = 'not_allowed_extension'

        return extension_id

    def addFileByExtension(self, entry, path):
        self.checked_files += 1
        self.percentage = percentage(self.checked_files, self.total_files)

        # here we get extension_id as number or 'no_extension' or 'not_allowed_extension'
        extension_id = self.extensionIdForFile(entry)

        if extension_id != 'not_allowed_extension':
            if extension_id == 'no_extension':
                if self.index_files_without_extension or self.index_all_types_of_files:
                    extension_id = None  # NULL for database
                else:
                    extension_id = 'no_save'

            # here we have numeral, None or no_save
            # we save numeral or None
            if extension_id != 'no_save':
                item = {'dir': path, 'filename': entry.fileName(), 'size': entry.size(),
                        'extension_id': extension_id, 'folder_id': self.folder_id}
                self.found_files += 1
                self.signals.match_found.emit()
                # insert file in database
                self.addFile(item)

    def getUncategorizedCategoryId(self):
        """Get folder id inside of worker"""
        query = QtSql.QSqlQuery(self.con)
        query.prepare("SELECT id FROM categories WHERE category=:category")
        query.bindValue(':category', 'Uncategorized')
        if query.exec():
            while query.first():
                return query.value(0)

    def addNewExtension(self, ext):
        category_uncategorized = self.getUncategorizedCategoryId()

        query = QtSql.QSqlQuery(self.con)
        query.prepare(
            "INSERT INTO extensions ('extension', 'category_id', 'selected') VALUES (?, ?, ?)")
        query.addBindValue(ext)
        query.addBindValue(category_uncategorized)
        query.addBindValue(1)
        if query.exec():
            return query.lastInsertId()
        else:
            GDBModule.printQueryErr(query, 'addFile')

    def finishThread(self):
        self.con.close()
        self.signals.finished.emit()

    def kill(self):
        self.is_killed = True

    def setExtensions(self, extensions):
        self.extensions = extensions

    def reAssignExtensions(self):
        self.extensions = self.getExtensionsList()

    def getExtensionsList(self):
        extensions = {}
        query = QtSql.QSqlQuery(self.con)
        query.prepare("SELECT id, extension from extensions")
        if query.exec():
            while query.next():
                extensions[query.value('id')] = query.value('extension')
            query.clear()
        return extensions

    def setStatusFolder(self, path, status):
        query = QtSql.QSqlQuery(self.con)
        query.prepare("UPDATE folders SET status=:status WHERE path=:path")
        query.bindValue(':path', path)
        query.bindValue(':status', int(status))
        if query.exec():
            query.clear()
        return True

    def removeFilesBeforeReindex(self, folder_id):
        """ before reindex a folder, remove old indexed files from that folder
        to prevent duplication
        """
        query = QtSql.QSqlQuery(self.con)
        query.prepare("""Delete from files where folder_id=:folder_id""")
        query.bindValue(':folder_id', folder_id)
        if not query.exec():
            GDBModule.printQueryErr(query, 'removeFilesBeforeReindex')

    def extensionId(self, extension):
        for key, value in self.extensions.items():
            if extension == value:
                return key

    def addFile(self, file):
        """Used by indexer thread with own connection
        to add new-found file to database"""
        query = QtSql.QSqlQuery(self.con)
        query.prepare(
            "INSERT INTO files (%s) VALUES (%s)" % (','.join(file.keys()), ','.join("?" * len(file.values()))))
        for binder in file.values():
            query.addBindValue(binder)
        if query.exec():
            return True
        else:
            GDBModule.printQueryErr(query, 'addFile')

    def folderId(self, path):
        """Get folder id inside of worker"""
        query = QtSql.QSqlQuery(self.con)
        query.prepare("""SELECT id
        FROM folders fo	
        LEFT JOIN drives d ON d.serial = fo.drive_id 
        WHERE fo.path=:path AND d.active = 1""")

        query.bindValue(':path', str(path))
        if query.exec():
            while query.first():
                return query.value(0)

    def folderExists(self, folder: str) -> bool:
        """
        :param folder:
        :return:
        check if a folder exists
        """
        query = QtSql.QSqlQuery(self.con)
        query.prepare("SELECT path FROM folders where path=:path limit 1")
        query.bindValue(':path', folder)
        ret = query.exec() and query.first()
        query.clear()
        return ret

    def folderIsForbidden(self, folder):
        return folder.lower() in self.forbidden_folders

