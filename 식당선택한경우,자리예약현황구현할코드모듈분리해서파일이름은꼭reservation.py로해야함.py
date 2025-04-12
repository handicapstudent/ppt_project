# 임의 자리 예약 함수
from PyQt5.QtWidgets import QMessageBox


#식당별 자리배치도 확인하고 그에맞춰서 배치도 ui 구현,  자리를 누르면 -> 예약 하시겠습니까? y-> xx 시 xx부터 30분간 좌석이 예약되었습니다.
# n인경우 취소, 식당선택 화면으로 백? , 
# 다시 로그인해서 예약했던 현황을 확인하는 코드는 여부분이 잘 구현 되고 해야지 편할듯해서 아직 안함.  
def reserve_seat(restaurant, menu):
    print(f"[자리 예약 함수 호출] {restaurant} - 메뉴: {menu}")
    QMessageBox.information(None, "자리 예약", f"{restaurant}에서 '{menu}' 예약을 진행합니다.")
