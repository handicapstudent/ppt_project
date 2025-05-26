import requests
from bs4 import BeautifulSoup
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QScrollArea, QGroupBox, QMessageBox, QDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from review import ReviewDialog
from reservation_utils import reserve_seat

MENU_URL = "https://www.cbnucoop.com/service/restaurant/"

def fetch_today_and_week_menus(force_weekday=None):
    try:
        res = requests.get(MENU_URL, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        menu_divs = soup.select("#menu-result .menu")
        weekday_titles = soup.select(".weekday-title")
        weekday_map = []
        for th in weekday_titles:
            txt = th.text
            if '(' in txt and ')' in txt:
                weekday_map.append(txt.split('(')[1].replace(')', ''))
        if not weekday_map:
            weekday_map = ['월요일','화요일','수요일','목요일','금요일']
        code_to_name = {'18': '한빛식당', '19': '별빛식당', '20': '은하수식당'}
        results = {name: {요일: {} for 요일 in weekday_map} for name in code_to_name.values()}
        for menu in menu_divs:
            data_table = menu.get("data-table", "")
            parts = data_table.split("-")
            if len(parts) != 4:
                continue
            식당코드, _, 시간코드, 요일코드 = parts
            식당 = code_to_name.get(식당코드, None)
            if not 식당:
                continue
            요일 = weekday_map[int(요일코드)]
            header = menu.select_one("h6.card-header")
            items = menu.select("li.side")
            meal_name = header.text.strip() if header else ""
            side_dishes = [li.text.strip() for li in items]
            if meal_name:
                menu_text = '/'.join(side_dishes)
                results[식당][요일].setdefault(meal_name, []).append(menu_text)
        return results, weekday_map
    except Exception as e:
        print("메뉴 불러오기 실패:", e)
        return {"한빛식당": {}, "별빛식당": {}, "은하수식당": {}}, ['월요일','화요일','수요일','목요일','금요일']

class RestaurantReservation(QWidget):
    def __init__(self, force_weekday=None):
        super().__init__()
        self.setWindowTitle("학식 예약 프로그램")
        self.resize(1200, 900)
        self.current_user_id = None
        self.force_weekday = force_weekday
        self.initUI()

    def set_user(self, user_id):
        self.current_user_id = user_id

    def initUI(self):
        main_layout = QVBoxLayout()
        title = QLabel("학식 예약 시스템")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()

        full_menus, weekday_map = fetch_today_and_week_menus()
        today_index = self.force_weekday if self.force_weekday is not None else datetime.today().weekday()
        if today_index >= len(weekday_map):
            today_index = 0
        today = weekday_map[today_index]

        for name, menus in full_menus.items():
            group = QGroupBox(name)
            layout = QVBoxLayout()
            menu_dict = menus.get(today, {})
            # 한빛식당 또는 은하수식당만 아침/점심, 점심/저녁 순서 swap!
            keys = list(menu_dict.keys())
            if name == "한빛식당" and len(keys) >= 2:
                keys[0], keys[1] = keys[1], keys[0]
            elif name == "은하수식당" and len(keys) >= 2:
                keys[0], keys[1] = keys[1], keys[0]
            display_order = keys
            for meal_name in display_order:
                dishes = menu_dict[meal_name]
                layout.addWidget(QLabel(f"<b>{meal_name}</b>: {' + '.join(dishes)}"))

            more_btn = QPushButton("메뉴 더보기")
            more_btn.clicked.connect(lambda _, n=name, m=menus: self.show_full_menu(n, m, weekday_map))
            layout.addWidget(more_btn)

            reserve_button = QPushButton("예약하기")
            reserve_button.clicked.connect(lambda _, r=name: self.reserve_seat_dialog(r))
            layout.addWidget(reserve_button)

            review_button = QPushButton("후기 보기/작성")
            review_button.clicked.connect(lambda _, r=name: self.open_review_dialog(r))
            layout.addWidget(review_button)

            group.setLayout(layout)
            content_layout.addWidget(group)

        content.setLayout(content_layout)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def show_full_menu(self, name, menus, weekday_map):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{name} 한주간 메뉴")
        dialog.resize(600, 500)
        dlg_layout = QVBoxLayout()
        for 요일 in weekday_map:
            day_label = QLabel(f"<b>{요일}</b>")
            dlg_layout.addWidget(day_label)
            menu_dict = menus.get(요일, {})
            keys = list(menu_dict.keys())
            if name == "한빛식당" and len(keys) >= 2:
                keys[0], keys[1] = keys[1], keys[0]
            elif name == "은하수식당" and len(keys) >= 2:
                keys[0], keys[1] = keys[1], keys[0]
            display_order = keys
            for meal_name in display_order:
                dishes = menu_dict[meal_name]
                meal_text = QLabel(f"<b>{meal_name}</b>: {' + '.join(dishes)}")
                dlg_layout.addWidget(meal_text)
        dialog.setLayout(dlg_layout)
        dialog.exec_()

    def reserve_seat_dialog(self, restaurant_name):
        if not self.current_user_id:
            QMessageBox.warning(self, "오류", "먼저 로그인하세요.")
            return
        reserve_seat(self, restaurant_name, self.current_user_id)

    def open_review_dialog(self, restaurant_name):
        if not self.current_user_id:
            QMessageBox.warning(self, "오류", "먼저 로그인하세요.")
            return
        dialog = ReviewDialog(restaurant_name, self.current_user_id, self)
        dialog.exec_()
