from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QUrl, QSize, QFileInfo
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTextEdit

from mymodules.GlobalFunctions import goToFileBrowser, HEADER_SEARCH_RESULTS_TABLE, findMainWindow, getPreference
from mymodules.HumanReadableSize import HumanBytes
from mymodules.SystemModule import getFileEncoding, getFileData


class FileDetailDialog(QtWidgets.QDialog):

    resized = QtCore.pyqtSignal()

    def __init__(self, category, data, parent=None):
        super(FileDetailDialog, self).__init__(parent)
        self.setWindowTitle('File Detail')
        is_modal = int(getPreference('file_dialog_modal'))
        if is_modal:
            self.setModal(True)

        # needed for media player
        self.can_close = True
        self.mw = findMainWindow()

        # assign each column's value to class attribute
        [setattr(self, column.lower(), data[index]) for index, column in enumerate(HEADER_SEARCH_RESULTS_TABLE)]

        self.file_path = self.directory + '/' + self.filename
        info = QFileInfo(self.file_path)
        self.file_data = getFileData(self.file_path)
        self.layout = QtWidgets.QVBoxLayout()
        self.file_info_widget = DetailsFileWidget(category, self.drive, info, self)
        self.dispatcher(category)

        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(14)
        self.layout.addWidget(self.status_bar)
        self.status_bar.showMessage(self.file_data)

        self.setLayout(self.layout)
        self.show()

    def resizeEvent(self, event):
        self.resized.emit()

    def dispatcher(self, category):
        self.can_close = True
        if category == 'Video' and self.extension not in ['srt', 'sub']:
            self.can_close = False
            # add minimize, maximize and the other flags for manipulating window
            self.setWindowFlags(Qt.Window)
            self.setMinimumSize(600, 800)
            self.player = MediaPlayer('Video', self.file_path, self)
        elif category == 'Audio':
            self.setMaximumHeight(200)
            self.can_close = False
            self.player = MediaPlayer('Audio', self.file_path, self)
        elif category == 'Image':
            self.setWindowFlags(Qt.Window)
            WImage(self.file_path, self)
        else:
            encoding = getFileEncoding(self.file_path)
            self.setWindowFlags(Qt.Window)
            if not Editor(self.file_path, encoding, self):
                self.setMaximumHeight(130)

        self.mw.statusbar.showMessage('')

    def closeEvent(self, ev):
        if self.can_close:
            super(FileDetailDialog, self).closeEvent(ev)
        else:
            ev.ignore()
            # stop media player before close the dialog window
            self.player.media_player.stop()
            self.can_close = True
            super(FileDetailDialog, self).closeEvent(ev)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Escape:
            if self.can_close:
                super(FileDetailDialog, self).keyPressEvent(ev)
            else:
                ev.ignore()
                # stop media player before close the dialog window
                self.player.media_player.stop()
                self.can_close = True
                super(FileDetailDialog, self).keyPressEvent(ev)


class DetailsFileWidget(QtWidgets.QWidget):
    def __init__(self, category: str, drive: str, file: QFileInfo, parent=None):
        super(DetailsFileWidget, self).__init__(parent)

        self.layout_info = QtWidgets.QVBoxLayout()

        info_group = QtWidgets.QGroupBox()
        info_group.setMaximumHeight(130)
        info_group.setLayout(self.layout_info)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout_top_row = QtWidgets.QHBoxLayout()
        self.layout_cat_and_drive = QtWidgets.QVBoxLayout()
        self.layout_folder_go = QtWidgets.QVBoxLayout()
        self.layout_top_row.addLayout(self.layout_cat_and_drive)
        self.layout_top_row.addLayout(self.layout_folder_go)
        self.layout_info.addLayout(self.layout_top_row)

        self.map = {'Category': [':category.png', category],
                    'Drive': [':drive.png', drive],
                    'Folder Path': [':folder.png', file.absoluteDir().path()],
                    'Filename': [':file.png', file.fileName()],
                    'Size': [':size.png', HumanBytes.format(file.size(), True)]
                    }
        folder = self.map['Folder Path'][1]
        for k, v in self.map.items():
            self.rowInfo(k, v[0], v[1])

        self.layout.addWidget(info_group)
        self.parent().layout.addLayout(self.layout)
        self.launcherButton(folder)

    def launcherButton(self, path):
        image = QPixmap(':folder_go.png')
        folder_go_label = QtWidgets.QLabel()
        folder_go_label.setPixmap(image)
        folder_go_label.setMask(image.mask())
        launcher_button = QtWidgets.QPushButton()
        launcher_button.setIcon(QtGui.QIcon(image))
        launcher_button.setToolTip('Open in browser')
        launcher_button.clicked.connect(lambda: goToFileBrowser(path))
        self.layout_folder_go.addWidget(launcher_button)
        self.layout_folder_go.setAlignment(QtCore.Qt.AlignRight)

    def getLabelImageForList(self, src, row_type):
        image = QPixmap(src)
        img = image.scaled(16, 16, Qt.KeepAspectRatio)
        label_type = QtWidgets.QLabel()
        label_type.setPixmap(img)
        label_type.setMask(img.mask())
        label_type_text = QtWidgets.QLabel(row_type)
        label_type_text.setFixedWidth(70)
        self.lay_col_type = QtWidgets.QHBoxLayout()
        self.lay_col_type.addWidget(label_type)
        self.lay_col_type.addWidget(label_type_text)

    def rowInfo(self, row_type, src, value):
        self.getLabelImageForList(src, row_type)
        label_separator = QtWidgets.QLabel(' : ')
        label_separator.setFixedWidth(10)
        label_value = QtWidgets.QLabel(value)
        label_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label_value.setAlignment(Qt.AlignLeft)
        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self.lay_col_type)
        layout.addWidget(label_separator)
        layout.addWidget(label_value)
        layout.addStretch()
        if row_type != 'Category' and row_type != 'Drive':
            self.layout_info.addLayout(layout)
        else:
            self.layout_cat_and_drive.addLayout(layout)


class WImage(QtWidgets.QWidget):
    def __init__(self, file, parent=None):
        super(WImage, self).__init__(parent)
        self.file = file
        self.file_size = self.parent().size
        self.resize(800, 600)
        pixmap = QPixmap(file)
        self.image_width = pixmap.width()
        self.image_height = pixmap.height()
        if self.image_height > self.width() or self.image_height > self.height():
            image = pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        else:
            image = pixmap.scaled(self.image_width, self.image_height, Qt.KeepAspectRatio)
        self.label = QtWidgets.QLabel()
        self.label.setPixmap(image)
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.parent().layout.addLayout(self.layout)
        self.parent().resized.connect(self.parentResizeEvent)

    def parentResizeEvent(self):
        if self.image_height < self.width() or self.image_height < self.height():
            return
        # reduce size with complementary widgets (200)
        parent_width = self.parent().width() - 200
        parent_height = self.parent().height() - 200
        pixmap1 = QPixmap(self.file)
        pixmap = pixmap1.scaled(parent_width, parent_height, Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        self.label.resize(parent_width, parent_height)


class MediaPlayer(QWidget):

    def __init__(self, media_type, file_path, parent=None):
        super(MediaPlayer, self).__init__(parent)
        video_widget = QVideoWidget()
        video_widget.setMinimumSize(100, 100)
        btn_size = QSize(16, 16)
        self.media_player = QMediaPlayer()
        self.media_player.setVolume(50)
        if media_type == 'Video':
            self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setFixedHeight(24)
        self.play_button.setIconSize(btn_size)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.setPosition)

        self.volume_slider = QSlider(Qt.Vertical)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedHeight(50)
        self.volume_slider.sliderMoved.connect(self.setVolume)
        self.mute_button = QPushButton()
        self.mute_button.setCheckable(True)
        self.mute_button.setFixedHeight(24)
        self.mute_button.setIconSize(btn_size)
        self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.mute_button.clicked.connect(lambda: self.muteVolume(self.mute_button.isChecked()))

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)
        control_layout.addWidget(self.mute_button)
        control_layout.addWidget(self.volume_slider)

        self.layout = QVBoxLayout()
        if media_type == 'Video':
            self.layout.addWidget(video_widget)
            self.media_player.setVideoOutput(video_widget)
        self.layout.addLayout(control_layout)
        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.media_player.error.connect(self.handleError)
        mp_lay = QtWidgets.QHBoxLayout()
        mp_lay.addLayout(self.layout)
        self.parent().layout.addLayout(mp_lay)
        self.setSource(file_path)
        self.show()

    def setSource(self, filename):
        if filename != '':
            self.media_player.setMedia(
                    QMediaContent(QUrl.fromLocalFile(filename)))
            self.play_button.setEnabled(True)

    def play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def mediaStateChanged(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.position_slider.setValue(position)

    def durationChanged(self, duration):
        self.position_slider.setRange(0, duration)

    def setPosition(self, position):
        self.media_player.setPosition(position)

    def handleError(self):
        self.play_button.setEnabled(False)
        self.parent().status_bar.showMessage("Error: " + self.media_player.errorString())

    def setVolume(self, position):
        self.media_player.setVolume(position)

    def muteVolume(self, _is_checked):
        self.media_player.setMuted(not self.media_player.isMuted())
        if self.media_player.isMuted():
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))


class Editor(QTextEdit):

    def __init__(self, file, encoding, parent=None):
        super(Editor, self).__init__(parent)
        self.setReadOnly(True)
        text = 'Sorry! I could not read the file:\n' + file
        try:
            text = open(file, encoding=encoding).read()
        except Exception as _e:
            pass

        self.setText(text)
        layout_editor = QtWidgets.QVBoxLayout()
        layout_editor.addWidget(self)
        self.parent().layout.addLayout(layout_editor)

