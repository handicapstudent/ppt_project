# magnifier.py
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QGuiApplication, QCursor

class Magnifier(QWidget):
    def __init__(self, parent=None, zoom=2, size=200):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.zoom = zoom
        self.size = size  # 확대 영역(픽셀)
        self.label = QLabel(self)
        self.setFixedSize(size, size)
        self.label.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlag(Qt.Tool)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_magnifier)

    def start(self):
        self.timer.start(30)  # 30ms 마다 갱신(부드럽게)
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def update_magnifier(self):
        cursor_pos = QCursor.pos()
        grab_rect = (cursor_pos.x() - self.size // (2*self.zoom),
                     cursor_pos.y() - self.size // (2*self.zoom),
                     self.size // self.zoom, self.size // self.zoom)
        screen = QGuiApplication.primaryScreen()
        img = screen.grabWindow(0, *grab_rect)
        pixmap = img.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.label.setPixmap(pixmap)
        offset = 30
        self.move(cursor_pos.x() + offset, cursor_pos.y() + offset)
