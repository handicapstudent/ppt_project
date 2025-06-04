import requests
from bs4 import BeautifulSoup
from datetime import datetime
import webbrowser
import urllib.parse
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QScrollArea, QGroupBox, QMessageBox, QDialog, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from review import ReviewDialog
from reservation_utils import reserve_seat
from distance_utils_kakao import get_distance_text

MENU_URL = "https://www.cbnucoop.com/service/restaurant/"

address_map = {
    "한빛식당": "충북 청주시 서원구 충대로 1 제1학생회관",
    "별빛식당": "충북 청주시 서원구 충대로 1 제1학생회관",
    "은하수식당": "충북대학교 은하수 식당"
}

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
            meal_name = header.text.strip() if header else ""

            if meal_name:
                # ✅ 사이드 디쉬 제거 — 메뉴 본문 저장 안 함
                results[식당][요일].setdefault(meal_name, [])
        return results, weekday_map
    except Exception as e:
        print("메뉴 불러오기 실패:", e)
        return {"한빛식당": {}, "별빛식당": {}, "은하수식당": {}}, ['월요일','화요일','수요일','목요일','금요일']
