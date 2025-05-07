# main.py

import sys  # 시스템 관련 기능 사용을 위한 모듈
from PyQt5.QtWidgets import (  # PyQt5에서 GUI 구성에 필요한 위젯 불러오기
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QDialog, QHBoxLayout, QScrollArea, QGroupBox
)
from PyQt5.QtGui import QFont  # 글꼴 관련 클래스
from PyQt5.QtCore import Qt  # 정렬 등 Qt 상수 사용을 위한 모듈
from reservation_utils import reserve_seat  # 예약 기능 함수 불러오기 (별도 파일에서 정의됨)
import sqlite3  # (사용되고 있진 않지만) 데이터베이스 작업을 위한 모듈

# --- 메인 윈도우 클래스 정의 ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.restaurant_selection_window = RestaurantReservation()  # 식당 예약 창 객체 생성
        self.login_window = LoginWindow(self)  # 로그인 창 객체 생성 (MainWindow를 부모로 설정)
        self.login_window.show()  # 로그인 창 보여주기

# --- 로그인 창 클래스 정의 ---
class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window  # 메인 윈도우 참조 저장
        self.setWindowTitle("학식 예약 프로그램 - 로그인")  # 창 제목 설정
        self.setGeometry(100, 100, 300, 200)  # 창 위치와 크기 설정
        self.initUI()  # UI 초기화 함수 호출
        self.users = {  # 하드코딩된 사용자 정보 (ID, 비밀번호, 보안질문/답변)
            "user1": {"password": "pass1", "security_question": "가장 좋아하는 색깔은?", "security_answer": "파란색"},
            "user2": {"password": "pass2", "security_question": "처음 키운 애완동물 이름은?", "security_answer": "멍멍이"}
        }

    def initUI(self):
        layout = QVBoxLayout()  # 수직 레이아웃 생성
        title_label = QLabel("학식 예약 시스템")  # 제목 라벨
        title_label.setFont(QFont('Arial', 16, QFont.Bold))  # 라벨 글꼴 설정
        layout.addWidget(title_label)  # 레이아웃에 추가

        self.id_input = QLineEdit()  # 학번 입력란
        self.id_input.setPlaceholderText("학번")  # 힌트 텍스트
        layout.addWidget(self.id_input)

        self.pw_input = QLineEdit()  # 비밀번호 입력란
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setEchoMode(QLineEdit.Password)  # 비밀번호 숨김 처리
        layout.addWidget(self.pw_input)

        login_btn = QPushButton("로그인")  # 로그인 버튼
        login_btn.clicked.connect(self.login_check)  # 클릭 시 login_check 함수 호출
        layout.addWidget(login_btn)

        signup_btn = QPushButton("회원가입")  # 회원가입 버튼
        signup_btn.clicked.connect(self.signup)
        layout.addWidget(signup_btn)

        find_pw_btn = QPushButton("비밀번호 찾기")  # 비밀번호 찾기 버튼
        find_pw_btn.clicked.connect(self.find_password)
        layout.addWidget(find_pw_btn)

        self.setLayout(layout)  # 레이아웃 적용

    def login_check(self):
        user_id = self.id_input.text()  # 입력된 학번
        password = self.pw_input.text()  # 입력된 비밀번호

        # 사용자 정보와 일치하는지 확인
        if user_id in self.users and self.users[user_id]["password"] == password:
            self.main_window.restaurant_selection_window.set_user(user_id)  # 사용자 ID 설정
            self.main_window.restaurant_selection_window.show()  # 식당 창 표시
            self.hide()  # 로그인 창 숨김
        else:
            QMessageBox.warning(self, "로그인 실패", "학번 또는 비밀번호가 틀렸습니다.")  # 오류 메시지
            self.pw_input.clear()  # 비밀번호 입력란 초기화

    def signup(self):
        signup_dialog = SignupDialog(self)  # 회원가입 창 생성
        signup_dialog.exec()  # 다이얼로그 모달로 실행
        if signup_dialog.user_info:  # 회원가입 정보가 있으면
            user_id, password, question, answer = signup_dialog.user_info
            self.users[user_id] = {  # 새 사용자 추가
                "password": password,
                "security_question": question,
                "security_answer": answer
            }
            QMessageBox.information(self, "회원가입 성공", f"{user_id}님, 회원가입이 완료되었습니다.")

    def find_password(self):
        find_pw_dialog = FindPasswordDialog(self.users)  # 비밀번호 찾기 창
        find_pw_dialog.exec_()

# --- 회원가입 다이얼로그 ---
class SignupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)  # 부모 위젯 초기화
        self.setWindowTitle("회원가입")  # 다이얼로그 창의 제목 설정
        self.setGeometry(150, 150, 350, 250)  # 창의 위치 (x=150, y=150)와 크기 설정 (너비=350, 높이=250)
        self.user_info = None  # 사용자가 입력한 정보를 저장할 변수 (성공 시 튜플 형태로 저장)
        self.initUI()  # UI 요소들을 구성하는 함수 호출

    def initUI(self):
        layout = QVBoxLayout()  # 세로 방향 레이아웃을 생성

        self.id_input = QLineEdit()  # 학번 입력창 생성
        self.id_input.setPlaceholderText("새 학번")  # 힌트 텍스트 (입력 전 표시)
        layout.addWidget(self.id_input)  # 레이아웃에 입력창 추가

        self.pw_input = QLineEdit()  # 비밀번호 입력창 생성
        self.pw_input.setPlaceholderText("새 비밀번호")  # 힌트 텍스트 설정
        self.pw_input.setEchoMode(QLineEdit.Password)  # 입력 시 비밀번호 마스킹 처리 (●●● 형태)
        layout.addWidget(self.pw_input)  # 레이아웃에 비밀번호 입력창 추가

        self.pw_confirm_input = QLineEdit()  # 비밀번호 확인 입력창 생성
        self.pw_confirm_input.setPlaceholderText("비밀번호 확인")  # 힌트 텍스트
        self.pw_confirm_input.setEchoMode(QLineEdit.Password)  # 비밀번호 마스킹 처리
        layout.addWidget(self.pw_confirm_input)  # 레이아웃에 추가

        self.question_input = QLineEdit()  # 보안 질문 입력창 생성
        self.question_input.setPlaceholderText("비밀번호 찾기 질문")  # 힌트 텍스트
        layout.addWidget(self.question_input)  # 레이아웃에 추가

        self.answer_input = QLineEdit()  # 보안 질문에 대한 답 입력창 생성
        self.answer_input.setPlaceholderText("질문 답변")  # 힌트 텍스트
        layout.addWidget(self.answer_input)  # 레이아웃에 추가

        signup_btn = QPushButton("회원가입")  # '회원가입' 버튼 생성
        signup_btn.clicked.connect(self.signup_check)  # 클릭 시 `signup_check` 함수 실행
        layout.addWidget(signup_btn)  # 버튼을 레이아웃에 추가

        cancel_btn = QPushButton("취소")  # '취소' 버튼 생성
        cancel_btn.clicked.connect(self.close)  # 클릭 시 창 닫기
        layout.addWidget(cancel_btn)  # 버튼을 레이아웃에 추가

        self.setLayout(layout)  # 이 다이얼로그에 전체 레이아웃 적용

    def signup_check(self):
        new_id = self.id_input.text()  # 학번 입력값 가져오기
        new_pw = self.pw_input.text()  # 비밀번호 입력값 가져오기
        pw_confirm = self.pw_confirm_input.text()  # 비밀번호 확인 입력값
        question = self.question_input.text()  # 보안 질문 입력값
        answer = self.answer_input.text()  # 질문에 대한 답변 입력값

        # ⚠️ 모든 필수 항목이 입력되었는지 확인
        if not new_id or not new_pw or not question or not answer:
            QMessageBox.warning(self, "회원가입 오류", "모든 항목을 입력해주세요.")  # 입력이 빠졌을 경우 경고창 표시
            return  # 함수 종료

        # ⚠️ 비밀번호와 비밀번호 확인이 일치하는지 확인
        if new_pw != pw_confirm:
            QMessageBox.warning(self, "회원가입 오류", "비밀번호 확인이 일치하지 않습니다.")  # 불일치 시 경고
            return

        # ⚠️ 이미 존재하는 학번인지 확인
        if new_id in self.parent().users:  # 부모 위젯의 `users` 딕셔너리에서 학번 중복 여부 확인
            QMessageBox.warning(self, "회원가입 오류", "이미 존재하는 학번입니다.")  # 중복 시 경고
            return

        # ✅ 모든 조건을 통과하면 사용자 정보를 튜플 형태로 저장
        self.user_info = (new_id, new_pw, question, answer)

        self.close()  # 회원가입 창 닫기


# --- 비밀번호 찾기 다이얼로그 ---
class FindPasswordDialog(QWidget):
    def __init__(self, users, parent=None):
        super().__init__(parent)  # 부모 위젯 초기화
        self.setWindowTitle("비밀번호 찾기")  # 창 제목 설정
        self.setGeometry(150, 150, 350, 200)  # 창의 위치와 크기 설정
        self.users = users  # 사용자 정보를 받아 저장 (딕셔너리 형식)
        self.initUI()  # UI 초기화 함수 호출

    def initUI(self):
        layout = QVBoxLayout()  # 세로 방향 레이아웃 생성

        self.id_input = QLineEdit()  # 학번 입력 창 생성
        self.id_input.setPlaceholderText("학번 입력")  # 입력창에 표시될 안내 문구 설정
        layout.addWidget(self.id_input)  # 입력창을 레이아웃에 추가

        self.question_display = QLabel("질문이 여기에 표시됩니다.")  # 보안 질문이 표시될 라벨 생성
        layout.addWidget(self.question_display)  # 라벨을 레이아웃에 추가

        self.answer_input = QLineEdit()  # 질문에 대한 답변 입력창 생성
        self.answer_input.setPlaceholderText("질문에 대한 답변 입력")  # 안내 문구 설정
        layout.addWidget(self.answer_input)  # 입력창을 레이아웃에 추가

        find_btn = QPushButton("확인")  # 확인 버튼 생성
        find_btn.clicked.connect(self.check_answer)  # 버튼 클릭 시 답변 확인 함수 연결
        layout.addWidget(find_btn)  # 버튼을 레이아웃에 추가

        self.id_input.textChanged.connect(self.display_question)  # 학번 입력 시 질문 자동 표시

        self.setLayout(layout)  # 전체 레이아웃 설정
        self.current_user_id = None  # 현재 입력된 학번 저장 변수 초기화

    def display_question(self, user_id):
        self.current_user_id = user_id  # 현재 학번 저장
        if user_id in self.users:  # 학번이 존재하면
            self.question_display.setText(self.users[user_id]["security_question"])  # 질문 표시
        else:
            self.question_display.setText("존재하지 않는 학번입니다.")  # 없는 학번일 경우 경고 표시

    def check_answer(self):
        # 학번이 존재하고 사용자 정보가 있을 경우
        if self.current_user_id and self.current_user_id in self.users:
            correct = self.users[self.current_user_id]["security_answer"]  # 저장된 정답 불러오기
            if self.answer_input.text() == correct:  # 입력한 답변이 맞으면
                # 비밀번호를 메시지 박스로 표시
                QMessageBox.information(self, "비밀번호", f"비밀번호는: {self.users[self.current_user_id]['password']}")
                self.close()  # 창 닫기
            else:
                QMessageBox.warning(self, "오류", "답변이 일치하지 않습니다.")  # 답변 틀릴 경우 경고
        else:
            QMessageBox.warning(self, "오류", "학번을 다시 확인해주세요.")  # 유효하지 않은 학번일 경우


# --- 식당 선택 및 예약 창 ---
class RestaurantReservation(QWidget):
    def __init__(self):
        super().__init__()  # QWidget 초기화
        self.setWindowTitle("학식 예약 프로그램")  # 창 제목 설정
        self.setGeometry(100, 100, 800, 400)  # 창의 위치와 크기 설정
        self.current_user_id = None  # 로그인한 사용자 ID 저장용 변수
        self.initUI()  # UI 초기화 함수 호출

    def set_user(self, user_id):
        self.current_user_id = user_id  # 외부에서 로그인한 사용자 ID 설정

    def initUI(self):
        main_layout = QVBoxLayout()  # 메인 레이아웃 (수직 정렬)

        title = QLabel("학식 예약 시스템")  # 타이틀 라벨 생성
        title.setFont(QFont("Arial", 18, QFont.Bold))  # 글꼴, 크기, 굵기 설정
        title.setAlignment(Qt.AlignCenter)  # 가운데 정렬
        main_layout.addWidget(title)  # 타이틀을 메인 레이아웃에 추가

        scroll = QScrollArea()  # 스크롤 가능한 영역 생성
        scroll.setWidgetResizable(True)  # 내부 위젯 크기에 따라 자동 조절

        content = QWidget()  # 스크롤 안에 들어갈 컨테이너 위젯
        content_layout = QHBoxLayout()  # 컨텐츠들을 가로로 나열할 레이아웃

        # 식당과 그에 대한 메뉴 및 알레르기 정보를 딕셔너리로 저장
        restaurants = [
            {"name": "한빛식당", "menus": ["김치찌개", "제육볶음", "돈까스"], "allergy": "우유, 땅콩"},
            {"name": "별빛식당", "menus": ["된장찌개", "생선구이", "오므라이스"], "allergy": "대두, 밀"},
            {"name": "은하수식당", "menus": ["부대찌개", "닭갈비", "스파게티"], "allergy": "계란, 토마토"}
        ]

        # 각 식당 정보를 이용해 박스를 생성하고 레이아웃에 추가
        for restaurant in restaurants:
            box = self.create_restaurant_box(restaurant)  # 식당 박스 생성
            content_layout.addWidget(box)  # 생성된 박스를 레이아웃에 추가

        content.setLayout(content_layout)  # 컨텐츠 위젯에 레이아웃 설정
        scroll.setWidget(content)  # 스크롤 영역에 컨텐츠 위젯 부착
        main_layout.addWidget(scroll)  # 전체 스크롤 영역을 메인 레이아웃에 추가

        self.setLayout(main_layout)  # 메인 레이아웃을 현재 위젯에 설정

    # 식당 정보를 받아 하나의 그룹 박스 UI 요소를 생성하는 함수
    def create_restaurant_box(self, restaurant):
        group_box = QGroupBox()  # 그룹 박스 생성 (식당 하나를 나타내는 박스)

        layout = QVBoxLayout()  # 박스 안의 요소들을 수직으로 배치하기 위한 레이아웃 생성

        name_label = QLabel(restaurant["name"])  # 식당 이름 라벨 생성
        name_label.setFont(QFont("Arial", 14, QFont.Bold))  # 라벨에 Arial 14포인트 굵은 글꼴 설정
        name_label.setAlignment(Qt.AlignCenter)  # 식당 이름 라벨 가운데 정렬
        layout.addWidget(name_label)  # 이름 라벨을 레이아웃에 추가

        menu_label = QLabel("\n".join(restaurant["menus"]))  # 메뉴 리스트를 줄바꿈으로 연결하여 하나의 문자열로 만든 후 라벨 생성
        menu_label.setFont(QFont("Arial", 12))  # 메뉴 라벨에 Arial 12포인트 글꼴 적용
        layout.addWidget(menu_label)  # 메뉴 라벨을 레이아웃에 추가

        allergy_label = QLabel(f"알레르기 정보: {restaurant['allergy']}")  # 알레르기 정보를 표시하는 라벨 생성
        allergy_label.setFont(QFont("Arial", 10))  # 알레르기 라벨에 Arial 10포인트 글꼴 적용
        layout.addWidget(allergy_label)  # 알레르기 정보 라벨을 레이아웃에 추가

        reserve_button = QPushButton("예약하기")  # '예약하기' 버튼 생성

        # 버튼 클릭 시 특정 식당 이름을 인자로 reserve_seat_dialog 함수를 호출하도록 연결
        # 람다 함수에서 r=restaurant["name"]으로 값 캡처 (람다 내에서 직접 딕셔너리 참조하면 나중에 값이 바뀔 위험 있음)
        reserve_button.clicked.connect(lambda _, r=restaurant["name"]: self.reserve_seat_dialog(r))
        layout.addWidget(reserve_button)  # 예약 버튼을 레이아웃에 추가

        group_box.setLayout(layout)  # 구성한 레이아웃을 그룹 박스에 설정
        group_box.setFixedSize(230, 250)  # 그룹 박스 크기 고정 (너비 230, 높이 250)

        return group_box  # 완성된 그룹 박스를 반환 (scroll view 등에 배치하기 위해)

    # 사용자가 식당 예약 버튼을 클릭했을 때 실행되는 함수
    def reserve_seat_dialog(self, restaurant_name):
        # 사용자가 로그인하지 않은 상태면 경고 메시지 표시 후 함수 종료
        if not self.current_user_id:
            QMessageBox.warning(self, "오류", "먼저 로그인하세요.")  # 경고 창 표시
            return  # 함수 종료

        # 로그인 상태면 예약 함수 호출 (외부 모듈의 reserve_seat 함수 사용)
        reserve_seat(self, restaurant_name, self.current_user_id)
        # self: 부모 위젯 (예약 창이 뜰 위치)
        # restaurant_name: 예약할 식당 이름
        # self.current_user_id: 예약하는 사용자 ID


# --- 프로그램 실행 부분 ---
if __name__ == "__main__":
    app = QApplication(sys.argv)  # QApplication 객체 생성
    main_window = MainWindow()  # 메인 윈도우 실행
    sys.exit(app.exec_())  # 앱 실행
