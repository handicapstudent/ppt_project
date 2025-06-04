import os

import arg
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout,
    QFrame, QMessageBox, QDialog, QScrollArea
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

from menu import fetch_today_and_week_menus
from review import ReviewDialog
from reservation_utils import reserve_seat
import webbrowser, urllib.parse
from settings import AppSettings

address_map = {
    "한빛식당": "충북 청주시 서원구 충대로 1 제1학생회관",
    "별빛식당": "충북 청주시 서원구 충대로 1 제1학생회관",
    "은하수식당": "충북대학교 은하수 식당"
}

class MenuCard(QFrame):
    def __init__(self, title, callback, image_path=None):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #333;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        if image_path and os.path.exists(image_path):
            image_label = QLabel()
            pixmap = QPixmap(image_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)

            image_label.setStyleSheet("background: transparent; border:none;")
            layout.addWidget(image_label)

        text = QLabel(title)
        text.setFont(QFont("Noto Sans KR", 12))
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet("background: transparent; border: none;")
        layout.addWidget(text)

        self.setLayout(layout)
        self.mousePressEvent = lambda e: callback()


class RestaurantSelectDialog(QDialog):
    def __init__(self, title, callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(800, 200)         #창크기 변경
        layout = QVBoxLayout()
        grid = QGridLayout()

        cards = [                               #변경 시작
            ("한빛식당", "assets/메뉴보기.png"),
            ("별빛식당", "assets/별똥별.png"),
            ("은하수식당", "assets/은하수.png"),
        ]
        for i, (arg, image) in enumerate(cards):
            card = MenuCard(arg, lambda cb=self.select_restaurant: cb(arg, callback), image)
            grid.addWidget(card, 0, i)  # 한 줄에 배치
                                            #변경 끝
        layout.addLayout(grid)
        self.setLayout(layout)

    def make_btn_callback(self, restaurant_name, callback):
        return lambda _: self.select_restaurant(restaurant_name, callback)

    def select_restaurant(self, name, callback):
        self.accept()
        callback(name)

class RestaurantReservation(QWidget):
    def __init__(self, parent=None):
            super().__init__(parent)
            self.main_window = parent  # ✅ MainWindow 참조 저장
            self.setWindowTitle("식당 예약 메인")
            self.setFixedSize(1200, 800)
            self.current_user_id = None
            self.initUI()

    def apply_high_contrast(self):
        self.setStyleSheet("""
            QWidget {
                background-color: black;
                color: white;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid white;
            }
            QLabel, QCheckBox {
                color: white;
            }
        """)

    def reset_contrast(self):
        self.setStyleSheet("background-color: #f4f6f8;")
        # 내부 메뉴 카드들은 재생성될 때 자동 스타일링되므로 별도 초기화 필요 없음

    class StaticMenuCard(QFrame):
        def __init__(self, title, lines):
            super().__init__()
            self.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                    border: 1px solid #e0e0e0;
                }
                QLabel {
                    color: #333;
                }
            """)
            layout = QVBoxLayout()
            layout.setContentsMargins(15, 15, 15, 20)
            layout.setSpacing(8)

            title_label = QLabel(title)
            title_label.setFont(QFont("Noto Sans KR", 11, QFont.Bold))
            layout.addWidget(title_label)

            for line in lines:
                item_label = QLabel(line)
                item_label.setFont(QFont("Noto Sans KR", 10))
                layout.addWidget(item_label)

            self.setLayout(layout)

    def initUI(self):
        self.setStyleSheet("background-color: #f4f6f8;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        # 상단 바
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0,0,0,0)
        # top_bar.setSpacing(6)
        # logo = QLabel("충북대학교\nCHUNGBUK NATIONAL UNIVERSITY")
        # logo.setFont(QFont("Arial", 12, QFont.Bold))

        logo = QLabel("충북대학교\nCHUNGBUK NATIONAL UNIVERSITY")
        logo.setFont(QFont("Arial", 10, QFont.Bold))
        logo.setFixedHeight(40)
        logo.setStyleSheet("""
            QLabel {
                background: transparent;
                line-height: 90%;
                padding-left: 4px;
            }
        """)
        top_bar.addWidget(logo)

        top_bar.addStretch()
        main_layout.addLayout(top_bar)


        # 메뉴 카드 그리드
        grid = QGridLayout()
        grid.setSpacing(10)

        cards = [
            ("한빛식당 메뉴 보기", self.show_menu,"한빛식당", "assets/메뉴보기.png"),
            ("별빛식당 메뉴 보기", self.show_menu,"별빛식당", "assets/별똥별.png"),
            ("은하수식당 메뉴 보기", self.show_menu,"은하수식당","assets/은하수.png"),
            ("좌석 예약하기", lambda:self.select_seat_reservation(), None,"assets/좌석예약.png"),
            ("후기 작성 게시판", lambda:self.select_review_dialog(), None, "assets/게시판.png"),
            ("카카오맵 길찾기", lambda:self.select_kakao_map(),None, "assets/지도.png")
        ]

        for i, (title, callback, arg, image) in enumerate(cards):
            row, col = divmod(i, 3)

            if arg is not None:
                card = MenuCard(title, lambda arg=arg, cb=callback: cb(arg), image)
            else:
                card = MenuCard(title, callback, image)

            grid.addWidget(card, row, col)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    def set_user(self, user_id):
        self.current_user_id = user_id


    def show_menu(self, name):
        menus, weekday_map = fetch_today_and_week_menus()
        if name not in menus:
            QMessageBox.warning(self, "오류", "메뉴 정보를 찾을 수 없습니다.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{name} 한주간 메뉴")
        dialog.resize(600, 500)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QGridLayout()
        layout.setSpacing(15)

        menu_dict = menus[name]
        for i, 요일 in enumerate(weekday_map):
            dishes = []
            for 시간대, items in menu_dict.get(요일, {}).items():
                dishes.append(f"[{시간대}] {', '.join(items)}")
            row, col = divmod(i, 2)
            card = self.StaticMenuCard(요일, dishes)
            layout.addWidget(card, row, col)

        content.setLayout(layout)
        scroll.setWidget(content)

        dlg_layout = QVBoxLayout()
        dlg_layout.addWidget(scroll)
        dialog.setLayout(dlg_layout)
        dialog.exec_()

    def select_seat_reservation(self):
        dialog = RestaurantSelectDialog("식당 선택 (예약)", self.reserve_seat, self)
        dialog.exec_()


    def reserve_seat(self, restaurant):
        reserve_seat(self, restaurant, self.current_user_id)

    def select_kakao_map(self):
        dialog = RestaurantSelectDialog("식당 선택 (길찾기)", self.open_map, self)
        dialog.exec_()

    def open_map(self, restaurant):
        addr = address_map.get(restaurant, "")
        if addr:
            encoded_to = urllib.parse.quote(addr)
            url = f"https://map.kakao.com/?eName={encoded_to}"
            webbrowser.open(url)
        else:
            QMessageBox.warning(self, "오류", "주소가 없습니다.")

    def select_review_dialog(self):
        dialog = RestaurantSelectDialog("식당 선택 (후기)", self.show_review, self)
        dialog.exec_()

    def show_review(self, restaurant):
        dlg = ReviewDialog(restaurant, self.current_user_id, self)
        dlg.exec_()
