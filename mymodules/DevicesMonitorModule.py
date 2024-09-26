import sys
import os
import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThreadPool

if sys.platform == 'linux':
    import pyudev


class WorkerKilledException(Exception):
    pass


class DeviceWorkerSignals(QtCore.QObject):
    configuration_changed = QtCore.pyqtSignal()


class DeviceJobRunner(QtCore.QRunnable):
    signals = DeviceWorkerSignals()

    def __init__(self):
        super().__init__()

        self.is_killed = False

    def kill(self):
        self.is_killed = True

    @pyqtSlot()
    def run(self):
        try:
            dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
            old = drives
            while True:
                if self.is_killed:
                    raise WorkerKilledException
                time.sleep(1)
                unchecked_drives = ['%s:' % d for d in dl if os.path.exists('%s:' % d)]
                if unchecked_drives != old:
                    self.signals.configuration_changed.emit()
                    old = unchecked_drives
        except WorkerKilledException:
            pass


class Devices(QtCore.QObject):
    """
    Monitoring devices status for adding/removing from device
    and add/remove available folders for indexing/reindexing
    """
    configuration_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        context = pyudev.Context()
        # Monitor devices
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by('block', device_type='disk')
        observer = pyudev.MonitorObserver(monitor, self.handleEvent)
        observer.start()
        # this will have to run continuously so will not stop
        # observer.stop()

    def handleEvent(self, _action, _device):
        self.configuration_changed.emit()


class Monitoring(QtCore.QObject):
    configuration_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(Monitoring, self).__init__(parent)

        if sys.platform == 'win32':
            self.device_threadpool = QThreadPool()
            self.devices_changes = DeviceJobRunner()
            self.devices_changes.signals.configuration_changed.connect(lambda: self.configurationChanged())
            self.device_threadpool.start(self.devices_changes)
            self.parent().kill_device_monitor_runner.connect(lambda: self.devices_changes.kill())
        elif sys.platform == 'linux':
            self.devices_changes = Devices()
            self.devices_changes_thread = QtCore.QThread()
            self.devices_changes.moveToThread(self.devices_changes_thread)
            self.devices_changes_thread.start()
            self.devices_changes.configuration_changed.connect(lambda: self.configurationChanged())

    def configurationChanged(self):
        self.configuration_changed.emit()
