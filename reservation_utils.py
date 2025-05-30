import sqlite3
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QLabel, QGridLayout, QTimeEdit,
    QDialogButtonBox, QMessageBox, QWidget, QHBoxLayout
)
from PyQt5.QtCore import QTimer, QTime, Qt
import datetime

DB_FILE = "reservations.db"


# DB 초기화 함수
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
    c.execute("""
       CREATE TABLE IF NOT EXISTS users (
           user_id TEXT PRIMARY KEY,
           password TEXT,
           security_question TEXT,
           security_answer TEXT
       )
       """)
    conn.commit()
    conn.close()


# 예약 중복 여부 확인 함수
def has_existing_reservation(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM reservations WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None


# 예약 정보 가져오기
def get_user_reservation(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM reservations WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result


# 좌석의 예약 정보 가져오기
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


# 현재 또는 미래에 예약된 좌석인지 확인
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


# 예약 저장 함수
def save_reservation(user_id, restaurant, seat, start_time, end_time):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO reservations (user_id, restaurant, seat, start_time, end_time)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, restaurant, seat, start_time.isoformat(), end_time.isoformat()))
    conn.commit()
    conn.close()


# 예약 취소 함수
def cancel_reservation(user_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM reservations WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# 예약 다이얼로그 창
class SeatReservationDialog(QDialog):
    def __init__(self, parent=None, restaurant_name="", user_id=""):
        super().__init__(parent)
        self.setWindowTitle(f"{restaurant_name} 좌석 예약")
        self.restaurant_name = restaurant_name
        self.user_id = user_id
        self.selected_seat = None
        self.seat_buttons = {}

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("좌석을 선택하세요 (1인 1좌석 예약 가능)"))
    
        cancel_btn = QPushButton("예약 취소")
        cancel_btn.clicked.connect(self.on_cancel_reservation)
        layout.addWidget(cancel_btn)
    
        current_res = get_user_reservation(self.user_id)
        if current_res:
            restaurant = current_res[2]
            seat = current_res[3]
            start_time = current_res[4][11:16]
            end_time = current_res[5][11:16]
            seat_info = f"현재 예약: {restaurant}, 좌석 {seat}, {start_time} ~ {end_time}"
        else:
            seat_info = "현재 예약 없음"
    
        self.reservation_label = QLabel(seat_info)
        layout.addWidget(self.reservation_label)
    
        # ✅ Tkinter 스타일 좌석 배치
        seat_layout = [
            "000  000  0000  00  00  000  00  000  00  00  00  000  00",
            "-                                               ",
            "000 000  000 00 000 000  000 000 000  000 000 000 00  000",
            "000 000  000 00 000 000  000 000 000  000 000 000 000 000",
            "-                                              ",
            "000 001  000 000 00 00   000 000 000  000 000 000 000 000",
            "000 000  000 000 00 00   000 000 000  000 000 000 000 000",
            "-                                                         ",
            "         000 000 000     00 000 000   000 000 000  0  000",
            "         000 000  00     00 000 000   00  000 000 000 001",
            "-                                                         ",
            "         00 000 00 00    00  00  00   000 000 000 000",
            "         00 000 00 00    000 000 00   000 000  00 001",
            "-                                                         ",
            "         00 00 00 000    00 000 00    000 000 000 00 ",
            "         00 00 00 00     00 000 00    00  00  000 0 ",
            "-                                                         ",
            "         00 00 00 00     00 00 00 00  00 00 00 00",
            "         00 00 00 00     01 00 00 00  00 00 00 00"
        ]
    
        grid = QGridLayout()
        self.seat_buttons = {}
    
        for r, line in enumerate(seat_layout):
            col = 0
            for c in line:
                seat_name = f"{r}-{col}"
                if c == "0":
                    btn = QPushButton()
                    btn.setFixedSize(30, 30)
                    btn.setStyleSheet("background-color: green;")
                    btn.setEnabled(False)
                    grid.addWidget(btn, r, col)
                elif c == "1":
                    btn = QPushButton()
                    btn.setFixedSize(30, 30)
                    btn.setIcon(QIcon("disable_seat.png"))
                    btn.setIconSize(QSize(30, 30))
                    btn.setStyleSheet("border: none; background-color: transparent;")  # ✅ 배경색 제거
                    btn.clicked.connect(lambda _, s=seat_name: self.try_reserve_seat(s))
                    self.seat_buttons[seat_name] = btn
                    grid.addWidget(btn, r, col)
                
                elif c == "-":
                    lbl = QLabel()
                    lbl.setFixedSize(30, 30)
                    lbl.setPixmap(QPixmap("empty.png").scaled(30, 30))
                    lbl.setStyleSheet("background-color: transparent;")  # ✅ 테이블 이미지
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
    
        layout.addLayout(grid)
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
                return "background-color: red;"  # 예약 사용시간(30분) 동안 빨간색
            elif now < start_time:
                return "background-color: gray;"  # 예약 대기(앞 시간 예약)
            else:
                return "background-color: green;"  # 예약 없음(지나감)
        else:
            return "background-color: green;"  # 예약 없음

    def update_seat_color(self, seat_name):
        btn = self.seat_buttons[seat_name]
        btn.setStyleSheet(self.seat_button_color(seat_name))
        # 이미 예약된 좌석은 비활성화
        if is_seat_reserved(self.restaurant_name, seat_name):
            btn.setEnabled(False)
        else:
            btn.setEnabled(True)

    def refresh_seat_colors(self):
        for seat_name in self.seat_buttons:
            self.update_seat_color(seat_name)

    def try_reserve_seat(self, seat_name):
        if has_existing_reservation(self.user_id):
            QMessageBox.warning(self, "예약 불가", "이미 예약된 좌석이 있습니다.")
            return
        if is_seat_reserved(self.restaurant_name, seat_name):
            QMessageBox.warning(self, "예약 불가", "이미 예약된 좌석입니다.")
            self.refresh_seat_colors()
            return

        self.selected_seat = seat_name
        self.open_time_dialog()

    def open_time_dialog(self):
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
                QMessageBox.warning(self, "오류", "현재 시간보다 이후를 선택하세요.")
                return

            # 현재 좌석이 그 시간에 이미 예약되어 있는지 다시 체크
            if is_seat_reserved(self.restaurant_name, self.selected_seat):
                QMessageBox.warning(self, "예약 불가", "이미 예약된 좌석입니다.")
                self.refresh_seat_colors()
                return

            end_time = start_time + datetime.timedelta(minutes=30)
            save_reservation(self.user_id, self.restaurant_name, self.selected_seat, start_time, end_time)
            dialog.accept()
            QMessageBox.information(self, "예약 완료", f"{start_time.strftime('%H:%M')}에 예약되었습니다.")
            self.reservation_label.setText(
                f"현재 예약: {self.selected_seat}, {start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}")
            self.refresh_seat_colors()

        buttons.accepted.connect(confirm_time)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()

    def on_cancel_reservation(self):
        res = get_user_reservation(self.user_id)
        if not res:
            QMessageBox.information(self, "예약 없음", "취소할 예약이 없습니다.")
            return
        reply = QMessageBox.question(self, "예약 취소", "예약을 취소하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            cancel_reservation(self.user_id)
            QMessageBox.information(self, "취소 완료", "예약이 취소되었습니다.")
            self.reservation_label.setText("현재 예약 없음")
            self.refresh_seat_colors()


# 예약을 처리하는 함수
def reserve_seat(parent, restaurant_name, user_id):
    init_db()  # DB 초기화
    dialog = SeatReservationDialog(parent, restaurant_name, user_id)
    dialog.exec_()

def save_user(user_id, password, question, answer):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (user_id, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
                  (user_id, password, question, answer))
        conn.commit()
        conn.close()

def get_user(user_id):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        return user
