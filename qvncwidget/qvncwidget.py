import logging

from PyQt5.QtCore import (
    QEvent,
    QSize,
    Qt,
    pyqtSignal
)
from PyQt5.QtGui import (
    QImage,
    QPaintEvent,
    QPainter,
    QPixmap,
    QResizeEvent,
    QKeyEvent,
    QMouseEvent
)

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QWidget
)

from qvncwidget.rfb import RFBClient
from qvncwidget.rfbhelpers import RFBPixelformat, RFBInput

log = logging.getLogger("QVNCWidget")

class QVNCWidget(QLabel, RFBClient):
    
    IMG_FORMAT = QImage.Format_RGB32

    onInitialResize = pyqtSignal(QSize)
    onUpdatePixmap = pyqtSignal(int, int, int, int, bytes)
    onSetPixmap = pyqtSignal()

    onKeyPress = pyqtSignal(QKeyEvent)
    onKeyRelease = pyqtSignal(QKeyEvent)

    def __init__(self, parent, 
                 host, port=5900, password: str=None,
                 mouseTracking=False):
        super().__init__(
            parent=parent,
            host=host,
            port=port,
            password=password,
            daemonThread=True
        )
        #import faulthandler
        #faulthandler.enable()
        self.screen: QImage = None
        self.vncWidth  = None
        self.vncHeight = None

        # The window can be shrink or expand
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # Prerequisites for cursor coordinate calculation
        self.setAlignment(Qt.AlignCenter)

        # initial pixmap (dummy)
        dummy = QPixmap(800, 600) # FIXME
        dummy.fill(Qt.white)
        self.setPixmap(dummy)

        self.onUpdatePixmap.connect(self._updateImage)
        self.onSetPixmap.connect(self._setImage)
        self.setMouseTracking(mouseTracking)

    def _initMouse(self):
        self.buttonMask = 0 # pressed buttons (bit fields)

    def _initKeypress(self):
        self.onKeyPress.connect(self._keyPress)
        self.onKeyRelease.connect(self._keyRelease)

    def start(self):
        self.startConnection()

    def stop(self):
        self.closeConnection()
        if self.screenPainter: self.screenPainter.end()

    def onConnectionMade(self):
        self.onInitialResize.emit(QSize(self.vncWidth, self.vncHeight))
        self.setPixelFormat(RFBPixelformat.getRGB32())
        self._initKeypress()
        self._initMouse()

    def onRectangleUpdate(self,
            x: int, y: int, width: int, height: int, data: bytes):
        self.onUpdatePixmap.emit(x, y, width, height, data)

    def onFramebufferUpdateFinished(self):
        self.onSetPixmap.emit()
        return

        # *** NOT_REACHED ***
        """if self.pixmap():
            #self.setPixmap(QPixmap.fromImage(self.image))
            self.resizeEvent(None)
            """

    def onFatalError(self, error: Exception):
        log.error(str(error))
        #logging.exception(str(error))
        #self.reconnect()

    def _updateImage(self, x: int, y: int, width: int, height: int, data: bytes):
        if not self.screen:
            self.screen = QImage(width, height, self.IMG_FORMAT)
            self.screen.fill(Qt.red)
            self.screenPainter = QPainter(self.screen)

        #self.painter.beginNativePainting()
        #self.painter.drawPixmapFragments()

        #with open("/tmp/images/test.raw", "wb") as f:
        #    f.write(data)
        
        #p = QPainter(self.screen)
        self.screenPainter.drawImage(
            x, y, QImage(data, width, height, self.IMG_FORMAT))
        #p.end()

        #self.repaint()
        #self.update()

    # *** NOT_USED ***
    """def _drawPixmap(self, x: int, y: int, pix: QPixmap):
        #self.paintLock.acquire()
        self.setPixmap(pix)
    
        if not self.painter:
            self.painter = QPainter(self.pixmap())
        else:
            print("DRAW PIXMAP:", x, y, self.pixmap(), self.painter, pix, pix.isNull())
            self.painter.drawPixmap(x, y, self.pixmap())
        #self.paintLock.release()
        """

    # *** NOT_USED ***
    """def _drawPixmap2(self, x: int, y: int, pix: QPixmap, data: bytes):
        if not self.pixmap() or (
            x == 0 and y == 0 and
            pix.width() == self.pixmap().width() and pix.height() == self.pixmap().height()):

            self.setPixmap(pix.copy())
            self._setPixmap()
            return
        
        import time
        print("DRAW PIXMAP:", x, y, self.pixmap().width(), self.pixmap().height(), pix.width(), pix.height())
        _t = time.time()
        #self.pixmap().save(f"/tmp/images/imgP_{_t}", "jpg")
        #with open(f"/tmp/images/img_{_t}.raw", "wb") as f:
        #    f.write(data)
        #pix.save(f"/tmp/images/img_{_t}", "jpg")

        painter = QPainter(self.pixmap())
        painter.drawPixmap(x, y, pix)
        painter.end()
        #self._setPixmap()
        """

    # *** NOT_USED ***
    """def _setPixmap(self):
        if self.pixmap():
            self.setPixmap(
                self.pixmap().scaled(
                    self.width(), self.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        """

    def _setImage(self):
        if self.screen:
            self.setPixmap(QPixmap.fromImage(
                self.screen.scaled(
                    self.width(), self.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            ))

    # Passed events

    def _keyPress(self, ev: QKeyEvent):
        self.keyEvent(
            RFBInput.fromQKeyEvent(ev.key(), ev.text()), down=1)

    def _keyRelease(self, ev: QKeyEvent):
        self.keyEvent(
            RFBInput.fromQKeyEvent(ev.key(), ev.text()), down=0)

    # Window events

    """def paintEvent(self, a0: QPaintEvent):
        return super().paintEvent(a0)
        if not self.screen:
            self.screen = QImage(self.size(), self.IMG_FORMAT)
            self.screen.fill(Qt.red)
            self.screenPainter = QPainter(self.screen)

        p = QPainter()
        p.begin(self)
        p.drawImage(0, 0,
            self.screen.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        p.end()
        """

    def resizeEvent(self, a0: QResizeEvent):
        if self.screen:
            self.setPixmap(QPixmap.fromImage(
                self.screen.scaled(
                    self.width(), self.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
            )
            self.updateMargins()

    def mousePressEvent(self, ev: QMouseEvent):
        self.buttonMask = RFBInput.fromQMouseEvent(ev, True, self.buttonMask)
        self.pointerEvent(*self._getRemoteRel(ev), self.buttonMask)

    def mouseReleaseEvent(self, ev: QMouseEvent):
        self.buttonMask = RFBInput.fromQMouseEvent(ev, False, self.buttonMask)
        self.pointerEvent(*self._getRemoteRel(ev), self.buttonMask)

    def mouseMoveEvent(self, ev: QMouseEvent):
        self.pointerEvent(*self._getRemoteRel(ev), self.buttonMask)

    def _getRemoteRel(self, ev: QMouseEvent) -> tuple:

        # y coord is kinda fucked up
        yDiff = (self.height() - self.pixmap().height()) / 2
        yPos = ev.localPos().y() - yDiff
        if yPos < 0: yPos = 0
        if yPos > self.pixmap().height(): yPos = self.pixmap().height()

        yPos = self._calcRemoteRel(
            yPos, self.pixmap().height(), self.vncHeight)

        # x coord is kinda fucked up, too
        xDiff = (self.width() - self.pixmap().width()) / 2
        xPos = ev.localPos().x() - xDiff
        if xPos < 0: xPos = 0
        if xPos > self.pixmap().width(): xPos = self.pixmap().width()

        xPos = self._calcRemoteRel(
            xPos, self.pixmap().width(), self.vncWidth)
        
        return xPos, yPos

    def _calcRemoteRel(self, locRel, locMax, remoteMax) -> int:
        return int( (locRel / locMax) * remoteMax )

    # keep pixmap aspect ratio

    def setPixmap(self, pix):
        super().setPixmap(pix)
        self.updateMargins()

    def updateMargins(self):
        pixmap = self.pixmap()
        if pixmap:
            pWidth  = pixmap.width()
            pHeight = pixmap.height()
            w = self.width()
            h = self.height()
            if w * pHeight > h * pWidth:
                m = (w - (pWidth * h / pHeight)) / 2
                self.setContentsMargins(m, 0, m, 0)
            else:
                m = (h - (pHeight * w / pWidth)) / 2
                self.setContentsMargins(0, m, 0, m)
        #self.update()

    def __del__(self):
        self.stop()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.deleteLater()
