# main.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QDialog, QHBoxLayout, QScrollArea, QGroupBox
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from reservation_utils import reserve_seat  # 예약 기능
import sqlite3
import os

# --- 메인 윈도우 ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.restaurant_selection_window = RestaurantReservation()
        self.login_window = LoginWindow(self)
        self.login_window.show()

# --- 로그인 창 ---
class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("학식 예약 프로그램 - 로그인")
        self.setGeometry(200, 200, 400, 300)
        self.initUI()
        self.users = {
            "user1": {"password": "pass1", "security_question": "가장 좋아하는 색깔은?", "security_answer": "파란색"},
            "user2": {"password": "pass2", "security_question": "처음 키운 애완동물 이름은?", "security_answer": "멍멍이"}
        }

    def initUI(self):
        self.setFixedSize(500, 350)

        # === 배경 이미지 ===
        bg_label = QLabel(self)
        image_path = os.path.join(os.path.dirname(__file__), "충북대학교 정문.jpg")
        pixmap = QPixmap(image_path).scaled(self.width(), self.height(), Qt.KeepAspectRatioByExpanding)
        bg_label.setPixmap(pixmap)
        bg_label.setScaledContents(True)
        bg_label.setGeometry(0, 0, 500, 350)

        # === 메인 박스 ===
        content_widget = QWidget(self)
        content_widget.setGeometry(90, 50, 320, 250)
        content_widget.setStyleSheet("""
            background-color: rgba(255, 255, 255, 220);
            border-radius: 20px;
            box-shadow: 0px 0px 12px rgba(0, 0, 0, 0.3);
        """)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # === 상단: 로고 + 텍스트 ===
        top_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "HelpMeal.png")
        logo_pixmap = QPixmap(logo_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)

        app_name = QLabel("HelpMeal")
        app_name.setFont(QFont('Arial', 18, QFont.Bold))
        app_name.setStyleSheet("color: black;")

        top_layout.addWidget(logo_label)
        top_layout.addSpacing(10)
        top_layout.addWidget(app_name)
        top_layout.addStretch()

        content_layout.addLayout(top_layout)

        # === ID, PW 입력 ===
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        self.id_input.setStyleSheet("background-color: white;")
        content_layout.addWidget(self.id_input)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("PW")
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_input.setStyleSheet("background-color: white;")
        content_layout.addWidget(self.pw_input)

        # === 로그인 버튼 (강조 스타일)
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E8B57;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                height: 40px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #246B45;
            }
        """)
        login_btn.clicked.connect(self.login_check)
        content_layout.addWidget(login_btn)

        # === 회원가입 + PW 찾기 나란히
        bottom_btn_layout = QHBoxLayout()
        signup_btn = QPushButton("회원가입")
        pw_find_btn = QPushButton("PW 찾기")
        for btn in [signup_btn, pw_find_btn]:
            btn.setStyleSheet("background-color: rgba(255, 255, 255, 200);")
            btn.setFixedHeight(30)

        signup_btn.clicked.connect(self.signup)
        pw_find_btn.clicked.connect(self.find_password)
        bottom_btn_layout.addWidget(signup_btn)
        bottom_btn_layout.addWidget(pw_find_btn)

        content_layout.addLayout(bottom_btn_layout)
        content_widget.setLayout(content_layout)

    def login_check(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()

        if user_id in self.users and self.users[user_id]["password"] == password:
            self.main_window.restaurant_selection_window.set_user(user_id)
            self.main_window.restaurant_selection_window.show()
            self.hide()
        else:
            QMessageBox.warning(self, "로그인 실패", "학번 또는 비밀번호가 틀렸습니다.")
            self.pw_input.clear()

    def signup(self):
        signup_dialog = SignupDialog(self)
        signup_dialog.exec()
        if signup_dialog.user_info:
            user_id, password, question, answer = signup_dialog.user_info
            self.users[user_id] = {
                "password": password,
                "security_question": question,
                "security_answer": answer
            }
            QMessageBox.information(self, "회원가입 성공", f"{user_id}님, 회원가입이 완료되었습니다.")

    def find_password(self):
        find_pw_dialog = FindPasswordDialog(self.users)
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

    def signup_check(self):
        new_id = self.id_input.text()
        new_pw = self.pw_input.text()
        pw_confirm = self.pw_confirm_input.text()
        question = self.question_input.text()
        answer = self.answer_input.text()

        if not new_id or not new_pw or not question or not answer:
            QMessageBox.warning(self, "회원가입 오류", "모든 항목을 입력해주세요.")
            return

        if new_pw != pw_confirm:
            QMessageBox.warning(self, "회원가입 오류", "비밀번호 확인이 일치하지 않습니다.")
            return

        if new_id in self.parent().users:
            QMessageBox.warning(self, "회원가입 오류", "이미 존재하는 학번입니다.")
            return

        self.user_info = (new_id, new_pw, question, answer)
        self.close()

# --- 비밀번호 찾기 창 ---
class FindPasswordDialog(QWidget):
    def __init__(self, users, parent=None):
        super().__init__(parent)
        self.setWindowTitle("비밀번호 찾기")
        self.setGeometry(150, 150, 350, 200)
        self.users = users
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("학번 입력")
        layout.addWidget(self.id_input)

        self.question_display = QLabel("질문이 여기에 표시됩니다.")
        layout.addWidget(self.question_display)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("질문에 대한 답변 입력")
        layout.addWidget(self.answer_input)

        find_btn = QPushButton("확인")
        find_btn.clicked.connect(self.check_answer)
        layout.addWidget(find_btn)

        self.id_input.textChanged.connect(self.display_question)

        self.setLayout(layout)
        self.current_user_id = None

    def display_question(self, user_id):
        self.current_user_id = user_id
        if user_id in self.users:
            self.question_display.setText(self.users[user_id]["security_question"])
        else:
            self.question_display.setText("존재하지 않는 학번입니다.")

    def check_answer(self):
        if self.current_user_id and self.current_user_id in self.users:
            correct = self.users[self.current_user_id]["security_answer"]
            if self.answer_input.text() == correct:
                QMessageBox.information(self, "비밀번호", f"비밀번호는: {self.users[self.current_user_id]['password']}")
                self.close()
            else:
                QMessageBox.warning(self, "오류", "답변이 일치하지 않습니다.")
        else:
            QMessageBox.warning(self, "오류", "학번을 다시 확인해주세요.")

# --- 식당 선택 및 예약 창 ---
class RestaurantReservation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학식 예약 프로그램")
        self.setGeometry(100, 100, 800, 400)
        self.current_user_id = None
        self.initUI()

    def set_user(self, user_id):
        self.current_user_id = user_id

    def initUI(self):
        main_layout = QVBoxLayout()

        title = QLabel("학식 예약 시스템")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QHBoxLayout()

        restaurants = [
            {"name": "한빛식당", "menus": ["김치찌개", "제육볶음", "돈까스"], "allergy": "우유, 땅콩"},
            {"name": "별빛식당", "menus": ["된장찌개", "생선구이", "오므라이스"], "allergy": "대두, 밀"},
            {"name": "은하수식당", "menus": ["부대찌개", "닭갈비", "스파게티"], "allergy": "계란, 토마토"}
        ]

        for restaurant in restaurants:
            box = self.create_restaurant_box(restaurant)
            content_layout.addWidget(box)

        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def create_restaurant_box(self, restaurant):
        group_box = QGroupBox()
        layout = QVBoxLayout()

        name_label = QLabel(restaurant["name"])
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)

        menu_label = QLabel("\n".join(restaurant["menus"]))
        menu_label.setFont(QFont("Arial", 12))
        layout.addWidget(menu_label)

        allergy_label = QLabel(f"알레르기 정보: {restaurant['allergy']}")
        allergy_label.setFont(QFont("Arial", 10))
        layout.addWidget(allergy_label)

        reserve_button = QPushButton("예약하기")
        reserve_button.clicked.connect(lambda _, r=restaurant["name"]: self.reserve_seat_dialog(r))
        layout.addWidget(reserve_button)

        group_box.setLayout(layout)
        group_box.setFixedSize(230, 250)
        return group_box

    def reserve_seat_dialog(self, restaurant_name):
        if not self.current_user_id:
            QMessageBox.warning(self, "오류", "먼저 로그인하세요.")
            return
        reserve_seat(self, restaurant_name, self.current_user_id)

# --- 프로그램 실행 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
