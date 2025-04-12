# 임의 자리 예약 함수
from PyQt5.QtWidgets import QMessageBox


def reserve_seat(restaurant, menu):
    print(f"[자리 예약 함수 호출] {restaurant} - 메뉴: {menu}")
    QMessageBox.information(None, "자리 예약", f"{restaurant}에서 '{menu}' 예약을 진행합니다.")
