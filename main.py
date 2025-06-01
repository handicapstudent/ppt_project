# main.py
import os
import sys
from restaurant_ui_relayout import RestaurantReservation
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QMessageBox, QLabel, QLineEdit, QDialog, QCheckBox, QFrame, QFileDialog
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt

from reservation_utils import init_db, get_user, save_user
from settings import AppSettings
from tts import speak

class ProfileDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("개인정보 관리")
        self.setFixedSize(400, 450)
        self.setModal(True)
        user = get_user(user_id)

        layout = QVBoxLayout()
        self.id_label = QLabel(f"학번: {user[0]}")
        layout.addWidget(self.id_label)

        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호 변경 (입력시 변경)")
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)

        self.cert_label = QLabel()
        self.status_label = QLabel()
        self.attach_btn = QPushButton("파일 첨부 (장애인등록증)")
        self.attach_btn.clicked.connect(self.attach_file)
        self.selected_file = None
        self.attach_btn.setVisible(False)  # 기본값 숨김

        cert_path = user[4] if len(user) > 4 else None
        if not cert_path:
            self.status_label.setText("장애인 인증 현황: 인증안됨")
            self.attach_btn.setVisible(True)
        else:
            # 실제 서비스라면 관리자 승인값으로 "인증중"/"인증완료" 분기!
            self.status_label.setText("장애인 인증 현황: 인증중")
            file_name = os.path.basename(cert_path)
            self.cert_label.setText(f"첨부파일: {file_name}")
        layout.addWidget(self.status_label)
        layout.addWidget(self.cert_label)
        layout.addWidget(self.attach_btn)

        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def attach_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "장애인등록증 파일 선택", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            self.selected_file = file_name
            self.cert_label.setText(os.path.basename(file_name))

    def save_changes(self):
        user = get_user(self.user_id)
        new_pw = self.pw_input.text() if self.pw_input.text() else user[1]
        question = user[2]
        answer = user[3]
        cert_path = user[4] if len(user) > 4 else None
        if self.selected_file:
            upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            basename = f"{self.user_id}_" + os.path.basename(self.selected_file)
            dest = os.path.join(upload_dir, basename)
            import shutil
            shutil.copy2(self.selected_file, dest)
            cert_path = dest
        save_user(self.user_id, new_pw, question, answer, cert_path)
        QMessageBox.information(self, "저장 완료", "개인정보가 저장되었습니다.")
        self.close()

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedSize(1200, 800)
        init_db()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        # 배경
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
        central_layout.setContentsMargins(80, 60, 80, 60)
        self.central_widget.setFixedSize(720, 600)
        self.central_widget.move((self.width() - 720) // 2, (self.height() - 600) // 2)
        self.central_widget.setStyleSheet("background-color: rgba(255, 255, 255, 230); border-radius: 32px;")

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
            widget.setStyleSheet("QLineEdit { background-color: white; color: black; padding: 16px; border: 2px solid #ccc; border-radius: 16px; }")
            central_layout.addWidget(widget)

        login_btn = QPushButton("로그인")
        login_btn.setFont(QFont("Arial", 24, QFont.Bold))
        login_btn.clicked.connect(self.login_check)
        login_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 20px; border-radius: 20px; font-weight: bold; } QPushButton:hover { background-color: #45a049; }")
        central_layout.addWidget(login_btn)

        link_layout = QHBoxLayout()
        signup_btn = QPushButton("회원가입")
        pw_find_btn = QPushButton("비밀번호 찾기")
        for btn in [signup_btn, pw_find_btn]:
            btn.setFont(QFont("Arial", 18))
            btn.setFlat(True)
            btn.setStyleSheet("QPushButton { color: #555; text-decoration: underline; } QPushButton:hover { color: #000; }")
            btn.setCursor(Qt.PointingHandCursor)

        signup_btn.clicked.connect(lambda: self.main_window.navigate_to(1))
        pw_find_btn.clicked.connect(lambda: self.main_window.navigate_to(3))

        link_layout.addWidget(signup_btn)
        link_layout.addStretch()
        link_layout.addWidget(pw_find_btn)

        accessibility_layout = QHBoxLayout()
        contrast_checkbox = QCheckBox("고대비 모드")
        contrast_checkbox.setFont(QFont("Arial", 18))
        contrast_checkbox.setChecked(False)
        contrast_checkbox.stateChanged.connect(self.toggle_contrast)

        tts_checkbox = QCheckBox("TTS 음성안내 활성화")
        tts_checkbox.setFont(QFont("Arial", 18))
        tts_checkbox.setChecked(True)
        tts_checkbox.stateChanged.connect(lambda state: setattr(AppSettings, 'tts_enabled', state == Qt.Checked))

        accessibility_layout.addWidget(contrast_checkbox)
        accessibility_layout.addWidget(tts_checkbox)

        central_layout.addLayout(accessibility_layout)
        central_layout.addLayout(link_layout)

        self.id_input.returnPressed.connect(login_btn.click)
        self.pw_input.returnPressed.connect(login_btn.click)

    def toggle_contrast(self, state):
        self.central_widget.setStyleSheet("background-color: black; border-radius: 32px;" if state else "background-color: rgba(255, 255, 255, 230); border-radius: 32px;")

    def login_check(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()
        user = get_user(user_id)
        if user and user[1] == password:
            if AppSettings.tts_enabled:
                speak("로그인 되셨습니다.")
            self.main_window.current_user_id = user_id
            self.main_window.restaurant_page.set_user(user_id)
            self.main_window.navigate_to(2)
        else:
            if AppSettings.tts_enabled:
                speak("학번 또는 비밀번호가 틀렸습니다.")
            QMessageBox.warning(self, "로그인 실패", "학번 또는 비밀번호가 틀렸습니다.")

class SignupPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.user_info = None
        self.selected_file = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("새 학번")
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("새 비밀번호")
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_confirm_input = QLineEdit()
        self.pw_confirm_input.setPlaceholderText("비밀번호 확인")
        self.pw_confirm_input.setEchoMode(QLineEdit.Password)
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("비밀번호 찾기 질문")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("질문 답변")
        self.file_label = QLabel("장애인등록증 파일 없음")
        attach_btn = QPushButton("장애인등록증 첨부")
        attach_btn.clicked.connect(self.attach_file)
        signup_btn = QPushButton("회원가입")
        signup_btn.clicked.connect(self.signup_check)
        for widget in [self.id_input, self.pw_input, self.pw_confirm_input,
                       self.question_input, self.answer_input, self.file_label, attach_btn, signup_btn]:
            layout.addWidget(widget)
        self.setLayout(layout)

    def attach_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "장애인등록증 파일 선택", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            self.selected_file = file_name
            self.file_label.setText(os.path.basename(file_name))
        else:
            self.selected_file = None
            self.file_label.setText("장애인등록증 파일 없음")

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
        if get_user(new_id):
            QMessageBox.warning(self, "회원가입 오류", "이미 존재하는 학번입니다.")
            return
        cert_path = None
        if self.selected_file:
            upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            basename = f"{new_id}_" + os.path.basename(self.selected_file)
            dest = os.path.join(upload_dir, basename)
            try:
                import shutil
                shutil.copy2(self.selected_file, dest)
                cert_path = dest
            except Exception as e:
                QMessageBox.warning(self, "첨부 오류", f"파일 복사 실패: {e}")
                return
        save_user(new_id, new_pw, question, answer, cert_path)
        QMessageBox.information(self, "회원가입 성공", f"{new_id}님, 회원가입이 완료되었습니다.")
        self.main_window.navigate_to(0)

class PasswordFindPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_user_id = None
        self.initUI()
    def initUI(self):
        layout = QVBoxLayout()
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("학번 입력")
        self.question_display = QLabel("질문이 여기에 표시됩니다.")
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("질문에 대한 답변 입력")
        find_btn = QPushButton("확인")
        find_btn.clicked.connect(self.check_answer)
        self.id_input.textChanged.connect(self.display_question)
        layout.addWidget(self.id_input)
        layout.addWidget(self.question_display)
        layout.addWidget(self.answer_input)
        layout.addWidget(find_btn)
        self.setLayout(layout)
    def display_question(self):
        user_id = self.id_input.text()
        self.current_user_id = user_id
        user = get_user(user_id)
        self.question_display.setText(user[2] if user else "존재하지 않는 학번입니다.")
    def check_answer(self):
        user = get_user(self.current_user_id)
        if user and self.answer_input.text() == user[3]:
            QMessageBox.information(self, "비밀번호", f"비밀번호는: {user[1]}")
            self.main_window.navigate_to(0)
        else:
            QMessageBox.warning(self, "오류", "답변이 일치하지 않습니다.")

class MainWindow(QWidget):
    def __init__(self):
        self.current_user_id = None  # 로그인한 학번 저장용
        super().__init__()
        self.setWindowTitle("HelpMeal")
        self.resize(1200, 800)

        self.stack = QStackedWidget()
        self.history = []
        self.history_index = -1

        self.login_page = LoginPage(self)
        self.signup_page = SignupPage(self)
        self.password_page = PasswordFindPage(self)
        self.restaurant_page = RestaurantReservation(self)

        self.stack.addWidget(self.login_page)         # index 0
        self.stack.addWidget(self.signup_page)        # index 1
        self.stack.addWidget(self.restaurant_page)    # index 2
        self.stack.addWidget(self.password_page)      # index 3

        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.setFlat(True)
        self.back_btn.clicked.connect(self.go_back)

        self.forward_btn = QPushButton(">")
        self.forward_btn.setFixedSize(32, 32)
        self.forward_btn.setFlat(True)
        self.forward_btn.clicked.connect(self.go_forward)

        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.setContentsMargins(10, 10, 10, 0)

        layout = QVBoxLayout()
        layout.addLayout(nav_layout)
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.navigate_to(0)

    def navigate_to(self, index):
        self.stack.setCurrentIndex(index)
        self.history = self.history[:self.history_index + 1]
        self.history.append(index)
        self.history_index += 1

    def go_back(self):
        if hasattr(self, 'sidebar_dialog') and self.sidebar_dialog.isVisible():
            self.sidebar_dialog.close()
            return
        if self.history_index > 0:
            self.history_index -= 1
            self.stack.setCurrentIndex(self.history[self.history_index])

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.stack.setCurrentIndex(self.history[self.history_index])


    def open_profile_dialog(self):
        if self.current_user_id:
            dialog = ProfileDialog(self.current_user_id, self)
            dialog.exec_()

    def logout(self):
        self.sidebar_dialog.close()
        self.navigate_to(0)

    def toggle_contrast_global(self, state):
        if state == Qt.Checked:
            self.setStyleSheet("background-color: black; color: white;")
        else:
            self.setStyleSheet("")

if __name__ == "__main__":
    init_db()
    AppSettings.tts_enabled = True
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
