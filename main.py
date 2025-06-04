# main.py
import os
import sys
import shutil
from restaurant_ui_relayout import RestaurantReservation
from reservation_utils import init_db, get_user, save_user
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QLineEdit, QDialog, QCheckBox, QFrame, QComboBox, QSizePolicy,
    QGraphicsOpacityEffect, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
from Magnifier import Magnifier
from settings import AppSettings
from tts import speak

# ──────────────────────────────────────────────────────────────────────────────
# 메시지박스를 항상 기본 스타일(흰배경·검정텍스트)로 띄우는 헬퍼 함수
def show_messagebox(message_type, title, text):
    box = QMessageBox()
    box.setWindowTitle(title)
    box.setText(text)
    box.setStyleSheet("")  # 고대비 모드와 상관없이 기본 스타일 유지

    if message_type == 'info':
        box.setIcon(QMessageBox.Information)
    elif message_type == 'warn':
        box.setIcon(QMessageBox.Warning)
    elif message_type == 'error':
        box.setIcon(QMessageBox.Critical)
    else:
        box.setIcon(QMessageBox.NoIcon)

    box.setWindowModality(Qt.ApplicationModal)
    box.exec_()
# ──────────────────────────────────────────────────────────────────────────────


class ProfileDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("개인정보 관리")
        self.setFixedSize(400, 550)
        self.setModal(True)
        user = get_user(user_id)
        # user = (user_id, password, question, answer, cert_path, cert_blob)

        layout = QVBoxLayout()
        self.id_label = QLabel(f"학번: {user[0]}")
        layout.addWidget(self.id_label)

        # 비밀번호 변경 입력
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호 변경 (입력 시 변경)")
        self.pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pw_input)

        # 현재 이미지(첨부 파일) 미리보기: cert_blob이 있으면 QPixmap으로 변환
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(200, 200)
        self.image_preview.setStyleSheet("border: 1px solid #ccc;")
        layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        # DB에 저장된 blob이 있으면 미리보기
        if user and user[5]:  # cert_blob이 존재하면
            pixmap = QPixmap()
            pixmap.loadFromData(user[5])
            self.image_preview.setPixmap(pixmap.scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.image_preview.setText("첨부된 이미지 없음")
            self.image_preview.setAlignment(Qt.AlignCenter)

        self.cert_label = QLabel()
        self.status_label = QLabel()
        self.attach_btn = QPushButton("이미지 변경 (첨부)")
        self.attach_btn.clicked.connect(self.attach_file)
        self.selected_file = None

        cert_path = user[4] if user else None
        if not cert_path:
            self.status_label.setText("장애인 인증 현황: 인증 안 됨")
        else:
            self.status_label.setText("장애인 인증 현황: 인증 중")
            file_name = os.path.basename(cert_path)
            self.cert_label.setText(f"첨부 파일: {file_name}")

        layout.addWidget(self.status_label)
        layout.addWidget(self.cert_label)
        layout.addWidget(self.attach_btn)

        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def attach_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "장애인등록증 파일 선택", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_name:
            self.selected_file = file_name
            self.cert_label.setText(os.path.basename(file_name))

    def save_changes(self):
        user = get_user(self.user_id)
        new_pw = self.pw_input.text() if self.pw_input.text() else user[1]
        question = user[2]
        answer = user[3]
        cert_path = user[4] if user else None

        # 선택된 새 파일이 있으면 uploads/ 디렉토리에 복사
        if self.selected_file:
            upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            basename = f"{self.user_id}_" + os.path.basename(self.selected_file)
            dest = os.path.join(upload_dir, basename)
            shutil.copy2(self.selected_file, dest)
            cert_path = dest

        # save_user가 cert_blob까지 동시에 업데이트
        save_user(self.user_id, new_pw, question, answer, cert_path)
        show_messagebox('info', "저장 완료", "개인정보가 저장되었습니다.")
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

        # 배경 이미지 또는 기본 배경색
        self.bg_label = QLabel(self)
        image_path = os.path.join(os.path.dirname(__file__), "충북대학교 정문.jpg")
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self.bg_label.setPixmap(pixmap)
        else:
            self.bg_label.setStyleSheet("background-color: #f0f0f0;")
        self.bg_label.setScaledContents(True)
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()

        # 중앙 위젯(투명도 배경)
        self.central_widget = QWidget(self)
        central_layout = QVBoxLayout(self.central_widget)
        central_layout.setContentsMargins(80, 60, 80, 60)
        self.central_widget.setFixedSize(720, 600)
        self.central_widget.move(
            (self.width() - 720) // 2, (self.height() - 600) // 2
        )
        self.central_widget.setStyleSheet(
            "background-color: rgba(255, 255, 255, 230); border-radius: 32px;"
        )

        # 타이틀 영역
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(16)

        self.logo_label = QLabel()
        self.logo_label.setStyleSheet("background: transparent;")
        logo_path = os.path.join(os.path.dirname(__file__), "HelpMeal.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(logo_pixmap)

        self.title_text = QLabel("HelpMeal")
        self.title_text.setFont(QFont("Arial", 40, QFont.Bold))
        self.title_text.setStyleSheet("color: #333333; background: transparent;")
        title_layout.addStretch()
        title_layout.addWidget(self.logo_label)
        title_layout.addWidget(self.title_text)
        title_layout.addStretch()
        central_layout.addWidget(title_container)

        # ID / Password 입력 필드
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID")
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("Password")
        self.pw_input.setEchoMode(QLineEdit.Password)

        for widget in [self.id_input, self.pw_input]:
            widget.setFont(QFont("Arial", 24))
            widget.setStyleSheet(
                "QLineEdit { background-color: white; color: black; padding: 16px;"
                " border: 2px solid #ccc; border-radius: 16px; }"
            )
            central_layout.addWidget(widget)

        # 로그인 버튼
        self.login_btn = QPushButton("로그인")
        self.login_btn.setFont(QFont("Arial", 24, QFont.Bold))
        self.login_btn.clicked.connect(self.login_check)
        self.login_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 20px; "
            "border-radius: 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        central_layout.addWidget(self.login_btn)

        # 회원가입 / 비밀번호 찾기 링크
        link_layout = QHBoxLayout()
        self.signup_btn = QPushButton("회원가입")
        self.pw_find_btn = QPushButton("비밀번호 찾기")
        for btn in [self.signup_btn, self.pw_find_btn]:
            btn.setFont(QFont("Noto Sans KR", 18))
            btn.setFlat(True)
            btn.setStyleSheet(
                "QPushButton { color: #555; text-decoration: underline; }"
                "QPushButton:hover { color: #000; }"
            )
            btn.setCursor(Qt.PointingHandCursor)

        self.signup_btn.clicked.connect(lambda: self.main_window.navigate_to(1))
        self.pw_find_btn.clicked.connect(lambda: self.main_window.navigate_to(3))

        link_layout.addWidget(self.signup_btn)
        link_layout.addStretch()
        link_layout.addWidget(self.pw_find_btn)

        # 고대비 / TTS 체크박스
        accessibility_layout = QHBoxLayout()
        self.contrast_checkbox = QCheckBox("고대비 모드")
        self.contrast_checkbox.setObjectName("contrast_checkbox")
        self.contrast_checkbox.setFont(QFont("Noto Sans KR", 18))
        self.contrast_checkbox.setChecked(False)
        self.contrast_checkbox.stateChanged.connect(self.toggle_contrast)

        self.tts_checkbox = QCheckBox("TTS 음성안내 활성화")
        self.tts_checkbox.setFont(QFont("Noto Sans KR", 18))
        self.tts_checkbox.setChecked(True)
        self.tts_checkbox.stateChanged.connect(
            lambda state: setattr(AppSettings, "tts_enabled", state == Qt.Checked)
        )

        accessibility_layout.addWidget(self.contrast_checkbox)
        accessibility_layout.addWidget(self.tts_checkbox)

        central_layout.addLayout(accessibility_layout)
        central_layout.addLayout(link_layout)

        # Enter 키로 로그인
        self.id_input.returnPressed.connect(self.login_btn.click)
        self.pw_input.returnPressed.connect(self.login_btn.click)

    def apply_high_contrast(self):
        # 로그인 페이지 전역 텍스트/배경 변경
        self.central_widget.setStyleSheet(
            "background-color: black; border-radius: 32px;"
        )
        self.bg_label.setStyleSheet("background-color: black;")
        self.title_text.setStyleSheet("color: white; background: transparent;")
        for widget in [self.id_input, self.pw_input]:
            widget.setStyleSheet(
                "QLineEdit { background-color: white; color: black; padding: 16px;"
                " border: 2px solid white; border-radius: 16px; }"
            )
        self.login_btn.setStyleSheet(
            "QPushButton { background-color: #333; color: white; padding: 20px; "
            "border-radius: 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #555; }"
        )
        self.signup_btn.setStyleSheet(
            "QPushButton { color: white; text-decoration: underline; }"
            "QPushButton:hover { color: #ccc; }"
        )
        self.pw_find_btn.setStyleSheet(
            "QPushButton { color: white; text-decoration: underline; }"
            "QPushButton:hover { color: #ccc; }"
        )
        self.contrast_checkbox.setStyleSheet("QCheckBox { color: white; }")
        self.tts_checkbox.setStyleSheet("QCheckBox { color: white; }")

    def reset_contrast(self):
        # 로그인 페이지 기본 모드로 복원
        self.central_widget.setStyleSheet(
            "background-color: rgba(255, 255, 255, 230); border-radius: 32px;"
        )
        self.bg_label.setStyleSheet("background-color: #f0f0f0;")
        self.title_text.setStyleSheet("color: #333333; background: transparent;")
        for widget in [self.id_input, self.pw_input]:
            widget.setStyleSheet(
                "QLineEdit { background-color: white; color: black; padding: 16px;"
                " border: 2px solid #ccc; border-radius: 16px; }"
            )
        self.login_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; padding: 20px; "
            "border-radius: 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.signup_btn.setStyleSheet(
            "QPushButton { color: #555; text-decoration: underline; }"
            "QPushButton:hover { color: #000; }"
        )
        self.pw_find_btn.setStyleSheet(
            "QPushButton { color: #555; text-decoration: underline; }"
            "QPushButton:hover { color: #000; }"
        )
        self.contrast_checkbox.setStyleSheet("QCheckBox { color: black; }")
        self.tts_checkbox.setStyleSheet("QCheckBox { color: black; }")

    def toggle_contrast(self, state):
        AppSettings.contrast_enabled = (state == Qt.Checked)

        # 로그인 페이지 자체에 적용하거나 해제
        if state == Qt.Checked:
            self.apply_high_contrast()
        else:
            self.reset_contrast()

        # 전역 고대비 반영
        self.main_window.toggle_contrast_global(state)

    def login_check(self):
        user_id = self.id_input.text()
        password = self.pw_input.text()
        user = get_user(user_id)
        if user and user[1] == password:
            if AppSettings.tts_enabled:
                speak("로그인 되셨습니다.")
            # 로그인 성공 시 입력 필드 비우기
            self.id_input.clear()
            self.pw_input.clear()

            self.main_window.current_user_id = user_id
            self.main_window.restaurant_page.set_user(user_id)

            # 고대비 체크 상태를 다시 확인하여 전역 반영
            if self.contrast_checkbox.isChecked():
                self.main_window.toggle_contrast_global(Qt.Checked)
            else:
                self.main_window.toggle_contrast_global(Qt.Unchecked)

            self.main_window.navigate_to(2)
        else:
            if AppSettings.tts_enabled:
                speak("학번 또는 비밀번호가 틀렸습니다.")
            show_messagebox('warn', "로그인 실패", "학번 또는 비밀번호가 틀렸습니다.")


class SignupPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.cert_file = None
        self.initUI()

    def apply_high_contrast(self):
        # 고대비 모드용 스타일
        self.central_widget.setStyleSheet(
            "background-color: black; color: black; border: 1px solid white;"
        )
        self.setStyleSheet(
            "QLabel, QLineEdit, QComboBox { background-color: white; color: black; border: 1px solid white; }"
            "QPushButton { background-color: #222; color: white; border: 1px solid white; }"
        )

    def reset_contrast(self):
        # 기본 모드용 스타일
        self.central_widget.setStyleSheet(
            "background-color: white; border: 1px solid #ccc;"
        )
        self.setStyleSheet("")

    def initUI(self):
        self.setStyleSheet("background-color: white;")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.central_widget = QWidget()
        self.central_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.central_widget.setStyleSheet(
            "background-color: white; border-radius: 0px; padding: 16px; border: 1px solid #ccc;"
        )
        form_layout = QVBoxLayout(self.central_widget)
        form_layout.setSpacing(12)

        title_label = QLabel("회원가입")
        title_label.setStyleSheet(
            "background-color: #ffffff; border-radius: 20px; padding: 12px; "
            "font-size: 24px; border: 1px solid #ddd;"
        )
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Noto Sans KR", 24, QFont.Bold))
        form_layout.addWidget(title_label)
        form_layout.addSpacing(12)

        def add_field(label_text, widget):
            label = QLabel(label_text)
            label.setFont(QFont("Noto Sans KR", 12, QFont.Bold))
            label.setStyleSheet(
                "background-color: #ffffff; border-radius: 20px; padding: 12px; "
                "font-size: 16px; border: 1px solid #ddd;"
            )
            form_layout.addWidget(label)
            form_layout.addWidget(widget)

        self.id_input = QLineEdit()
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(QLineEdit.Password)
        self.pw_confirm_input = QLineEdit()
        self.pw_confirm_input.setEchoMode(QLineEdit.Password)

        self.question_combo = QComboBox()
        self.question_combo.addItems(
            [
                "가장 좋아하는 음식은?",
                "출신 초등학교는?",
                "어릴 적 별명은?",
                "기억에 남는 선생님 이름은?",
                "가장 친한 친구 이름은?",
            ]
        )
        self.answer_input = QLineEdit()

        for w in [
            self.id_input,
            self.pw_input,
            self.pw_confirm_input,
            self.question_combo,
            self.answer_input,
        ]:
            w.setStyleSheet(
                "background-color: #ffffff; border-radius: 20px; padding: 12px; "
                "font-size: 16px; border: 1px solid #ddd;"
            )

        add_field("새 학번", self.id_input)
        add_field("비밀번호", self.pw_input)
        add_field("비밀번호 확인", self.pw_confirm_input)
        add_field("비밀번호 찾기 질문", self.question_combo)
        add_field("질문 답변", self.answer_input)

        # 장애인등록증 첨부
        self.cert_label = QLabel("장애인등록증 파일 없음")
        self.attach_btn = QPushButton("장애인등록증 첨부")
        self.attach_btn.setStyleSheet(
            "background-color: #eee; color: #333; border-radius: 12px; padding: 8px; font-size: 14px;"
        )
        self.attach_btn.clicked.connect(self.attach_file)
        form_layout.addWidget(self.cert_label)
        form_layout.addWidget(self.attach_btn)

        self.signup_btn = QPushButton("가입하기")
        self.signup_btn.setObjectName("signupBtn")
        self.signup_btn.setStyleSheet(
            "background-color: #99c2ff; color: black; border-radius: 20px; "
            "padding: 14px; font-size: 18px; font-weight: bold;"
        )
        self.signup_btn.clicked.connect(self.signup_check)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.signup_btn)

        outer_layout.addWidget(self.central_widget)

    def attach_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "장애인등록증 파일 선택", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
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
            show_messagebox('warn', "회원가입 오류", "모든 항목을 입력해주세요.")
            return
        if new_pw != pw_confirm:
            show_messagebox('warn', "회원가입 오류", "비밀번호 확인이 일치하지 않습니다.")
            return
        if get_user(new_id):
            show_messagebox('warn', "회원가입 오류", "이미 존재하는 학번입니다.")
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
                show_messagebox('warn', "첨부 오류", f"파일 복사 실패: {e}")
                return

        save_user(new_id, new_pw, question, answer, cert_path)
        show_messagebox('info', "회원가입 성공", f"{new_id}님, 회원가입이 완료되었습니다.")

        # 회원가입 성공 후 입력 필드 초기화
        self.id_input.clear()
        self.pw_input.clear()
        self.pw_confirm_input.clear()
        self.answer_input.clear()
        self.question_combo.setCurrentIndex(0)
        self.cert_label.setText("장애인등록증 파일 없음")
        self.cert_file = None

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
        self.central_widget.setStyleSheet(
            "background-color: white; border-radius: 0px; padding: 16px; border: 1px solid #ccc;"
        )
        form_layout = QVBoxLayout(self.central_widget)
        form_layout.setSpacing(12)

        title_label = QLabel("비밀번호 찾기")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "background-color: #ffffff; border-radius: 20px; padding: 12px; "
            "font-size: 26px; border: 1px solid #ddd;"
        )
        title_label.setFont(QFont("Noto Sans KR", 24, QFont.Bold))
        form_layout.addWidget(title_label)
        form_layout.addSpacing(12)

        def add_field(label_text, widget):
            label = QLabel(label_text)
            label.setStyleSheet(
                "background-color: #ffffff; border-radius: 20px; padding: 12px; "
                "font-size: 16px; border: 1px solid #ddd;"
            )
            label.setFont(QFont("Noto Sans KR", 12, QFont.Bold))
            form_layout.addWidget(label)
            form_layout.addWidget(widget)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("학번 입력")
        self.id_input.setStyleSheet(
            "background-color: #ffffff; border-radius: 20px; padding: 12px; "
            "font-size: 16px; border: 1px solid #ddd;"
        )
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("질문에 대한 답변 입력")
        self.answer_input.setStyleSheet(
            "background-color: #ffffff; border-radius: 20px; padding: 12px; "
            "font-size: 16px; border: 1px solid #ddd;"
        )

        self.question_display = QLabel("질문이 여기에 표시됩니다.")
        self.question_display.setFont(QFont("Noto Sans KR", 11))
        self.question_display.setStyleSheet(
            "background-color: #ffffff; border-radius: 20px; padding: 12px; "
            "font-size: 16px; border: 1px solid #ddd;"
        )

        self.find_btn = QPushButton("확인")
        self.find_btn.setStyleSheet(
            "background-color: #99c2ff; color: black; border-radius: 20px; "
            "padding: 14px; font-size: 18px; font-weight: bold;"
        )
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
            show_messagebox('info', "비밀번호", f"비밀번호는: {user[1]}")
            self.main_window.navigate_to(0)
        else:
            show_messagebox('warn', "오류", "답변이 일치하지 않습니다.")

    def apply_high_contrast(self):
        self.central_widget.setStyleSheet(
            "background-color: black; color: black; border: 1px solid white;"
        )
        self.setStyleSheet(
            "QLabel, QLineEdit { background-color: white; color: black; border: 1px solid white; }"
            "QPushButton { background-color: #222; color: white; border: 1px solid white; }"
        )

    def reset_contrast(self):
        self.central_widget.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        self.setStyleSheet("")


class MainWindow(QWidget):
    def __init__(self):
        self.current_user_id = None
        super().__init__()
        self.setWindowTitle("HelpMeal")
        self.resize(1200, 800)

        # 스택 위젯 + 페이지들
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

        # 뒤/앞 버튼
        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(32, 32)
        self.back_btn.setFlat(True)
        self.back_btn.clicked.connect(self.go_back)

        self.forward_btn = QPushButton(">")
        self.forward_btn.setFixedSize(32, 32)
        self.forward_btn.setFlat(True)
        self.forward_btn.clicked.connect(self.go_forward)

        # 돋보기 버튼
        self.magnifier_btn = QPushButton("🔍")
        self.magnifier_btn.setCheckable(True)
        self.magnifier_btn.setFixedSize(36, 36)
        self.magnifier_btn.setStyleSheet("font-size:18px; background:#f0f0f0; border-radius:8px;")
        self.magnifier_btn.toggled.connect(self.toggle_magnifier)
        self.magnifier = Magnifier(self)

        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        # 돋보기 → 뒤 → 앞
        nav_layout.addWidget(self.magnifier_btn)
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.setContentsMargins(10, 10, 10, 0)

        # QStacked + 네비게이션을 오버레이 방식으로
        container = QWidget(self)
        container.setStyleSheet("background-color: transparent;")
        container.setGeometry(0, 0, 1200, 800)

        self.stack.setParent(container)
        self.stack.setGeometry(0, 0, 1200, 800)

        nav_frame = QFrame(container)
        nav_frame.setGeometry(1200 - 130, 10, 120, 40)
        nav_layout_in_frame = QHBoxLayout(nav_frame)
        nav_layout_in_frame.setContentsMargins(0, 0, 0, 0)
        nav_layout_in_frame.setSpacing(10)
        nav_layout_in_frame.insertWidget(0, self.magnifier_btn)
        nav_layout_in_frame.addWidget(self.back_btn)
        nav_layout_in_frame.addWidget(self.forward_btn)

        self.setLayout(QVBoxLayout())  # 빈 레이아웃
        self.navigate_to(0)

    def toggle_magnifier(self, checked):
        if checked:
            self.magnifier.start()
        else:
            self.magnifier.stop()

    def navigate_to(self, index):
        self.stack.setCurrentIndex(index)
        # 인덱스 전환 시 입력란 초기화
        if index == 0:  # LoginPage
            self.login_page.id_input.clear()
            self.login_page.pw_input.clear()
        elif index == 1:  # SignupPage
            self.signup_page.id_input.clear()
            self.signup_page.pw_input.clear()
            self.signup_page.pw_confirm_input.clear()
            self.signup_page.answer_input.clear()
            self.signup_page.question_combo.setCurrentIndex(0)
            self.signup_page.cert_label.setText("장애인등록증 파일 없음")
            self.signup_page.cert_file = None

        self.history = self.history[: self.history_index + 1]
        self.history.append(index)
        self.history_index += 1

    def go_back(self):
        if hasattr(self, "sidebar_dialog") and self.sidebar_dialog.isVisible():
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
        AppSettings.contrast_enabled = (state == Qt.Checked)

        if state == Qt.Checked:
            # 고대비 스타일
            self.setStyleSheet(
                """
                QWidget {
                    background-color: black;
                    color: white;
                }
                QPushButton {
                    background-color: #333;
                    color: white;
                    border: 1px solid white;
                }
                QLabel, QCheckBox, QLineEdit {
                    color: white;
                    background-color: #222;
                }
                QLineEdit {
                    border: 1px solid white;
                }
                """
            )
            self.back_btn.setStyleSheet(
                "background-color: black; color: white; border: 1px solid white;"
            )
            self.forward_btn.setStyleSheet(
                "background-color: black; color: white; border: 1px solid white;"
            )
            self.restaurant_page.apply_high_contrast()
            self.signup_page.apply_high_contrast()
            self.password_page.apply_high_contrast()
        else:
            # 기본 스타일로 리셋
            self.setStyleSheet("")
            self.back_btn.setStyleSheet("")
            self.forward_btn.setStyleSheet("")
            self.restaurant_page.reset_contrast()
            self.signup_page.reset_contrast()
            self.password_page.reset_contrast()


if __name__ == "__main__":
    init_db()
    AppSettings.contrast_enabled = False
    AppSettings.tts_enabled = True
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
