# 관리자.py

import sys
import sqlite3
from io import BytesIO
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QMessageBox, QHeaderView
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# 기존 예약 DB 경로
RESERVATION_DB_PATH = "reservations.db"
# 리뷰 DB 경로
REVIEW_DB_PATH = "review.db"

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("관리자 프로그램 (PyQt5)")
        self.setGeometry(100, 100, 1200, 700)

        self.tabs = QTabWidget()
        self.user_tab = QWidget()
        self.reservation_tab = QWidget()
        self.review_tab = QWidget()

        self.tabs.addTab(self.user_tab, "회원 관리")
        self.tabs.addTab(self.reservation_tab, "예약 관리")
        self.tabs.addTab(self.review_tab, "리뷰 관리")

        self.init_user_tab()
        self.init_reservation_tab()
        self.init_review_tab()

        self.setCentralWidget(self.tabs)

    # ──────────────────────────────────────────────────────────────────────────
    def init_user_tab(self):
        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # ─── 왼쪽: 검색 + 테이블 ───────────────────────────────────────────────
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("user_id 검색")
        btn_search = QPushButton("검색")
        btn_search.clicked.connect(self.search_users)
        btn_reload = QPushButton("새로고침")
        btn_reload.clicked.connect(self.load_users)
        btn_delete = QPushButton("선택 삭제")
        btn_delete.clicked.connect(self.delete_user)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_search)
        search_layout.addWidget(btn_reload)
        search_layout.addWidget(btn_delete)

        self.user_table = QTableWidget()
        # 5열: User ID, Password, Question, Answer, 이미지 미리보기
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            "User ID", "Password", "Security Question", "Answer", "이미지 미리보기"
        ])
        # “이미지 미리보기” 열 너비 고정
        self.user_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.user_table.setColumnWidth(4, 100)
        self.user_table.cellClicked.connect(self.on_user_table_click)

        left_layout.addLayout(search_layout)
        left_layout.addWidget(self.user_table)

        # ─── 오른쪽: 선택된 사용자의 이미지를 크게 보여주는 영역 ───────────────
        self.preview_label = QLabel("이미지 선택 시\n여기에 표시됩니다")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(240, 240)
        self.preview_label.setStyleSheet("border: 1px solid #aaa;")

        right_layout.addWidget(QLabel("선택된 사용자 이미지 미리보기:"))
        right_layout.addWidget(self.preview_label, alignment=Qt.AlignTop)
        right_layout.addStretch()

        layout.addLayout(left_layout, stretch=3)
        layout.addLayout(right_layout, stretch=1)

        self.user_tab.setLayout(layout)
        self.load_users()

    def load_users(self):
        """
        - users 테이블에서 cert_blob까지 함께 읽어와 테이블에 표시합니다.
        - cert_blob이 있으면 썸네일로, 없으면 “없음”을 표시합니다.
        """
        conn = sqlite3.connect(RESERVATION_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, password, security_question, security_answer, cert_blob
            FROM users
        """)
        rows = cursor.fetchall()
        conn.close()

        self.user_table.setRowCount(len(rows))
        for i, (uid, pw, q, a, blob) in enumerate(rows):
            self.user_table.setItem(i, 0, QTableWidgetItem(uid))
            self.user_table.setItem(i, 1, QTableWidgetItem(pw))
            self.user_table.setItem(i, 2, QTableWidgetItem(q))
            self.user_table.setItem(i, 3, QTableWidgetItem(a))

            if blob:
                pixmap = QPixmap()
                pixmap.loadFromData(blob)
                thumb = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumb_label = QLabel()
                thumb_label.setPixmap(thumb)
                thumb_label.setAlignment(Qt.AlignCenter)
                self.user_table.setCellWidget(i, 4, thumb_label)
            else:
                no_label = QLabel("없음")
                no_label.setAlignment(Qt.AlignCenter)
                self.user_table.setCellWidget(i, 4, no_label)

    def search_users(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_users()
            return

        conn = sqlite3.connect(RESERVATION_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, password, security_question, security_answer, cert_blob
            FROM users
            WHERE user_id LIKE ?
        """, (f"%{keyword}%",))
        rows = cursor.fetchall()
        conn.close()

        self.user_table.setRowCount(len(rows))
        for i, (uid, pw, q, a, blob) in enumerate(rows):
            self.user_table.setItem(i, 0, QTableWidgetItem(uid))
            self.user_table.setItem(i, 1, QTableWidgetItem(pw))
            self.user_table.setItem(i, 2, QTableWidgetItem(q))
            self.user_table.setItem(i, 3, QTableWidgetItem(a))
            if blob:
                pixmap = QPixmap()
                pixmap.loadFromData(blob)
                thumb = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                thumb_label = QLabel()
                thumb_label.setPixmap(thumb)
                thumb_label.setAlignment(Qt.AlignCenter)
                self.user_table.setCellWidget(i, 4, thumb_label)
            else:
                no_label = QLabel("없음")
                no_label.setAlignment(Qt.AlignCenter)
                self.user_table.setCellWidget(i, 4, no_label)

    def delete_user(self):
        selected = self.user_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "경고", "삭제할 사용자를 선택하세요.")
            return
        user_id = self.user_table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "확인", f"정말로 '{user_id}' 사용자를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(RESERVATION_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            self.load_users()
            self.preview_label.setText("이미지 선택 시\n여기에 표시됩니다")
            self.preview_label.setPixmap(QPixmap())

    def on_user_table_click(self, row, column):
        """
        - 테이블의 특정 행(row) 클릭 시, 해당 user_id의 cert_blob을 DB에서 다시 가져와 우측에 확대 표시합니다.
        """
        user_id = self.user_table.item(row, 0).text()
        conn = sqlite3.connect(RESERVATION_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT cert_blob FROM users WHERE user_id = ?", (user_id,))
        record = cursor.fetchone()
        conn.close()

        if record and record[0]:
            blob = record[0]
            pixmap = QPixmap()
            pixmap.loadFromData(blob)
            scaled_pix = pixmap.scaled(220, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pix)
        else:
            self.preview_label.setText("이미지 없음")
            self.preview_label.setPixmap(QPixmap())

    # ──────────────────────────────────────────────────────────────────────────
    def init_reservation_tab(self):
        layout = QVBoxLayout()
        self.res_table = QTableWidget()
        layout.addWidget(self.res_table)

        btn_layout = QHBoxLayout()
        self.res_search_input = QLineEdit()
        self.res_search_input.setPlaceholderText("user_id로 예약 검색")
        btn_res_search = QPushButton("검색")
        btn_res_search.clicked.connect(self.search_reservations)
        btn_res_reload = QPushButton("새로고침")
        btn_res_reload.clicked.connect(self.load_reservations)
        btn_res_delete = QPushButton("선택 예약 삭제")
        btn_res_delete.clicked.connect(self.delete_reservation)

        btn_layout.addWidget(self.res_search_input)
        btn_layout.addWidget(btn_res_search)
        btn_layout.addWidget(btn_res_reload)
        btn_layout.addWidget(btn_res_delete)

        layout.addLayout(btn_layout)
        self.reservation_tab.setLayout(layout)
        self.load_reservations()

    def load_reservations(self):
        conn = sqlite3.connect(RESERVATION_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, restaurant, seat, start_time, end_time
            FROM reservations
        """)
        rows = cursor.fetchall()
        conn.close()

        self.res_table.setRowCount(len(rows))
        self.res_table.setColumnCount(6)
        self.res_table.setHorizontalHeaderLabels(
            ["ID", "User ID", "Restaurant", "Seat", "Start Time", "End Time"]
        )
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.res_table.setItem(i, j, QTableWidgetItem(str(val)))

    def search_reservations(self):
        keyword = self.res_search_input.text().strip()
        if not keyword:
            self.load_reservations()
            return

        conn = sqlite3.connect(RESERVATION_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, restaurant, seat, start_time, end_time
            FROM reservations
            WHERE user_id LIKE ?
        """, (f"%{keyword}%",))
        rows = cursor.fetchall()
        conn.close()

        self.res_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.res_table.setItem(i, j, QTableWidgetItem(str(val)))

    def delete_reservation(self):
        selected = self.res_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "경고", "삭제할 예약을 선택하세요.")
            return
        res_id = self.res_table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "확인", f"정말로 예약 {res_id}를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(RESERVATION_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reservations WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
            self.load_reservations()

    # ──────────────────────────────────────────────────────────────────────────
    def init_review_tab(self):
        layout = QVBoxLayout()
        self.review_table = QTableWidget()
        layout.addWidget(self.review_table)

        btn_layout = QHBoxLayout()
        self.review_search_input = QLineEdit()
        self.review_search_input.setPlaceholderText("user_id로 리뷰 검색")
        btn_review_search = QPushButton("검색")
        btn_review_search.clicked.connect(self.search_reviews)
        btn_review_reload = QPushButton("새로고침")
        btn_review_reload.clicked.connect(self.load_reviews)
        btn_review_delete = QPushButton("선택 리뷰 삭제")
        btn_review_delete.clicked.connect(self.delete_review)

        btn_layout.addWidget(self.review_search_input)
        btn_layout.addWidget(btn_review_search)
        btn_layout.addWidget(btn_review_reload)
        btn_layout.addWidget(btn_review_delete)

        layout.addLayout(btn_layout)
        self.review_tab.setLayout(layout)
        self.load_reviews()

    def load_reviews(self):
        conn = sqlite3.connect(REVIEW_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, review, rating, timestamp
            FROM reviews
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        self.review_table.setRowCount(len(rows))
        self.review_table.setColumnCount(5)
        self.review_table.setHorizontalHeaderLabels(
            ["ID", "User ID", "Review Text", "Rating", "Timestamp"]
        )
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.review_table.setItem(i, j, QTableWidgetItem(str(val)))

    def search_reviews(self):
        keyword = self.review_search_input.text().strip()
        if not keyword:
            self.load_reviews()
            return

        conn = sqlite3.connect(REVIEW_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, review, rating, timestamp
            FROM reviews
            WHERE user_id LIKE ?
            ORDER BY timestamp DESC
        """, (f"%{keyword}%",))
        rows = cursor.fetchall()
        conn.close()

        self.review_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.review_table.setItem(i, j, QTableWidgetItem(str(val)))

    def delete_review(self):
        selected = self.review_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "경고", "삭제할 리뷰를 선택하세요.")
            return
        review_id = self.review_table.item(selected, 0).text()
        confirm = QMessageBox.question(
            self, "확인", f"정말로 리뷰 {review_id}를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(REVIEW_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE id=?", (review_id,))
            conn.commit()
            conn.close()
            self.load_reviews()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdminApp()
    window.show()
    sys.exit(app.exec_())
