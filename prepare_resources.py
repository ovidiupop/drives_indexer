import os
import pathlib
from PyQt5 import QtCore


def prepareQrcFile(resource_file_name='resources.qrc', path_to_resources='/images'):
    current_directory = str(pathlib.Path(__file__).parent.absolute())
    images_folder = current_directory + path_to_resources
    resource_file_path = current_directory + '/' + resource_file_name
    path = QtCore.QDir(images_folder)
    with open(resource_file_path, 'w') as f:
        f.write('<RCC>\n')
        f.write('\t<qresource>\n')
        recursiveFolders(path, f)
        f.write('\t</qresource>\n')
        f.write('</RCC>')


def recursiveFolders(path, f):
    directory = QtCore.QDir(path)
    current_directory = str(pathlib.Path(__file__).parent.absolute())
    file_for_path = directory.path().replace(current_directory, '')
    directory.setFilter(directory.filter() | QtCore.QDir.NoDotAndDotDot | QtCore.QDir.NoSymLinks)

    for entry in directory.entryInfoList():
        if entry.isFile():
            filename = entry.fileName()
            file = file_for_path + "/" + filename
            f.write(f'\t\t<file alias="{filename}">{file}</file>\n')
        if entry.isDir():
            recursiveFolders(entry.filePath(), f)


prepareQrcFile()