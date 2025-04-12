import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QComboBox, QDialog, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
# 상단 import 부분에 추가
from reservation import reserve_seat


class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("학식 예약 프로그램 - 로그인")
        self.setGeometry(100, 100, 300, 200)
        self.initUI()

        self.users = {
            "user1": {"password": "pass1", "security_question": "가장 좋아하는 색깔은?", "security_answer": "파란색"},
            "user2": {"password": "pass2", "security_question": "처음 키운 애완동물 이름은?", "security_answer": "멍멍이"}
        }

    def initUI(self):
        layout = QVBoxLayout()

        title_font = QFont('Arial', 16, QFont.Bold)
        title_label = QLabel("학식 예약 시스템")
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("학번")
        layout.addWidget(self.id_input)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)

        login_btn = QPushButton("로그인")
        login_btn.clicked.connect(self.login_check)
        layout.addWidget(login_btn)

        signup_btn = QPushButton("회원가입")
        signup_btn.clicked.connect(self.signup)
        layout.addWidget(signup_btn)

        find_pw_btn = QPushButton("비밀번호 찾기")
        find_pw_btn.clicked.connect(self.find_password)
        layout.addWidget(find_pw_btn)

        self.setLayout(layout)

    def login_check(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()

        if user_id in self.users and self.users[user_id]["password"] == password:
            self.main_window.restaurant_selection_window.show_restaurant_selection(user_id)
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
            self.pw_input.clear()
            self.pw_confirm_input.clear()
            return

        if new_id in self.parent().users:
            QMessageBox.warning(self, "회원가입 오류", "이미 존재하는 학번입니다.")
            return

        self.user_info = (new_id, new_pw, question, answer)
        self.close()

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

class RestaurantSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학식 예약 프로그램 - 식당 선택")
        self.setGeometry(50, 50, 700, 300)
        self.current_user = None

        self.restaurant_menus = {
            "한빛식당": "김치찌개, 제육볶음, 돈까스",
            "별빛식당": "된장찌개, 생선구이, 오므라이스",
            "은하수식당": "부대찌개, 닭갈비, 스파게티"
        }

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        top_label = QLabel("원하는 식당의 메뉴를 선택해주세요")
        top_label.setFont(QFont("Arial", 14))
        top_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(top_label)

        restaurant_layout = QHBoxLayout()

        for restaurant, menu in self.restaurant_menus.items():
            col = QVBoxLayout()

            name_label = QLabel(restaurant)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFont(QFont("Arial", 12, QFont.Bold))
            col.addWidget(name_label)

            menu_button = QPushButton(menu)
            menu_button.clicked.connect(lambda checked, r=restaurant, m=menu: reserve_seat(r, m))
            col.addWidget(menu_button)

            restaurant_layout.addLayout(col)

        layout.addLayout(restaurant_layout)
        self.setLayout(layout)

    def show_restaurant_selection(self, user_id):
        self.current_user = user_id
        self.show()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.login_window = LoginWindow(self)
        self.restaurant_selection_window = RestaurantSelectionWindow()
        self.login_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
