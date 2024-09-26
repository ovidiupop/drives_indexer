from PyQt5 import QtSql
from PyQt5.QtCore import qDebug

from mymodules.GlobalFunctions import *
from mymodules.HumanReadableSize import HumanBytes


def printQueryErr(query, method_name=''):
    """
    :param query:
    :param method_name:
    :return:
    """
    db_err = "Database Error: %s" % query.lastError().databaseText()
    errors = [db_err, query.lastError().text(), query.lastQuery(), query.executedQuery(), method_name]
    print(", ".join(errors))
    list = query.boundValues()
    for k, v in list.items():
        print(k, ": ", v, "\n")


def tables_columns(table: str) -> list:
    """
    :param table:
    :return:
    return column's name of a table
    """
    columns = []
    query = QtSql.QSqlQuery(f"PRAGMA table_info({table})")
    while query.next():
        name = query.record().indexOf("name")
        columns.append(query.value(name))
    return columns


def getAll(table: str, only_field: list = None) -> list:
    """
    :param table:
    :param only_field:
    :return:
    get all records from table
    if only_fields is set, return a list of chosen fields
    ex: ['aif', 'doc', 'docx', 'odt', 'pdf', 'rtf', 'tex', 'txt', 'wpd']
    else return a list of dict with all fields of table
    ex:[{'serial': 'S2R6NX0H703355N', 'name': 'Samsung_SSD_850_EVO_250GB', 'label': 'Samsung_SSD_850_EVO_250GB'},
    {'serial': '4990779F50C0', 'name': 'XPG_EX500', 'label': 'XPG_EX500'}]
    """
    return_array = []
    tables = tables_columns(table) if not only_field else only_field
    fields = ','.join(tables)
    query = QtSql.QSqlQuery(f"SELECT {fields} FROM {table}")
    while query.next():
        row = {} if not only_field else []
        for field in tables:
            if only_field:
                return_array.append(query.value(field))
            else:
                row[field] = query.value(field)
        if not only_field:
            return_array.append(row)
    query.clear()
    return return_array


def foldersOfDrive(serial):
    query = QtSql.QSqlQuery()
    query.prepare('SELECT path FROM folders WHERE drive_id=:drive_id')
    query.bindValue(':drive_id', serial)
    if query.exec():
        folders = []
        while query.next():
            folders.append(query.value(0))
        query.clear()
        return folders


def getExtensionsCategories():
    """
    :param extension:
    :return:
    """
    ext_cat = {}
    query = QtSql.QSqlQuery()
    query.prepare('SELECT extension, category from extensions e'
                  ' left join categories c on c.id=e.category_id')
    if query.exec():
        while query.next():
            ext_cat[query.value(0)] = query.value(1)
    query.clear()
    return ext_cat


def allFolders(hide_inactive=True) -> list:
    """
    :param hide_inactive:
    :return:
    """
    folders = []
    if hide_inactive:
        command = "SELECT fo.path FROM folders fo " \
                  "left join drives d on d.serial=fo.drive_id " \
                  "where d.active=1"
    else:
        command = "SELECT path FROM folders"
    query = QtSql.QSqlQuery(command)
    if query.exec():
        while query.next():
            folders.append(query.value('path'))
        query.clear()
        return folders


def getExtensionsForCategoryId(category: int) -> list:
    """
    :param category:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare('SELECT extension from extensions WHERE category_id=:category_id')
    query.bindValue(':category_id', category)
    if query.exec():
        ext = []
        while query.next():
            ext.append(query.value(0))
        query.clear()
        return ext


def getExtensionsForCategories(categories: list) -> list:
    """
    :param categories:
    :return:
    """
    query = QtSql.QSqlQuery()
    placeholder = ','.join("?" * len(categories))
    query.prepare('SELECT extension from extensions WHERE category_id IN (SELECT id from categories where category in '
                  '(%s))' % placeholder)
    for binder in categories:
        query.addBindValue(str(binder))
    if query.exec():
        ext = []
        while query.next():
            ext.append(query.value(0))
        query.clear()
        return ext


def categoryIdByText(category_text: str) -> int:
    """
    :param category_text:
    :return:
    return category ID
    """
    query = QtSql.QSqlQuery()
    query.prepare('SELECT id FROM categories WHERE category=:category')
    query.bindValue(':category', category_text)
    if query.exec():
        query.first()
        ret = query.value('id')
        query.clear()
        return ret


def allCategoriesAreSelected() -> bool:
    """
    :return:
    """
    query = QtSql.QSqlQuery('SELECT selected FROM categories WHERE selected=0')
    found = query.first()
    return not found


def setCategorySelected(category: str, selected: int) -> bool:
    """
    :param category:
    :param selected:
    :return:
    set category selected and also if success set selected for related extensions
    """
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE categories SET selected=:selected WHERE category=:category")
    query.bindValue(':selected', int(selected))
    query.bindValue(':category', category)
    if query.exec():
        query.clear()
        return setSelectedExtensionsByCategories()


def setSelectedExtensionsByCategories() -> bool:
    """
    :return:
    """
    query = QtSql.QSqlQuery("update extensions set selected=0")
    query.exec()
    query = QtSql.QSqlQuery("update extensions set selected=1"
                            " where category_id in ("
                            "select c.id from categories c"
                            " left join extensions e on c.id=e.category_id"
                            " where c.selected = 1)")
    ret = query.exec()
    query.clear()
    return ret


def folderExists(folder, serial) -> bool:
    """
    :param folder:
    :param serial:
    :return:
    check if a folder exists
    """
    query = QtSql.QSqlQuery()
    query.prepare("SELECT path FROM folders where path=:path and serial:=serial limit 1")
    query.bindValue(':path', folder)
    query.bindValue(':serial', serial)
    ret = query.exec() and query.first()
    query.clear()
    return ret


def addFolder(folder: str, serial: str) -> bool:
    """
    :param folder:
    :param serial:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare(""" INSERT INTO folders (path, drive_id) VALUES (?,?) """)
    query.addBindValue(folder)
    query.addBindValue(serial)
    if query.exec():
        ret = query.lastInsertId()
        query.clear()
        return ret


def getDriveLabelBySerial(serial: str) -> str:
    """
    :param extension:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("select label from drives where serial=:serial")
    query.bindValue(':serial', serial)
    if query.exec():
        while query.next():
            ret = query.value('label')
            query.clear()
            return ret
    else:
        printQueryErr(query, 'labelBySerial')


def deleteFoldersDB(paths: list, labels: list) -> bool:
    """
    :param paths:
    :param labels:
    :return:
    """
    query = QtSql.QSqlQuery()
    for ind, path in enumerate(paths):
        label = labels[ind]
        folder_id = folderId(path, label)
        query.prepare("""Delete from folders where id=:id""")
        query.bindValue(':id', folder_id)
        if query.exec():
            deleteFilesDB(folder_id)
        else:
            printQueryErr(query, 'deleteFoldersDB')
            return False
    query.clear()
    return True


def deleteFilesDB(folder_id: int) -> bool:
    """
    :param folder_id:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("""Delete from files where folder_id=:folder_id""")
    query.bindValue(':folder_id', folder_id)
    if query.exec():
        query.clear()
        return True
    else:
        printQueryErr(query, 'deleteFilesDB')


def cleanRemovedDuplicates(directory: str, filename: str) -> bool:
    """
    :param directory:
    :param filename:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("""Delete from files where dir=:dir AND filename=:filename""")
    query.bindValue(':dir', directory)
    query.bindValue(':filename', filename)
    if query.exec():
        query.clear()
        return True
    else:
        printQueryErr(query, 'cleanRemovedDuplicates')


def extensionId(extension: str) -> int:
    """
    :param extension:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("select id from extensions where extension=:extension")
    query.bindValue(':extension', extension)
    if query.exec():
        while query.next():
            ret = query.value('id')
            query.clear()
            return ret
    else:
        printQueryErr(query, 'extensionId')


def folderId(path: str, label: str) -> int:
    """
    :param path:
    :param label:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("""
        SELECT id FROM folders fo 
        LEFT JOIN drives d ON d.serial = fo.drive_id 
        WHERE fo.path=:path 
        AND d.label=:label
        """)

    query.bindValue(':path', path)
    query.bindValue(':label', label)
    if query.exec():
        while query.next():
            folder_id = query.value(0)
            query.clear()
            return folder_id
    else:
        printQueryErr(query, 'folderId')


def extensionsToInt(extensions_list_string: list) -> list:
    """
    :param extensions_list_string:
    :return:
    get a list of string and return a list of integers (IDS)
    """
    query = QtSql.QSqlQuery()
    placeholder = ','.join("?" * len(extensions_list_string))
    query.prepare('SELECT id FROM extensions WHERE extension IN (%s)' % placeholder)
    for binder in extensions_list_string:
        query.addBindValue(str(binder))
    if query.exec():
        ext = []
        while query.next():
            ext.append(query.value(0))
        query.clear()
        return ext
    else:
        printQueryErr(query, 'extensionsToInt')
        qDebug(query.lastQuery())


def extensionsIdNameDict(extensions_name_list: list) -> dict:
    """
    :param extensions_name_list:
    :return:
    return a dict of extensions key=id, value=extension
    """
    query = QtSql.QSqlQuery()
    placeholder = ','.join("?" * len(extensions_name_list))
    query.prepare('SELECT id, extension FROM extensions WHERE extension IN (%s)' % placeholder)
    for binder in extensions_name_list:
        query.addBindValue(str(binder))
    if query.exec():
        extensions = {}
        while query.next():
            extensions[query.value(0)] = query.value(1)
        query.clear()
        return extensions


def findFiles(search_term: str, extensions: list) -> list:
    """
    :param search_term:
    :param extensions:
    :return:
    search for a term
    """
    extensions_list_ids = extensionsToInt(extensions) or []
    placeholder = ','.join("?" * len(extensions_list_ids))
    query = QtSql.QSqlQuery()
    # if len(extensions_list_ids) > 0:
    query.prepare("select f.dir, f.filename, f.size, e.extension, d.label "
                  "from files f "
                  "left join extensions e on e.id=f.extension_id "
                  "left join folders fo on fo.id=f.folder_id "
                  "left join drives d on d.serial=fo.drive_id "
                  "where (f.extension_id in (%s) or f.extension_id is null) and (f.dir like ? or f.filename like ?)" % placeholder)
    for binder in extensions_list_ids:
        query.addBindValue(binder)
    query.addBindValue("%" + search_term + "%")
    query.addBindValue("%" + search_term + "%")

    if query.exec():
        results = []
        while query.next():
            item = [
                query.value('dir'),
                query.value('filename'),
                query.value('size'),
                query.value('extension'),
                query.value('label')
            ]
            results.append(item)
        query.clear()
        return results


def findDuplicates():
    query = QtSql.QSqlQuery()
    query.prepare("""WITH cte AS (
        SELECT f.dir, f.filename, f.size, e.extension, d.label, count(*) as Occurrence
        FROM files f 
        LEFT JOIN extensions e on e.id=f.extension_id
        LEFT JOIN folders fo on fo.id=f.folder_id
        LEFT JOIN drives d on d.serial=fo.drive_id
        GROUP BY f.size, f.filename
        HAVING COUNT(*) > 1
        )
        SELECT f.dir, f.filename, f.size, e.extension, d.label
        FROM  files f
            INNER JOIN cte ON cte.filename = f.filename AND cte.size = f.size
            LEFT JOIN extensions e on e.id=f.extension_id
            LEFT JOIN folders fo on fo.id=f.folder_id
            LEFT JOIN drives d on d.serial=fo.drive_id
        ORDER BY f.size DESC""")

    if query.exec():
        results = []
        while query.next():
            item = [
                query.value('dir'),
                query.value('filename'),
                query.value('size'),
                query.value('extension'),
                query.value('label'),
                0
            ]
            results.append(item)
        query.clear()
        return results


def findDuplicatesBySize():
    query = QtSql.QSqlQuery()
    query.prepare("""WITH cte AS (
        SELECT f.dir, f.filename, f.size, e.extension, d.label, count(*) as Occurrence
        FROM files f 
            LEFT JOIN extensions e on e.id=f.extension_id
            LEFT JOIN folders fo on fo.id=f.folder_id
            LEFT JOIN drives d on d.serial=fo.drive_id
        WHERE d.active = 1
        GROUP BY f.size, f.filename
        HAVING COUNT(*) > 1
        )
        SELECT f.dir, f.filename, f.size, e.extension, d.label
        FROM  files f
            INNER JOIN cte ON cte.size = f.size
            LEFT JOIN extensions e on e.id=f.extension_id
            LEFT JOIN folders fo on fo.id=f.folder_id
            LEFT JOIN drives d on d.serial=fo.drive_id
        WHERE d.active = 1
        ORDER BY f.size DESC""")

    if query.exec():
        results = []
        while query.next():
            item = [
                query.value('dir'),
                query.value('filename'),
                query.value('size'),
                query.value('extension'),
                query.value('label'),
                0
            ]
            results.append(item)
        query.clear()
        return results


def setDrivesActive(drives: list) -> None:
    """
    :param drives:
    """
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE drives SET active=0, path='unmounted'")
    if query.exec():
        for drive in drives:
            query.prepare('UPDATE drives SET active=1, path=:path WHERE serial=:serial')
            query.bindValue(':path', drive['path'])
            query.bindValue(':serial', drive['serial'])
            query.exec()
    query.clear()


def extensionExists(extension: str) -> bool:
    """
    :param extension:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("SELECT extension FROM extensions WHERE extension=:extension")
    query.bindValue(":extension", str(extension))
    ret = query.exec() and query.first()
    query.clear()
    return ret


def addNewExtension(extension: str, category_id: int) -> bool:
    """
    :param extension:
    :param category_id:
    :return:
    """
    if not extension or extensionExists(extension):
        return False
    query = QtSql.QSqlQuery()
    query.prepare(""" INSERT INTO extensions (extension, category_id) VALUES (?, ?)""")
    query.addBindValue(extension)
    query.addBindValue(category_id)
    if query.exec():
        ret = query.lastInsertId()
        query.clear()
        return ret


def removeExtensions(extensions: list) -> bool:
    """
    :param extensions:
    :return:
    """
    query = QtSql.QSqlQuery()
    exts_id = extensionsToInt(extensions)
    # clear indexed files with extension
    placeholder = ','.join("?" * len(exts_id))
    query.prepare('DELETE FROM files WHERE extension_id IN (%s)' % placeholder)
    for binder in exts_id:
        query.addBindValue(str(binder))
    if query.exec():
        # delete extension itself
        query.prepare('DELETE FROM extensions WHERE id IN (%s)' % placeholder)
        for binder in exts_id:
            query.addBindValue(str(binder))
        ret = query.exec()
        query.clear()
        return ret
    query.clear()
    return False


def moveExtensions(category_id: int, extensions: list) -> bool:
    """
    :param extensions:
    :return:
    """
    query = QtSql.QSqlQuery()
    extension_ids = extensionsToInt(extensions)
    for extension_id in extension_ids:
        query.prepare("UPDATE extensions SET category_id=:category_id WHERE id=:id")
        query.bindValue(':category_id', category_id)
        query.bindValue(':id', extension_id)
        if query.exec():
            query.clear()
        else:
            return False
    return True


def getDriveByPath(drive_path: str) -> str:
    """
    :param drive_path:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("SELECT serial FROM drives WHERE path=:path")
    query.bindValue(":path", drive_path)
    if query.exec():
        if query.first():
            ret = query.value('serial')
            query.clear()
            return ret
        else:
            print(f"No drive found with the path: {drive_path}")
            return None
    else:
        print(f"Error executing SQL query: {query.lastError().text()}")
        return None



# partition_path = /dev/nvme0n1p1
# return /dev/nvme0n1
def getDriveByPartitionPath(partition_path: str) -> str:
    try:
        # We use lsblk to get information about the device and its partitions
        result = subprocess.run(['lsblk', '-npo', 'TYPE,NAME,PKNAME', partition_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing lsblk command: {result.stderr}")
            return None

        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 3 and parts[0] == 'part':
                drive_path = f"{parts[2]}"
                break
        else:
            print(f"Could not determine the drive for partition: {partition_path}")
            return None

        # Query the database to get the drive's serial
        return getDriveByPath(drive_path)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None



def driveSerialExists(serial: str) -> bool:
    """
    :param serial:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("SELECT * FROM drives WHERE serial=:serial")
    query.bindValue(":serial", str(serial))
    if query.exec():
        ret = query.first()
        query.clear()
        return ret
    return False


def driveSerialIsMounted(serial: str) -> bool:
    """
    :param serial:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("SELECT * FROM drives WHERE serial=:serial and active=1")
    query.bindValue(":serial", str(serial))
    if query.exec():
        ret = query.first()
        query.clear()
        return ret
    return False


def isDriveActiveByLabel(label: str) -> bool:
    """
    :param serial:
    :return:
    """
    query = QtSql.QSqlQuery()
    query.prepare("SELECT * FROM drives WHERE label=:label and active=1")
    query.bindValue(":label", str(label))
    if query.exec():
        ret = query.first()
        query.clear()
        return ret
    return False


def getCategoryId(category):
    query = QtSql.QSqlQuery()
    query.prepare("SELECT id FROM categories WHERE category=:category")
    query.bindValue(":category", category)
    if query.exec():
        if query.first():
            return query.value('id')
    return False


def dummyDataResult():
    results = []
    term = 'index'
    query = QtSql.QSqlQuery("select dir, filename, size, extension_id, folder_id from files "
                            "where filename like '%index%'")
    while query.next():
        item = [
            query.value('dir'),
            query.value('filename'),
            query.value('size'),
            query.value('extension_id'),
            query.value('folder_id')
        ]
        results.append(item)
    return results


def setPreferenceById(id, value):
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE preferences SET value=:value WHERE id=:id")
    query.bindValue(':value', value)
    query.bindValue(':id', id)
    if query.exec():
        query.clear()
    return True


def setPreferenceByName(name, value):
    query = QtSql.QSqlQuery()
    query.prepare("UPDATE preferences SET value=:value WHERE name=:name")
    query.bindValue(':value', value)
    query.bindValue(':name', name)
    if query.exec():
        query.clear()
    return True


def getPreferenceByName(name):
    query = QtSql.QSqlQuery()
    query.prepare("SELECT value FROM preferences WHERE name=:name")
    query.bindValue(":name", str(name))
    if query.exec():
        query.first()
        ret = query.value('value')
        query.clear()
        return ret


def getPreferenceNameById(id):
    query = QtSql.QSqlQuery()
    query.prepare("SELECT name FROM preferences WHERE id=:id")
    query.bindValue(":id", id)
    if query.exec():
        query.first()
        ret = query.value('name')
        query.clear()
        return ret


def countFiles():
    query = QtSql.QSqlQuery()
    query.prepare("SELECT COUNT(id) FROM files")
    if query.exec():
        while query.first():
            return query.value(0)


def getUsedExtensions():
    result = []
    query = QtSql.QSqlQuery()
    query.prepare("SELECT c.category, coalesce(e.extension, 'no_extension') AS extension, "
                  "SUM(CASE WHEN f.extension_id is null THEN 1 ELSE 0 END) AS [no_extension], "
                  "COUNT(f.extension_id) AS [with_extension] "
                  "FROM files f "
                  "LEFT JOIN extensions e ON f.extension_id=e.id "
                  "LEFT JOIN categories c ON e.category_id=c.id "
                  "GROUP BY extension_id ORDER BY with_extension DESC")
    if query.exec():
        while query.next():
            if query.value('with_extension') != 0:
                result.append([query.value('category'), query.value('extension'), query.value('with_extension')])
            else:
                result.append([query.value('category'), query.value('extension'), query.value('no_extension')])
        query.clear()
    return result


# return list with files for each category
# [[category, files], [category, files]]
def categoryAndFiles():
    result = []
    query = QtSql.QSqlQuery()
    query.prepare("SELECT c.category, COUNT(f.extension_id) as files "
                  "FROM files f "
                  "LEFT JOIN extensions e ON f.extension_id=e.id "
                  "LEFT JOIN categories c ON e.category_id=c.id "
                  "WHERE e.category_id NOT NULL "
                  "GROUP BY category ORDER BY category ASC")
    if query.exec():
        while query.next():
            result.append([query.value('category'), query.value('files')])
        query.clear()
    return result


def filesOnDrive():
    result = []
    query = QtSql.QSqlQuery()
    query.prepare("SELECT d.label as drive, COUNT(f.id) as filesOnDrive, d.active, d.size "
                  "FROM files f "
                  "LEFT JOIN folders fo ON f.folder_id=fo.id "
                  "LEFT JOIN drives d on d.serial=fo.drive_id "
                  "GROUP BY fo.drive_id "
                  "ORDER BY filesOnDrive DESC")
    if query.exec():
        while query.next():
            result.append(
                [query.value('drive'), query.value('filesOnDrive'), query.value('active'), query.value('size')])
        query.clear()
    return result


def connection(name: str):
    """
    :param name:
    :return:
    """
    db = QtSql.QSqlDatabase.addDatabase(DATABASE_DRIVER, name)
    db.setDatabaseName(getDatabaseLocation())
    return db


class GDatabase:
    def __init__(self):
        super().__init__()
        local_path = getAppLocation()
        if not QDir(local_path).exists():
            QDir().mkdir(local_path)
        database_path = getDatabaseLocation()
        self.con = QtSql.QSqlDatabase.addDatabase(DATABASE_DRIVER)
        self.con.setDatabaseName(database_path)
        self.required_tables = REQUIRED_TABLES
        self.categories = CATEGORIES
        self.preferences = PREFERENCES
        self.default_extensions = default_extensions
        self.checkDatabaseConnection()
        self.tablesExists()

    def checkDatabaseConnection(self):
        if not self.con.open():
            QtWidgets.QMessageBox.critical(
                None, 'DB Connection Error',
                'Could not open database: '
                f'{self.con.lastError().databaseText()}')
            sys.exit(1)

    def tablesExists(self):
        required_tables = self.required_tables
        missing_tables = required_tables - set(self.con.tables())
        if missing_tables:
            self.addTablesDatabase()

    def addTablesDatabase(self):
        query = QtSql.QSqlQuery()
        commands = [
            'DROP TABLE IF EXISTS drivers_db',
            'DROP TABLE IF EXISTS databases',
            'DROP TABLE IF EXISTS categories',
            'DROP TABLE IF EXISTS drives',
            'DROP TABLE IF EXISTS folders',
            'DROP TABLE IF EXISTS extensions',
            'DROP TABLE IF EXISTS files',
            'DROP TABLE IF EXISTS preferences',

            'CREATE TABLE categories('
            '   id INTEGER PRIMARY KEY, '
            '   category VARCHAR(30) NOT NULL, '
            '   icon VARCHAR(30) NOT NULL, '
            '   selected INT NOT NULL DEFAULT 1)',

            'CREATE TABLE drives('
            '   serial TEXT PRIMARY KEY, '
            '   name VARCHAR(50) NOT NULL, '
            '   label VARCHAR(50) NOT NULL, '
            '   size FLOAT NOT NULL, '
            '   active INTEGER DEFAULT 0, '
            '   path VARCHAR(20) NOT NULL)',

            'CREATE TABLE folders('
            '   id INTEGER PRIMARY KEY, '
            '   path TEXT NOT NULL, '
            '   drive_id TEXT, '
            '   status INTEGER NOT NULL DEFAULT 0, '
            '   FOREIGN KEY(drive_id) REFERENCES drives(serial))',

            'CREATE TABLE extensions('
            '   id INTEGER PRIMARY KEY, '
            '   extension VARCHAR(20) NOT NULL, '
            '   category_id INTEGER NOT NULL, '
            '   selected INTEGER DEFAULT 0, '
            '   FOREIGN KEY(category_id) REFERENCES categories(id))',

            'CREATE TABLE files('
            '   id INTEGER PRIMARY KEY, '
            '   dir TEXT NOT NULL, '
            '   filename TEXT NOT NULL, '
            '   size INTEGER, '
            '   extension_id INTEGER DEFAULT NULL, '
            '   folder_id INTEGER NOT NULL, '
            '   FOREIGN KEY(extension_id) REFERENCES extensions(id), '
            '   FOREIGN KEY(folder_id) REFERENCES folders(id))',

            'CREATE TABLE preferences('
            '   id INTEGER PRIMARY KEY, '
            '   name VARCHAR(50) NOT NULL, '
            '   description TEXT, '
            '   value TEXT NOT NULL, '
            '   original VARCHAR(50) NOT NULL, '
            '   type VARCHAR(10) NOT NULL, '
            '   editable INT NOT NULL)',
        ]

        # each query must be prepared before execution
        for command in commands:
            query = QtSql.QSqlQuery()
            query.prepare(f"""{command};""")
            if not query.exec():
                print(f"""Error running {command} command""")

        # check if we have all tables created
        required_tables = self.required_tables
        missing_tables = required_tables - set(self.con.tables())
        if missing_tables:
            QtWidgets.QMessageBox.critical(
                None, 'DB Integrity Error',
                'Missing tables, please repair DB: '
                f'{missing_tables}')
            sys.exit(1)

        # populate preferences
        for preference in self.preferences:
            query.prepare("""INSERT INTO preferences (name, description, value, 
            original, type, editable) VALUES (?, ?, ?, ?, ?, ?)""")
            query.addBindValue(preference[0])
            query.addBindValue(preference[1])
            query.addBindValue(preference[2])
            query.addBindValue(preference[3])
            query.addBindValue(preference[4])
            query.addBindValue(preference[5])
            query.exec()

        # populate categories
        for category, icon in self.categories.items():
            query.prepare("""INSERT INTO categories (category, icon) VALUES (?, ?)""")
            query.addBindValue(category)
            query.addBindValue(icon)
            query.exec()

        # populate tables with default values
        # populate extensions
        for extension in self.default_extensions:
            query.prepare("""INSERT INTO extensions (extension, category_id, selected) VALUES (?, ?, ?)""")
            query.addBindValue(extension[0])
            query.addBindValue(extension[1])
            query.addBindValue(extension[2])
            query.exec()

        # check if extension has been populated
        if query.exec("SELECT extension FROM extensions"):
            query.first()
            extension = query.value('extension')
            if not extension:
                QtWidgets.QMessageBox.critical(
                    None, 'DB Integrity Error',
                    'Missing data from extensions')
                sys.exit(1)
