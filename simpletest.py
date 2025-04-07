import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QComboBox, QDialog
from PyQt5.QtGui import QFont

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("학식 예약 프로그램 - 로그인")
        self.setGeometry(100, 100, 300, 200)
        self.initUI()

        # 간단한 사용자 정보 (실제로는 데이터베이스에서 관리)
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

        self.id_label = QLabel("학번:")
        self.id_input = QLineEdit()
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        self.pw_label = QLabel("비밀번호:")
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_label)
        layout.addWidget(self.pw_input)

        login_btn = QPushButton("로그인", self)
        login_btn.clicked.connect(self.login_check)
        layout.addWidget(login_btn)

        signup_btn = QPushButton("회원가입", self)
        signup_btn.clicked.connect(self.signup)
        layout.addWidget(signup_btn)

        find_pw_btn = QPushButton("비밀번호 찾기", self)
        find_pw_btn.clicked.connect(self.find_password)
        layout.addWidget(find_pw_btn)

        self.setLayout(layout)

    def login_check(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()

        if user_id in self.users and self.users[user_id]["password"] == password:
            print("로그인 성공!")
            self.main_window.restaurant_selection_window.show_restaurant_selection(user_id) # 로그인 성공 후 식당 선택 창 표시
            self.hide() # LoginWindow 숨기기
            print("LoginWindow 숨김")
        else:
            QMessageBox.warning(self, "로그인 실패", "학번 또는 비밀번호가 틀렸습니다.")
            self.pw_input.clear()

    def signup(self):
        signup_dialog = SignupDialog(self)
        signup_dialog.exec()
        if signup_dialog.user_info:
            user_id, password, question, answer = signup_dialog.user_info
            self.users[user_id] = {"password": password, "security_question": question, "security_answer": answer}
            QMessageBox.information(self, "회원가입 성공", f"{user_id}님, 회원가입이 완료되었습니다.")

    def find_password(self):
        find_pw_dialog = FindPasswordDialog(self.users)
        find_pw_dialog.exec_()

class SignupDialog(QDialog): # QWidget 대신 QDialog를 상속받도록 수정
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("회원가입")
        self.setGeometry(150, 150, 350, 250)
        self.user_info = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.id_label = QLabel("새 학번:")
        self.id_input = QLineEdit()
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        self.pw_label = QLabel("새 비밀번호:")
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_label)
        layout.addWidget(self.pw_input)

        self.pw_confirm_label = QLabel("비밀번호 확인:")
        self.pw_confirm_input = QLineEdit()
        self.pw_confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_confirm_label)
        layout.addWidget(self.pw_confirm_input)

        self.question_label = QLabel("비밀번호 찾기 질문:")
        self.question_input = QLineEdit()
        layout.addWidget(self.question_label)
        layout.addWidget(self.question_input)

        self.answer_label = QLabel("질문 답변:")
        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_label)
        layout.addWidget(self.answer_input)

        signup_btn = QPushButton("회원가입", self)
        signup_btn.clicked.connect(self.signup_check)
        layout.addWidget(signup_btn)

        cancel_btn = QPushButton("취소", self)
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

        self.id_label = QLabel("학번:")
        self.id_input = QLineEdit()
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        self.question_label = QLabel("질문:")
        self.question_display = QLabel()
        layout.addWidget(self.question_label)
        layout.addWidget(self.question_display)

        self.answer_label = QLabel("답변:")
        self.answer_input = QLineEdit()
        layout.addWidget(self.answer_label)
        layout.addWidget(self.answer_input)

        find_btn = QPushButton("확인", self)
        find_btn.clicked.connect(self.check_answer)
        layout.addWidget(find_btn)

        cancel_btn = QPushButton("취소", self)
        cancel_btn.clicked.connect(self.close)
        layout.addWidget(cancel_btn)

        self.setLayout(layout)

        self.id_input.textChanged.connect(self.display_question)
        self.current_user_id = None

    def display_question(self, user_id):
        self.current_user_id = user_id
        if user_id in self.users:
            self.question_display.setText(self.users[user_id]["security_question"])
        else:
            self.question_display.setText("존재하지 않는 학번입니다.")

    def check_answer(self):
        if self.current_user_id and self.current_user_id in self.users:
            correct_answer = self.users[self.current_user_id]["security_answer"]
            user_answer = self.answer_input.text()
            if user_answer == correct_answer:
                QMessageBox.information(self, "비밀번호 찾기 성공", f"비밀번호는: {self.users[self.current_user_id]['password']} 입니다.")
                self.close()
            else:
                QMessageBox.warning(self, "비밀번호 찾기 실패", "답변이 틀렸습니다.")
                self.answer_input.clear()
        else:
            QMessageBox.warning(self, "비밀번호 찾기 실패", "학번을 먼저 입력해주세요.")

class RestaurantSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학식 예약 프로그램 - 식당 선택")
        self.setGeometry(50, 50, 400, 300)
        self.current_user = None

        # 간단한 식당 정보
        self.restaurants = ["한빛식당", "별빛식당", "은하수식당"]
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        welcome_label = QLabel("안녕하세요!")
        self.user_info_label = QLabel()
        layout.addWidget(welcome_label)
        layout.addWidget(self.user_info_label)

        restaurant_label = QLabel("식당을 선택하세요:")
        self.restaurant_combo = QComboBox()
        self.restaurant_combo.addItems(self.restaurants)
        layout.addWidget(restaurant_label)
        layout.addWidget(self.restaurant_combo)

        select_btn = QPushButton("선택", self)
        select_btn.clicked.connect(self.show_reservation_options)
        layout.addWidget(select_btn)

        logout_btn = QPushButton("로그아웃", self)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        self.setLayout(layout)

    def show_restaurant_selection(self, user_id):
        print("RestaurantSelectionWindow.show_restaurant_selection 호출됨", user_id)
        self.current_user = user_id
        self.user_info_label.setText(f"{user_id}님")
        self.show()

    def show_reservation_options(self):
        selected_restaurant = self.restaurant_combo.currentText()
        QMessageBox.information(self, "식당 선택", f"{selected_restaurant}을 선택하셨습니다. (예약 옵션 구현 예정)")

    def logout(self):
        self.parent().login_window.show()
        self.hide()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("MainWindow.__init__ 호출됨")
        self.login_window = LoginWindow(self)
        print("LoginWindow 객체 생성됨")
        self.restaurant_selection_window = RestaurantSelectionWindow()
        print("RestaurantSelectionWindow 객체 생성됨")
        self.login_window.show()
        print("LoginWindow.show() 호출됨")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
