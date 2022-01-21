#! /usr/bin/env python3

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QKeyEvent
from qvncwidget import QVNCWidget

class Window(QMainWindow):
    def __init__(self, app: QApplication):
        super(Window, self).__init__()

        self.app = app
        self.initUI()

    def initUI(self):
        self.setWindowTitle("QVNCWidget")

        self.vnc = QVNCWidget(
            parent=self,
            host="127.0.0.1", port=5900,
            password="1234"
        )
        self.setCentralWidget(self.vnc)
        self.vnc.start()

    def keyPressEvent(self, ev: QKeyEvent):
        self.vnc.onKeyPress.emit(ev)

    def keyReleaseEvent(self, ev: QKeyEvent):
        self.vnc.onKeyRelease.emit(ev)

app = QApplication(sys.argv)
window = Window(app)
window.resize(800, 600)
window.show()

sys.exit(app.exec_())
