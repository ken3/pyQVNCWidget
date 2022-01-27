#! /usr/bin/env python3

import sys

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QKeyEvent, QCursor, QPixmap
from qvncwidget import QVNCWidget

class Window(QMainWindow):
    def __init__(self, app: QApplication):
        super(Window, self).__init__()

        self.app = app
        self.initUI()
        self.isResizing = False

        # local cursor shape on this application
        pixmap = QPixmap(2,2)
        pixmap.fill(Qt.white)
        myCursor = QCursor(pixmap)
        QApplication.setOverrideCursor(myCursor)

    def initUI(self):
        self.setWindowTitle("QVNCWidget")

        self.vnc = QVNCWidget(
            parent=self,
            host="127.0.0.1", port=5900,
            password="1234",
            mouseTracking=True
        )
        self.setCentralWidget(self.vnc)
        self.vnc.onInitialResize.connect(self.resize)
        self.vnc.start()

    def keyPressEvent(self, ev: QKeyEvent):
        self.vnc.onKeyPress.emit(ev)

    def keyReleaseEvent(self, ev: QKeyEvent):
        self.vnc.onKeyRelease.emit(ev)

    def event(self, ev: QEvent):
        t = ev.type()
        #print(f"event: type={t};")

        if t == QEvent.Resize:
            # pixmap resizing in progress
            self.isResizing = True
        elif t == QEvent.ActivationChange:
            # Fit MainWindow to resized pixmap
            self.isResizing = False
            pixmap = self.vnc.pixmap()
            vncWidth = self.vnc.vncWidth
            if pixmap and vncWidth:
                print(f"view scale: {float(pixmap.width()) / float(self.vnc.vncWidth)}")
                self.resize(pixmap.size())
        """elif t == QEvent.NonClientAreaMouseButtonRelease:
            self.isResizing = False
        elif t == QEvent.PlatformSurface:
            self.isResizing = False
        else:
            True
            """
        return super().event(ev)

app = QApplication(sys.argv)
window = Window(app)
#window.resize(800, 600)
window.show()

sys.exit(app.exec_())
