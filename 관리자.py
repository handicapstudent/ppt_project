import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QMessageBox
)

DB_PATH = "reservations.db"

class AdminApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("관리자 프로그램 (PyQt5)")
        self.setGeometry(100, 100, 1000, 600)

        self.tabs = QTabWidget()
        self.user_tab = QWidget()
        self.reservation_tab = QWidget()

        self.tabs.addTab(self.user_tab, "회원 관리")
        self.tabs.addTab(self.reservation_tab, "예약 관리")

        self.init_user_tab()
        self.init_reservation_tab()

        self.setCentralWidget(self.tabs)

    def init_user_tab(self):
        layout = QVBoxLayout()
        self.user_table = QTableWidget()
        layout.addWidget(self.user_table)

        btn_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("user_id 검색")
        btn_layout.addWidget(self.search_input)

        btn_search = QPushButton("검색")
        btn_search.clicked.connect(self.search_users)
        btn_layout.addWidget(btn_search)

        btn_reload = QPushButton("새로고침")
        btn_reload.clicked.connect(self.load_users)
        btn_layout.addWidget(btn_reload)

        btn_delete = QPushButton("선택 삭제")
        btn_delete.clicked.connect(self.delete_user)
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)
        self.user_tab.setLayout(layout)
        self.load_users()

    def load_users(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password, security_question, security_answer FROM users")
        rows = cursor.fetchall()
        conn.close()

        self.user_table.setRowCount(len(rows))
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["User ID", "Password", "Security Question", "Answer"])
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.user_table.setItem(i, j, QTableWidgetItem(str(val)))

    def search_users(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_users()
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password, security_question, security_answer FROM users WHERE user_id LIKE ?", (f"%{keyword}%",))
        rows = cursor.fetchall()
        conn.close()

        self.user_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.user_table.setItem(i, j, QTableWidgetItem(str(val)))

    def delete_user(self):
        selected = self.user_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "경고", "삭제할 사용자를 선택하세요.")
            return
        user_id = self.user_table.item(selected, 0).text()

        confirm = QMessageBox.question(self, "확인", f"정말로 {user_id} 사용자를 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            self.load_users()

    def init_reservation_tab(self):
        layout = QVBoxLayout()
        self.res_table = QTableWidget()
        layout.addWidget(self.res_table)

        btn_layout = QHBoxLayout()
        self.res_search_input = QLineEdit()
        self.res_search_input.setPlaceholderText("user_id로 예약 검색")
        btn_layout.addWidget(self.res_search_input)

        btn_res_search = QPushButton("검색")
        btn_res_search.clicked.connect(self.search_reservations)
        btn_layout.addWidget(btn_res_search)

        btn_res_reload = QPushButton("새로고침")
        btn_res_reload.clicked.connect(self.load_reservations)
        btn_layout.addWidget(btn_res_reload)

        btn_res_delete = QPushButton("선택 예약 삭제")
        btn_res_delete.clicked.connect(self.delete_reservation)
        btn_layout.addWidget(btn_res_delete)

        layout.addLayout(btn_layout)
        self.reservation_tab.setLayout(layout)
        self.load_reservations()

    def load_reservations(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, restaurant, seat, start_time, end_time FROM reservations")
        rows = cursor.fetchall()
        conn.close()

        self.res_table.setRowCount(len(rows))
        self.res_table.setColumnCount(6)
        self.res_table.setHorizontalHeaderLabels(["ID", "User ID", "Restaurant", "Seat", "Start Time", "End Time"])
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.res_table.setItem(i, j, QTableWidgetItem(str(val)))

    def search_reservations(self):
        keyword = self.res_search_input.text().strip()
        if not keyword:
            self.load_reservations()
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, restaurant, seat, start_time, end_time FROM reservations WHERE user_id LIKE ?", (f"%{keyword}%",))
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

        confirm = QMessageBox.question(self, "확인", f"정말로 예약 {res_id}를 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reservations WHERE id=?", (res_id,))
            conn.commit()
            conn.close()
            self.load_reservations()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdminApp()
    window.show()
    sys.exit(app.exec_())
