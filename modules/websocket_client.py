# """
# 웹소켓 클라이언트 - 스프링 부트와 통신
# """
# import json
# import time
# import socketio
# from config import *

# # Socket.IO 클라이언트 생성
# sio = socketio.Client()

# # 연결 상태
# is_connected = False


# # ==================== 이벤트 핸들러 ====================

# @sio.event
# def connect():
#     """서버 연결 성공"""
#     global is_connected
#     is_connected = True # 연결 상태 변경
#     print("스프링 부트 서버 연결 성공")


# @sio.event
# def disconnect():
#     """서버 연결 끊김"""
#     global is_connected
#     is_connected = False # 연결 상태 변경
#     print("서버 연결 끊김")

# # 명령 수신 핸들러
# @sio.on('command')
# def on_command(data):
#     """
#     서버로부터 명령 수신
#     data 예시: {"type": "pump", "action": "on"}
#     """
#     print(f"← 명령 수신: {data}")
    
#     # 여기서 명령 처리 (나중에 app.py에서 처리)
#     # 일단 콜백 함수로 전달
#     if command_callback:
#         command_callback(data)
# """
# **설명:**
# - `@sio.on('command')`: 'command'라는 이름의 메시지 받을 때
# - `command_callback`: 나중에 app.py에서 등록할 함수

# **흐름:**
# 스프링 부트 → 'command' 전송 → on_command() 실행 → command_callback() 호출
# """


# # ==================== 연결 ====================

# def connect_to_server():
#     """스프링 부트 서버에 연결"""
#     try:
#         print(f"서버 연결 시도: {SPRING_BOOT_URL}")
#         sio.connect(SPRING_BOOT_URL) # 연결 시도
#         return True # 성공
#     except Exception as e:
#         print(f"서버 연결 실패: {e}")
#         return False # 실패


# def disconnect_from_server():
#     """서버 연결 종료"""
#     try:
#         sio.disconnect()
#         print("서버 연결 종료")
#     except Exception as e:
#         print(f"연결 종료 오류: {e}")


# # ==================== 데이터 전송 ====================

# def send_sensor_data(data):
#     """
#     센서 데이터 전송
#     data: dict {'temperature': 25, 'humidity': 60, ...}
#     """
#     if not is_connected:
#         print("! 서버 미연결 - 전송 실패")
#         return False
    
#     try:
#         sio.emit('sensor_data', data) # 'sensor_data' 이벤트로 전송
#         print(f"→ 센서 데이터 전송: {data}")
#         return True
#     except Exception as e:
#         print(f"데이터 전송 오류: {e}")
#         return False


# def send_device_status(data):
#     """
#     기기 상태 전송
#     data: dict {'pump': True, 'led': False, ...}
#     """
#     if not is_connected:
#         return False
    
#     try:
#         sio.emit('device_status', data) # 'device_data' 이벤트로 전송
#         print(f"→ 기기 상태 전송: {data}")
#         return True
#     except Exception as e:
#         print(f"상태 전송 오류: {e}")
#         return False


# def send_image(image_path):
#     """
#     이미지 전송
#     image_path: 이미지 파일 경로
#     """
#     if not is_connected:
#         return False
    
#     try:
#         # 이미지를 base64로 인코딩
#         import base64

#         # 이미지 파일을 바이트로 읽기
#         with open(image_path, 'rb') as f:
#             image_data = base64.b64encode(f.read()).decode('utf-8') # base64로 인코딩 (텍스트로 변환)
        
#         # 전송
#         sio.emit('camera_image', {'image': image_data})
#         print(f"→ 이미지 전송: {image_path}")
#         return True
#     except Exception as e:
#         print(f"이미지 전송 오류: {e}")
#         return False
#     # 이미지(바이너리) -> base 64 -> 텍스트 -> 웹소켓으로 전송 가능


# # ==================== 명령 콜백 ====================

# command_callback = None # 전역 변수

# def set_command_callback(callback):
#     """
#     명령 수신 콜백 함수 등록
#     callback: 명령 받았을 때 호출할 함수
#     """
#     global command_callback
#     command_callback = callback