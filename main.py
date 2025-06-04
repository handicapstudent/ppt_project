# main.py
import os
import sys
import shutil
from restaurant_ui_relayout import RestaurantReservation
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, QLabel, QLineEdit,
    QDialog, QCheckBox, QFrame, QComboBox, QSizePolicy, QGraphicsOpacityEffect, QFileDialog
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt

from reservation_utils import init_db, get_user, save_user
from settings import AppSettings
from tts import speak
from Magnifier import Magnifier

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
        self.attach_btn.setVisible(False)

        cert_path = user[4] if len(user) > 4 else None
        if not cert_path:
            self.status_label.setText("장애인 인증 현황: 인증안됨")
            self.attach_btn.setVisible(True)
        else:
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

        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(16)

        logo_label = QLabel()
        logo_label.setStyleSheet("background: transparent;")
        logo_path = os.path.join(os.path.dirname(__file__), "HelpMeal.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)

        title_text = QLabel("HelpMeal")
        title_text.setFont(QFont("Arial", 40, QFont.Bold))
        title_text.setStyleSheet("color: #333333; background: transparent;")
        title_layout.addStretch()
        title_layout.addWidget(logo_label)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        central_layout.addWidget(title_container)

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
            btn.setFont(QFont("Noto Sans KR", 18))
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
        contrast_checkbox.setFont(QFont("Noto Sans KR", 18))
        contrast_checkbox.setChecked(False)
        contrast_checkbox.stateChanged.connect(self.toggle_contrast)

        tts_checkbox = QCheckBox("TTS 음성안내 활성화")
        tts_checkbox.setFont(QFont("Noto Sans KR", 18))
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
        self.cert_file = None
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white;")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0,0,0,0)
        outer_layout.setSpacing(0)

        self.central_widget = QWidget()
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.central_widget.setStyleSheet("""
            background-color: white;
            border-radius: 0px;
            padding: 16px;
            border: 1px solid #ccc;
        """)
        form_layout = QVBoxLayout(self.central_widget)
        form_layout.setSpacing(12)
        title_label = QLabel("회원가입")
        title_label.setStyleSheet("""
                background-color: #ffffff;
                border-radius: 20px;
                padding: 12px;
                font-size: 24px;
                border: 1px solid #ddd;
            """)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Noto Sans KR", 24, QFont.Bold))
        form_layout.addWidget(title_label)
        form_layout.addSpacing(12)

        def add_field(label_text, widget):
            label = QLabel(label_text)
            label.setFont(QFont("Noto Sans KR",12,QFont.Bold))
            label.setStyleSheet("""
                background-color: #ffffff;
                border-radius: 20px;
                padding: 12px;
                font-size: 16px;
                border: 1px solid #ddd;
            """)
            form_layout.addWidget(label)
            form_layout.addWidget(widget)

        self.id_input = QLineEdit()
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_confirm_input = QLineEdit()
        self.pw_confirm_input.setEchoMode(QLineEdit.Password)
        self.question_combo = QComboBox()
        self.question_combo.addItems([
            "가장 좋아하는 음식은?",
            "출신 초등학교는?",
            "어릴 적 별명은?",
            "기억에 남는 선생님 이름은?",
            "가장 친한 친구 이름은?"
        ])
        self.answer_input = QLineEdit()
        for w in [self.id_input, self.pw_input, self.pw_confirm_input, self.question_combo, self.answer_input]:
            w.setStyleSheet("""
                background-color: #ffffff;
                border-radius: 20px;
                padding: 12px;
                font-size: 16px;
                border: 1px solid #ddd;
            """)
        add_field("새 학번", self.id_input)
        add_field("비밀번호", self.pw_input)
        add_field("비밀번호 확인", self.pw_confirm_input)
        add_field("비밀번호 찾기 질문", self.question_combo)
        add_field("질문 답변", self.answer_input)
        # 장애인등록증 첨부 추가
        self.cert_label = QLabel("장애인등록증 파일 없음")
        self.attach_btn = QPushButton("장애인등록증 첨부")
        self.attach_btn.setStyleSheet("""
            background-color: #eee; color: #333;
            border-radius: 12px; padding: 8px; font-size: 14px;
        """)
        self.attach_btn.clicked.connect(self.attach_file)
        form_layout.addWidget(self.cert_label)
        form_layout.addWidget(self.attach_btn)
        self.signup_btn = QPushButton("가입하기")
        self.signup_btn.setObjectName("signupBtn")
        self.signup_btn.setStyleSheet("""
            background-color: #99c2ff;
            color: black;
            border-radius: 20px;
            padding: 14px;
            font-size: 18px;
            font-weight: bold;
        """)
        self.signup_btn.clicked.connect(self.signup_check)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.signup_btn)
        outer_layout.addWidget(self.central_widget)

    def attach_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "장애인등록증 파일 선택", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            self.cert_file = file_name
            self.cert_label.setText(os.path.basename(file_name))
        else:
            self.cert_file = None
            self.cert_label.setText("장애인등록증 파일 없음")

    def signup_check(self):
        new_id = self.id_input.text().strip()
        new_pw = self.pw_input.text().strip()
        pw_confirm = self.pw_confirm_input.text().strip()
        question = self.question_combo.currentText()
        answer = self.answer_input.text().strip()

        if not new_id or not new_pw or not pw_confirm or not answer:
            QMessageBox.warning(self, "회원가입 오류", "모든 항목을 입력해주세요.")
            return
        if new_pw != pw_confirm:
            QMessageBox.warning(self, "회원가입 오류", "비밀번호 확인이 일치하지 않습니다.")
            return
        if get_user(new_id):
            QMessageBox.warning(self, "회원가입 오류", "이미 존재하는 학번입니다.")
            return
        cert_path = None
        if self.cert_file:
            upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            basename = f"{new_id}_" + os.path.basename(self.cert_file)
            dest = os.path.join(upload_dir, basename)
            try:
                shutil.copy2(self.cert_file, dest)
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
        self.bg_image = QLabel(self)
        bg_path = os.path.join(os.path.dirname(__file__), "HelpMeal.png")
        if os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            self.bg_image.pixmap = pixmap
            self.bg_image.setPixmap(pixmap)
            self.bg_image.setScaledContents(True)
            self.bg_image.setGeometry(0, 0, self.width(), self.height())
            opacity = QGraphicsOpacityEffect()
            opacity.setOpacity(0.3)
            self.bg_image.setGraphicsEffect(opacity)
            self.bg_image.lower()
        self.setStyleSheet("background-color: white;")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        self.central_widget = QWidget()
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.central_widget.setStyleSheet("""
            background-color: white;
            border-radius: 0px;
            padding: 16px;
            border: 1px solid #ccc;
        """)
        form_layout = QVBoxLayout(self.central_widget)
        form_layout.setSpacing(12)
        title_label = QLabel("비밀번호 찾기")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 20px;
            padding: 12px;
            font-size: 26px;
            border: 1px solid #ddd;
        """)
        title_label.setFont(QFont("Noto Sans KR", 24, QFont.Bold))
        form_layout.addWidget(title_label)
        form_layout.addSpacing(12)

        def add_field(label_text, widget):
            label = QLabel(label_text)
            label.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 20px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #ddd;
        """)
            label.setFont(QFont("Noto Sans KR", 12, QFont.Bold))
            form_layout.addWidget(label)
            form_layout.addWidget(widget)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("학번 입력")
        self.id_input.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 20px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #ddd;
        """)
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("질문에 대한 답변 입력")
        self.answer_input.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 20px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #ddd;
        """)
        self.question_display = QLabel("질문이 여기에 표시됩니다.")
        self.question_display.setFont(QFont("Noto Sans KR", 11))
        self.question_display.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 20px;
            padding: 12px;
            font-size: 16px;
            border: 1px solid #ddd;
        """)
        self.find_btn = QPushButton("확인")
        self.find_btn.setStyleSheet("""
            background-color: #99c2ff;
            color: black;
            border-radius: 20px;
            padding: 14px;
            font-size: 18px;
            font-weight: bold;
        """)
        self.find_btn.clicked.connect(self.check_answer)
        self.id_input.textChanged.connect(self.display_question)
        add_field("학번", self.id_input)
        form_layout.addWidget(self.question_display)
        add_field("답변", self.answer_input)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.find_btn)
        outer_layout.addWidget(self.central_widget)

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
        self.current_user_id = None
        super().__init__()
        self.setWindowTitle("HelpMeal")
        self.magnifier_btn = QPushButton("🔍 돋보기", self)
        self.magnifier_btn.setCheckable(True)
        self.magnifier_btn.setStyleSheet("font-size:18px; background:#eaf5ff; border-radius:10px; padding:6px 16px;")
        self.magnifier_btn.setFixedSize(100, 36)
        self.magnifier_btn.move(self.width()-130, 10)   # 윈도우 우측 상단 여백 10
        self.magnifier_btn.raise_()
        self.magnifier_btn.toggled.connect(self.toggle_magnifier)
        self.magnifier = Magnifier(self)
        self.resize(1200, 800)
        self.stack = QStackedWidget()
        self.history = []
        self.history_index = -1
        self.login_page = LoginPage(self)
        self.signup_page = SignupPage(self)
        self.password_page = PasswordFindPage(self)
        self.restaurant_page = RestaurantReservation(self)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)
        self.stack.addWidget(self.restaurant_page)
        self.stack.addWidget(self.password_page)
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
    def show_sidebar(self):
        self.sidebar_dialog = QDialog(self)
        self.sidebar_dialog.setWindowFlags(Qt.FramelessWindowHint)
        self.sidebar_dialog.setModal(True)
        self.sidebar_dialog.setStyleSheet("background-color: rgba(0, 0, 0, 70);")
        self.sidebar_dialog.setFixedSize(self.width(), self.height())
        sidebar_panel = QWidget(self.sidebar_dialog)
        sidebar_panel.setGeometry(0, 0, int(self.width() * 0.6), self.height())
        sidebar_panel.setStyleSheet("background-color: white;")
        sidebar_layout = QVBoxLayout(sidebar_panel)
        sidebar_layout.setContentsMargins(30, 30, 30, 30)
        sidebar_layout.setSpacing(20)
        user_label = QLabel(f"학번 : {self.current_user_id or '알 수 없음'}")
        user_label.setFont(QFont("Arial", 14, QFont.Bold))
        sidebar_layout.addWidget(user_label)
        logout_btn = QPushButton("로그아웃")
        logout_btn.clicked.connect(lambda: self.logout())
        sidebar_layout.addWidget(logout_btn)
        tts_checkbox = QCheckBox("TTS 음성안내")
        tts_checkbox.setChecked(AppSettings.tts_enabled)
        tts_checkbox.stateChanged.connect(lambda state: setattr(AppSettings, 'tts_enabled', state == Qt.Checked))
        sidebar_layout.addWidget(tts_checkbox)
        contrast_checkbox = QCheckBox("고대비 모드")
        contrast_checkbox.stateChanged.connect(self.toggle_contrast_global)
        sidebar_layout.addWidget(contrast_checkbox)
        profile_btn = QPushButton("개인정보 관리")
        profile_btn.clicked.connect(self.show_profile_dialog)
        sidebar_layout.addWidget(profile_btn)
        sidebar_layout.addStretch()
        overlay = QPushButton(self.sidebar_dialog)
        overlay.setGeometry(int(self.width() * 0.6), 0, int(self.width() * 0.4), self.height())
        overlay.setStyleSheet("background-color: transparent;")
        overlay.setCursor(Qt.PointingHandCursor)
        overlay.clicked.connect(self.sidebar_dialog.close)
        self.sidebar_dialog.show()
    def logout(self):
        self.sidebar_dialog.close()
        self.navigate_to(0)
    def toggle_contrast_global(self, state):
        if state == Qt.Checked:
            self.setStyleSheet("background-color: black; color: white;")
        else:
            self.setStyleSheet("")
    def show_profile_dialog(self):
        dlg = ProfileDialog(self.current_user_id, self)
        dlg.exec_()
        
    def resizeEvent(self, event):
    # 창 크기 변경 시 돋보기 버튼 위치 유지
        self.magnifier_btn.move(self.width()-130, 10)
        super().resizeEvent(event)

    def toggle_magnifier(self, checked):
        if checked:
            self.magnifier.start()
        else:
            self.magnifier.stop()

if __name__ == "__main__":
    init_db()
    AppSettings.tts_enabled = True
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
