# theme.py
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_high_contrast(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(Qt.black))
    palette.setColor(QPalette.WindowText, QColor(Qt.white))
    palette.setColor(QPalette.Base, QColor(Qt.black))
    palette.setColor(QPalette.AlternateBase, QColor(Qt.darkGray))
    palette.setColor(QPalette.ToolTipBase, QColor(Qt.white))
    palette.setColor(QPalette.ToolTipText, QColor(Qt.black))
    palette.setColor(QPalette.Text, QColor(Qt.white))
    palette.setColor(QPalette.Button, QColor(Qt.black))
    palette.setColor(QPalette.ButtonText, QColor(Qt.white))
    palette.setColor(QPalette.Highlight, QColor(Qt.white))
    palette.setColor(QPalette.HighlightedText, QColor(Qt.black))
    app.setPalette(palette)

    app.setStyleSheet("""
        QWidget {
            background-color: black;
            color: white;
        }
        QPushButton {
            background-color: #222;
            color: white;
            border: 1px solid white;
        }
        QPushButton:hover {
            background-color: #444;
        }
        QLineEdit, QTextEdit {
            background-color: #000;
            color: white;
            border: 1px solid white;
        }
    """)

def reset_theme(app):
    app.setPalette(QPalette())  # 기본 테마로 복원
    app.setStyleSheet("")
