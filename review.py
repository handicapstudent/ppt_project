import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QTextEdit, QPushButton, QVBoxLayout, QLabel,
    QMessageBox, QHBoxLayout, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from datetime import datetime
from PyQt5.QtGui import QFont

DB_FILE = "review.db"


def init_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            review TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_review(user_id, review_text, rating):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO reviews (user_id, review, rating, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_id, review_text, rating, timestamp))
    conn.commit()
    conn.close()


def get_reviews_by_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, review, rating, timestamp FROM reviews WHERE user_id = ?", (user_id,))
    reviews = cursor.fetchall()
    conn.close()
    return reviews


def get_all_reviews():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, review, rating, timestamp FROM reviews ORDER BY timestamp DESC")
    reviews = cursor.fetchall()
    conn.close()
    return reviews


def update_review(review_id, new_text, new_rating):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        UPDATE reviews
        SET review = ?, rating = ?, timestamp = ?
        WHERE id = ?
    """, (new_text, new_rating, timestamp, review_id))
    conn.commit()
    conn.close()


def delete_review(review_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()


class ReviewDialog(QDialog):
    def __init__(self, restaurant_name, user_id, parent=None):
        super().__init__(parent)
        self.restaurant_name = restaurant_name
        self.user_id = user_id
        self.current_edit_id = None
        self.init_ui()

    def init_ui(self):
        self.rating_value = 3
        self.setWindowTitle("후기 작성")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f6f8;
            }
            QLabel {
                font-size: 14px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #125ea3;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 13px;
            }
        """)

        layout = QVBoxLayout()

        label = QLabel("후기를 작성하세요:")
        layout.addWidget(label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("이곳에 후기를 입력하세요...")
        layout.addWidget(self.text_edit)

        rating_layout = QHBoxLayout()
        rating_label = QLabel("별점:")
        rating_layout.addWidget(rating_label)

        self.stars = []
        for i in range(5):
            star = QLabel("☆")
            star.setFont(QFont("Arial", 26))
            star.setStyleSheet("color: gold;")
            star.setAlignment(Qt.AlignCenter)
            star.setFixedWidth(34)
            star.mousePressEvent = self.make_star_clicked_handler(i + 1)
            self.stars.append(star)
            rating_layout.addWidget(star)

        self.update_star_display()
        layout.addLayout(rating_layout)

        self.submit_button = QPushButton("후기 제출")
        self.submit_button.clicked.connect(self.submit_review)
        layout.addWidget(self.submit_button)

        layout.addWidget(QLabel("이전 후기 목록:"))
        self.review_list = QListWidget()
        self.review_list.itemClicked.connect(self.load_review_for_edit)
        layout.addWidget(self.review_list)

        self.edit_button = QPushButton("선택한 후기 삭제")
        self.edit_button.clicked.connect(self.delete_selected_review)
        layout.addWidget(self.edit_button)

        self.setLayout(layout)
        self.load_reviews()

    def make_star_clicked_handler(self, rating):
        def handler(event):
            self.rating_value = rating
            self.update_star_display()
        return handler

    def update_star_display(self):
        for i, star in enumerate(self.stars):
            star.setText("★" if i < self.rating_value else "☆")

    def load_reviews(self):
        self.review_list.clear()
        self.reviews = get_all_reviews()
        for review_id, writer_id, text, rating, timestamp in self.reviews:
            stars = "★" * rating + "☆" * (5 - rating)
            display_text = f"[{timestamp}] ({writer_id}) {stars}\n{text}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, (review_id, writer_id))
            item.setFont(QFont("Noto Sans KR", 11))
            self.review_list.addItem(item)

    def load_review_for_edit(self, item):
        review_id, writer_id = item.data(Qt.UserRole)
        if writer_id != self.user_id:
            QMessageBox.warning(self, "권한 오류", "본인의 후기만 수정할 수 있습니다.")
            return

        for rid, wid, text, rating, timestamp in self.reviews:
            if rid == review_id:
                self.current_edit_id = rid
                self.text_edit.setText(text)
                self.rating_value = rating
                self.update_star_display()
                break

    def submit_review(self):
        review_text = self.text_edit.toPlainText().strip()
        if not review_text:
            QMessageBox.warning(self, "입력 오류", "후기를 입력해주세요.")
            return
        rating = self.rating_value

        if self.current_edit_id:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM reviews WHERE id = ?", (self.current_edit_id,))
            result = cursor.fetchone()
            conn.close()

            if not result or result[0] != self.user_id:
                QMessageBox.warning(self, "권한 오류", "본인의 후기만 수정할 수 있습니다.")
                return

            update_review(self.current_edit_id, review_text, rating)
            QMessageBox.information(self, "수정 완료", "후기가 수정되었습니다.")
            self.current_edit_id = None
        else:
            save_review(self.user_id, review_text, rating)
            QMessageBox.information(self, "성공", "후기가 저장되었습니다.")

        self.text_edit.clear()
        self.load_reviews()

    def delete_selected_review(self):
        selected_item = self.review_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "선택 오류", "삭제할 후기를 선택하세요.")
            return

        review_id, writer_id = selected_item.data(Qt.UserRole)
        if writer_id != self.user_id:
            QMessageBox.warning(self, "권한 오류", "본인의 후기만 삭제할 수 있습니다.")
            return

        delete_review(review_id)
        QMessageBox.information(self, "삭제 완료", "후기가 삭제되었습니다.")
        self.text_edit.clear()
        self.current_edit_id = None
        self.load_reviews()
