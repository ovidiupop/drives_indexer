from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QHBoxLayout, QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar)


class MediaPlayer(QWidget):

    def __init__(self, media_type,  parent=None):
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

        self.status_bar = QStatusBar()
        self.status_bar.setFont(QFont("Noto Sans", 7))
        self.status_bar.setFixedHeight(14)

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
        self.layout.addWidget(self.status_bar)

        self.media_player.stateChanged.connect(self.mediaStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)
        self.media_player.error.connect(self.handleError)
        self.status_bar.showMessage("Ready")

        self.show()

    def set_source(self, filename):
        if filename != '':
            self.media_player.setMedia(
                    QMediaContent(QUrl.fromLocalFile(filename)))
            self.play_button.setEnabled(True)
            self.status_bar.showMessage(filename)

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
        self.status_bar.showMessage("Error: " + self.media_player.errorString())

    def setVolume(self, position):
        self.media_player.setVolume(position)

    def muteVolume(self, is_checked):
        self.media_player.setMuted(not self.media_player.isMuted())
        if self.media_player.isMuted():
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        else:
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
