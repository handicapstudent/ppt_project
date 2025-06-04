# reservation_utils.py

import sqlite3
import os
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QLabel, QGridLayout, QTimeEdit,
    QDialogButtonBox, QMessageBox, QWidget, QHBoxLayout, QScrollArea
)
from PyQt5.QtCore import QTimer, QTime, Qt, QSize
import datetime
from settings import AppSettings
from tts import speak
from functools import partial

DB_FILE = "reservations.db"

def init_db():
    """
    - reservations 테이블과 users 테이블을 초기화합니다.
    - users 테이블에 cert_path(TEXT) 및 cert_blob(BLOB) 컬럼이 없다면 ALTER TABLE로 추가합니다.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # ─── reservations 테이블 생성 ─────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        restaurant TEXT,
        seat TEXT,
        start_time TEXT,
        end_time TEXT
    )
    """)

    # ─── users 테이블 생성 (초기화 또는 기존 테이블이 없으면 새로 만듦) ────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        password TEXT,
        security_question TEXT,
        security_answer TEXT,
        cert_path TEXT,
        cert_blob BLOB
    )
    """)

    # ─── 기존 users 테이블에 cert_path, cert_blob 칼럼이 있는지 확인, 없으면 ALTER ─────
    c.execute("PRAGMA table_info(users)")
    existing_columns = [row[1] for row in c.fetchall()]
    if "cert_path" not in existing_columns:
        c.execute("ALTER TABLE users ADD COLUMN cert_path TEXT")
    if "cert_blob" not in existing_columns:
        c.execute("ALTER TABLE users ADD COLUMN cert_blob BLOB")

    conn.commit()
    conn.close()

# ──────────────────────────────────────────────────────────────────────────────────
def has_existing_reservation(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM reservations WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_user_reservation(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM reservations WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_seat_reservation(restaurant, seat):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM reservations WHERE restaurant = ? AND seat = ?",
        (restaurant, seat)
    )
    result = c.fetchone()
    conn.close()
    return result

def is_seat_reserved(restaurant, seat):
    now = datetime.datetime.now().isoformat()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "SELECT * FROM reservations WHERE restaurant = ? AND seat = ? AND end_time > ?",
        (restaurant, seat, now)
    )
    result = c.fetchone()
    conn.close()
    return result is not None

def save_reservation(user_id, restaurant, seat, start_time, end_time):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO reservations (user_id, restaurant, seat, start_time, end_time)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, restaurant, seat, start_time.isoformat(), end_time.isoformat()))
    conn.commit()
    conn.close()

def cancel_reservation(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM reservations WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# ──────────────────────────────────────────────────────────────────────────────────
class SeatReservationDialog(QDialog):
    def __init__(self, parent=None, restaurant_name="", user_id=""):
        super().__init__(parent)
        self.setWindowTitle(f"{restaurant_name} 좌석 예약")
        self.restaurant_name = restaurant_name
        self.user_id = user_id
        self.selected_seat = None
        self.seat_buttons = {}
        self.initUI()

    def get_seat_layout(self):
        if self.restaurant_name == "한빛식당":
            return ["00010001"]
        elif self.restaurant_name == "별빛식당":
            return ["111111", "------", "000000"]
        elif self.restaurant_name == "은하수식당":
            return ["000 000", " 1   1 ", "000 000"]
        else:
            return ["0000", "0 10", "0000"]

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("좌석을 선택하세요 (1인 1좌석 예약 가능)"))

        cancel_btn = QPushButton("예약 취소")
        cancel_btn.clicked.connect(self.on_cancel_reservation)
        layout.addWidget(cancel_btn)

        current_res = get_user_reservation(self.user_id)
        if current_res:
            restaurant, seat, start_time, end_time = current_res[2:6]
            seat_info = f"현재 예약: {restaurant}, 좌석 {seat}, {start_time[11:16]} ~ {end_time[11:16]}"
        else:
            seat_info = "현재 예약 없음"
        self.reservation_label = QLabel(seat_info)
        layout.addWidget(self.reservation_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout()
        container.setLayout(grid)

        seat_layout = self.get_seat_layout()
        for r, line in enumerate(seat_layout):
            col = 0
            for c in line:
                seat_name = f"{r}-{col}"
                if c == "0":
                    btn = QPushButton()
                    btn.setFixedSize(30, 30)
                    btn.setStyleSheet("background-color: #a0d6a0;")
                    btn.setEnabled(False)
                    grid.addWidget(btn, r, col)
                elif c == "1":
                    btn = QPushButton()
                    btn.setFixedSize(30, 30)
                    btn.setIcon(QIcon("disable_seat.png"))
                    btn.setIconSize(QSize(30, 30))
                    btn.setStyleSheet("border: none; background-color: #3cb043;")
                    btn.clicked.connect(partial(self.try_reserve_seat, seat_name))
                    self.seat_buttons[seat_name] = btn
                    grid.addWidget(btn, r, col)
                elif c == "-":
                    lbl = QLabel()
                    lbl.setFixedSize(30, 30)
                    lbl.setPixmap(QPixmap("empty.png").scaled(30, 30))
                    lbl.setStyleSheet("background-color: transparent;")
                    grid.addWidget(lbl, r, col)
                elif c == "3":
                    pillar = QLabel()
                    pillar.setFixedSize(30, 30)
                    pillar.setStyleSheet("background-color: black;")
                    grid.addWidget(pillar, r, col)
                elif c == " ":
                    blank = QLabel()
                    blank.setFixedSize(30, 30)
                    blank.setStyleSheet("background-color: white; border: none;")
                    grid.addWidget(blank, r, col)
                col += 1

        scroll.setWidget(container)
        layout.addWidget(scroll)

        self.setLayout(layout)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_seat_colors)
        self.refresh_timer.start(60000)
        self.refresh_seat_colors()

    def seat_button_color(self, seat_name):
        reservation = get_seat_reservation(self.restaurant_name, seat_name)
        now = datetime.datetime.now()
        if reservation:
            start_time = datetime.datetime.fromisoformat(reservation[4])
            end_time = datetime.datetime.fromisoformat(reservation[5])
            if start_time <= now < end_time:
                return "background-color: red;"
            elif now < start_time:
                return "background-color: gray;"
            else:
                return "background-color: green;"
        else:
            return "background-color: green;"

    def update_seat_color(self, seat_name):
        btn = self.seat_buttons[seat_name]
        btn.setStyleSheet(self.seat_button_color(seat_name))
        if is_seat_reserved(self.restaurant_name, seat_name):
            btn.setEnabled(False)
        else:
            btn.setEnabled(True)

    def refresh_seat_colors(self):
        for seat_name in self.seat_buttons:
            self.update_seat_color(seat_name)

    def try_reserve_seat(self, seat_name):
        if has_existing_reservation(self.user_id):
            if AppSettings.tts_enabled:
                speak("예약 불가: 이미 예약된 좌석이 있습니다.")
            QMessageBox.warning(self, "예약 불가", "이미 예약된 좌석이 있습니다.")
            return
        if is_seat_reserved(self.restaurant_name, seat_name):
            QMessageBox.warning(self, "예약 불가", "이미 예약된 좌석입니다.")
            self.refresh_seat_colors()
            return

        self.selected_seat = seat_name
        self.open_time_dialog()

    def open_time_dialog(self):
        if AppSettings.tts_enabled:
            speak("예약 시간을 선택하세요")

        dialog = QDialog(self)
        dialog.setWindowTitle("예약 시간 선택")
        layout = QVBoxLayout()

        time_edit = QTimeEdit()
        time_edit.setTime(QTime.currentTime())
        time_edit.setDisplayFormat("HH:mm")
        layout.addWidget(QLabel("예약 시작 시간을 선택하세요"))
        layout.addWidget(time_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)
        dialog.setLayout(layout)

        def confirm_time():
            start_time = datetime.datetime.combine(datetime.date.today(), time_edit.time().toPyTime())
            now = datetime.datetime.now()
            if start_time <= now:
                if AppSettings.tts_enabled:
                    speak("현재 시간보다 이후를 선택하세요")
                QMessageBox.warning(self, "오류", "현재 시간보다 이후를 선택하세요.")
                return

            if is_seat_reserved(self.restaurant_name, self.selected_seat):
                if AppSettings.tts_enabled:
                    speak("예약 불가: 이미 예약된 좌석입니다.")
                QMessageBox.warning(self, "예약 불가", "이미 예약된 좌석입니다.")
                self.refresh_seat_colors()
                return

            end_time = start_time + datetime.timedelta(minutes=30)
            save_reservation(self.user_id, self.restaurant_name, self.selected_seat, start_time, end_time)
            dialog.accept()
            if AppSettings.tts_enabled:
                speak(f"{start_time.strftime('%H:%M')}에 예약되었습니다.")
            QMessageBox.information(self, "예약 완료", f"{start_time.strftime('%H:%M')}에 예약되었습니다.")
            self.reservation_label.setText(
                f"현재 예약: {self.selected_seat}, {start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}"
            )
            self.refresh_seat_colors()

        buttons.accepted.connect(confirm_time)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()

    def on_cancel_reservation(self):
        res = get_user_reservation(self.user_id)
        if not res:
            if AppSettings.tts_enabled:
                speak("취소할 예약이 없습니다.")
            QMessageBox.information(self, "예약 없음", "취소할 예약이 없습니다.")
            return
        if AppSettings.tts_enabled:
            speak("예약을 취소하시겠습니까?")
        reply = QMessageBox.question(self, "예약 취소", "예약을 취소하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            cancel_reservation(self.user_id)
            if AppSettings.tts_enabled:
                speak("취소 완료: 예약이 취소되었습니다.")
            QMessageBox.information(self, "취소 완료", "예약이 취소되었습니다.")
            self.reservation_label.setText("현재 예약 없음")
            self.refresh_seat_colors()

# ──────────────────────────────────────────────────────────────────────────────────
def reserve_seat(parent, restaurant_name, user_id):
    init_db()  # DB 초기화
    dialog = SeatReservationDialog(parent, restaurant_name, user_id)
    dialog.exec_()

def save_user(user_id, password, question, answer, cert_path=None):
    """
    - cert_path가 주어지면 파일을 바이너리 모드로 읽어 cert_blob 칼럼에 저장합니다.
    - cert_path는 그대로 TEXT 칼럼에도 저장합니다.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # cert_blob 읽기
    cert_blob = None
    if cert_path and os.path.isfile(cert_path):
        try:
            with open(cert_path, "rb") as f:
                cert_blob = f.read()
        except Exception:
            cert_blob = None

    # UPSERT(INSERT OR REPLACE)
    c.execute("""
        INSERT OR REPLACE INTO users
            (user_id, password, security_question, security_answer, cert_path, cert_blob)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, password, question, answer, cert_path, cert_blob))

    conn.commit()
    conn.close()

def get_user(user_id):
    """
    - users 테이블에서 (user_id, password, question, answer, cert_path, cert_blob)을 반환합니다.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT user_id, password, security_question, security_answer, cert_path, cert_blob
        FROM users
        WHERE user_id = ?
    """, (user_id,))
    user = c.fetchone()
    conn.close()
    return user
