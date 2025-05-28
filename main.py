# main.py
import os
from menu import RestaurantReservation
import sqlite3
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QDialog, QHBoxLayout, QScrollArea, QGroupBox, QCheckBox
)
import sys
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from review import ReviewDialog, init_database  # 리뷰 모듈 관련
from settings import AppSettings
from tts import speak
from reservation_utils import reserve_seat, init_db, save_user, get_user
from theme import apply_high_contrast, reset_theme
from menu import RestaurantReservation  # ✔ 메뉴 기능 분리 완료

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.restaurant_selection_window = RestaurantReservation()
        self.login_window = LoginWindow(self)
        self.login_window.show()

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("HelpMeal 로그인")
        self.resize(1200, 800)  # 2배 확대
        self.high_contrast = False
        init_db()
        self.initUI()

    def initUI(self):
        bg_label = QLabel(self)
        image_path = os.path.join(os.path.dirname(__file__), "충북대학교 정문.jpg")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            bg_label.setPixmap(pixmap)
        else:
            bg_label.setStyleSheet("background-color: #f0f0f0;")
        bg_label.setScaledContents(True)
        bg_label.setGeometry(0, 0, self.width(), self.height())
        bg_label.lower()

        self.central_widget = QWidget(self)
        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(80, 60, 80, 60)  # 2배
        self.central_widget.setFixedSize(720, 600)
        self.central_widget.move((self.width() - self.central_widget.width()) // 2,
                                 (self.height() - self.central_widget.height()) // 2)
        self.central_widget.setStyleSheet("""
            background-color: rgba(255, 255, 255, 230);
            border-radius: 32px;
        """)

        title_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "HelpMeal.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)

        title_text = QLabel("HelpMeal")
        title_text.setFont(QFont("Arial", 40, QFont.Bold))
        title_text.setStyleSheet("color: #333333;")

        title_layout.addWidget(logo_label)
        title_layout.addSpacing(20)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        central_layout.addLayout(title_layout)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("Password")
        self.pw_input.setEchoMode(QLineEdit.Password)

        for widget in [self.id_input, self.pw_input]:
            widget.setFont(QFont("Arial", 24))
            widget.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: black;
                    padding: 16px;
                    border: 2px solid #ccc;
                    border-radius: 16px;
                }
            """)
            central_layout.addWidget(widget)

        login_btn = QPushButton("로그인")
        login_btn.setFont(QFont("Arial", 24, QFont.Bold))
        login_btn.clicked.connect(self.login_check)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        central_layout.addWidget(login_btn)

        link_layout = QHBoxLayout()
        signup_btn = QPushButton("회원가입")
        pw_find_btn = QPushButton("비밀번호 찾기")
        for btn in [signup_btn, pw_find_btn]:
            btn.setFont(QFont("Arial", 18))
            btn.setFlat(True)
            btn.setStyleSheet("""
                QPushButton {
                    color: #555;
                    text-decoration: underline;
                }
                QPushButton:hover {
                    color: #000;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)

        signup_btn.clicked.connect(self.signup)
        pw_find_btn.clicked.connect(self.find_password)

        link_layout.addWidget(signup_btn)
        link_layout.addStretch()
        link_layout.addWidget(pw_find_btn)

        self.tts_enabled = True
        accessibility_layout = QHBoxLayout()

        contrast_checkbox = QCheckBox("고대비 모드")
        contrast_checkbox.setFont(QFont("Arial", 18))
        contrast_checkbox.setChecked(False)
        contrast_checkbox.stateChanged.connect(self.toggle_contrast)

        tts_checkbox = QCheckBox("TTS 음성안내 활성화")
        tts_checkbox.setFont(QFont("Arial", 18))
        tts_checkbox.setChecked(True)
        tts_checkbox.stateChanged.connect(
            lambda state: setattr(AppSettings, 'tts_enabled', state == Qt.Checked)
        )

        accessibility_layout.addWidget(contrast_checkbox)
        accessibility_layout.addWidget(tts_checkbox)
        central_layout.addLayout(accessibility_layout)

        central_layout.addLayout(link_layout)

        self.id_input.returnPressed.connect(login_btn.click)
        self.pw_input.returnPressed.connect(login_btn.click)

    def toggle_contrast(self, state):
        self.high_contrast = (state == Qt.Checked)
        app = QApplication.instance()
        if self.high_contrast:
            apply_high_contrast(app)
            self.central_widget.setStyleSheet("background-color: black; border-radius: 32px;")
            self.id_input.setStyleSheet("""
                QLineEdit {
                    background-color: black;
                    color: white;
                    padding: 16px;
                    border: 2px solid white;
                    border-radius: 16px;
                }
            """)
            self.pw_input.setStyleSheet("""
                QLineEdit {
                    background-color: black;
                    color: white;
                    padding: 16px;
                    border: 2px solid white;
                    border-radius: 16px;
                }
            """)
        else:
            reset_theme(app)
            self.central_widget.setStyleSheet("background-color: rgba(255, 255, 255, 230); border-radius: 32px;")
            self.id_input.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: black;
                    padding: 16px;
                    border: 2px solid #ccc;
                    border-radius: 16px;
                }
            """)
            self.pw_input.setStyleSheet("""
                QLineEdit {
                    background-color: white;
                    color: black;
                    padding: 16px;
                    border: 2px solid #ccc;
                    border-radius: 16px;
                }
            """)

    def login_check(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()
        user = get_user(user_id)
        if user and user[1] == password:
            if AppSettings.tts_enabled:
                speak("로그인 되셨습니다.")
            self.main_window.restaurant_selection_window.set_user(user_id)
            self.main_window.restaurant_selection_window.show()
            self.hide()
        else:
            if AppSettings.tts_enabled:
                speak("학번 또는 비밀번호가 틀렸습니다.")
            QMessageBox.warning(self, "로그인 실패", "학번 또는 비밀번호가 틀렸습니다.")
            self.pw_input.clear()

    def signup(self):
        signup_dialog = SignupDialog(self)
        signup_dialog.exec()
        if signup_dialog.user_info:
            user_id, password, question, answer = signup_dialog.user_info
            if AppSettings.tts_enabled:
                speak("회원가입 오류 이미 존재하는 학번입니다.")
            if get_user(user_id):
                QMessageBox.warning(self, "회원가입 오류", "이미 존재하는 학번입니다.")
                return
            save_user(user_id, password, question, answer)
            if AppSettings.tts_enabled:
                speak("회원가입이 완료되었습니다.")
            QMessageBox.information(self, "회원가입 성공", f"{user_id}님, 회원가입이 완료되었습니다.")

    def find_password(self):
        find_pw_dialog = FindPasswordDialog()
        find_pw_dialog.exec_()

# --- 회원가입 다이얼로그 ---
class SignupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("회원가입")
        self.setGeometry(150, 150, 350, 250)
        self.user_info = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("새 학번")
        layout.addWidget(self.id_input)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("새 비밀번호")
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)

        self.pw_confirm_input = QLineEdit()
        self.pw_confirm_input.setPlaceholderText("비밀번호 확인")
        self.pw_confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_confirm_input)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("비밀번호 찾기 질문")
        layout.addWidget(self.question_input)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("질문 답변")
        layout.addWidget(self.answer_input)

        signup_btn = QPushButton("회원가입")
        signup_btn.clicked.connect(self.signup_check)
        layout.addWidget(signup_btn)

        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)
        if AppSettings.tts_enabled:
            speak("학번 비밀번호 비밀번호 확인 찾기 찾기질문 입력")


    def signup_check(self):
        new_id = self.id_input.text()
        new_pw = self.pw_input.text()
        pw_confirm = self.pw_confirm_input.text()
        question = self.question_input.text()
        answer = self.answer_input.text()

        if not new_id or not new_pw or not question or not answer:
            if AppSettings.tts_enabled:
                speak("회원가입오류 모든 항목을 입력해주세요.")
            QMessageBox.warning(self, "회원가입 오류", "모든 항목을 입력해주세요.")
            return

        if new_pw != pw_confirm:
            if AppSettings.tts_enabled:
                speak("회원가입오류 비밀번호 확인이 일치하지 않습니다.")
            QMessageBox.warning(self, "회원가입 오류", "비밀번호 확인이 일치하지 않습니다.")
            return

        if get_user(new_id):
            if AppSettings.tts_enabled:
                speak("회원가입 오류 이미 존재하는 학번입니다.")
            QMessageBox.warning(self, "회원가입 오류", "이미 존재하는 학번입니다.")
            return

        self.user_info = (new_id, new_pw, question, answer)
        self.close()

# --- 비밀번호 찾기 창 ---
class FindPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("비밀번호 찾기")
        self.setGeometry(150, 150, 350, 200)
        self.initUI()
        self.current_user_id = None

    def initUI(self):
        if AppSettings.tts_enabled:
            speak("학번입력, 질문에대한 답변 입력.")
        layout = QVBoxLayout()

        # 학번 입력
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("학번 입력")
        layout.addWidget(self.id_input)

        # 보안 질문 표시
        self.question_display = QLabel("질문이 여기에 표시됩니다.")
        layout.addWidget(self.question_display)

        # 질문에 대한 답변 입력
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("질문에 대한 답변 입력")
        layout.addWidget(self.answer_input)

        # 확인 버튼
        find_btn = QPushButton("확인")
        find_btn.clicked.connect(self.check_answer)
        layout.addWidget(find_btn)

        # 학번 입력 시 질문 표시 업데이트
        self.id_input.textChanged.connect(self.display_question)

        self.setLayout(layout)

    def display_question(self):
        user_id = self.id_input.text()
        self.current_user_id = user_id
        user = get_user(user_id)
        if user:
            self.question_display.setText(user[2])  # security_question
        else:
            self.question_display.setText("존재하지 않는 학번입니다.")

    def check_answer(self):
        user = get_user(self.current_user_id)
        if user and self.answer_input.text() == user[3]:  # security_answer
            if AppSettings.tts_enabled:
                speak(f"비밀번호는: {user[1]}")
            QMessageBox.information(self, "비밀번호", f"비밀번호는: {user[1]}")  # password
            self.close()
        else:
            if AppSettings.tts_enabled:
                speak("오류 답변이 일치하지 않습니다.")
            QMessageBox.warning(self, "오류", "답변이 일치하지 않습니다.")





# --- 프로그램 실행 ---
if __name__ == "__main__":
    init_database()  # 리뷰 DB 초기화
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
