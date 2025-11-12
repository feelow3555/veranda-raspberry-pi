"""
스마트팜 메인 프로그램
- 센서 데이터 주기적으로 읽고 전송
- 서버 명령 받아서 기기 제어
"""
import time
import threading # 멀티 스레드
from config import *

# 모듈 import
from modules import sensors # 센서
from modules import devices # 디바이스
from modules import camera # 카메라
from modules import websocket_client as ws # 웹 소켓 ws 라는 이름으로 사용


# ==================== 센서 데이터 전송 ====================

def sensor_loop():
    """
    센서 데이터 주기적으로 읽고 전송
    5초마다 실행
    """
    print("센서 모니터링 시작...")
    
    while True:
        try:
            # 모든 센서 데이터 읽기
            data = sensors.get_all_sensor_data()
            
            # 서버로 전송
            ws.send_sensor_data(data)
            
            # 대기
            time.sleep(SENSOR_INTERVAL)
            
        except Exception as e:
            print(f"센서 루프 오류: {e}")
            time.sleep(5)


# ==================== 명령 처리 ====================

def handle_command(data):
    """
    서버로부터 받은 명령 처리
    data 예시: {"type": "pump", "action": "on"}
    """
    try:
        cmd_type = data.get('type')
        action = data.get('action')
        
        print(f"명령 처리: {cmd_type} - {action}")
        
        # 펌프 제어
        if cmd_type == 'pump':
            if action == 'on':
                devices.control_pump(True)
            elif action == 'off':
                devices.control_pump(False)
        
        # LED 제어
        elif cmd_type == 'led':
            if action == 'on':
                devices.control_led(True)
            elif action == 'off':
                devices.control_led(False)
        
        # 팬 제어
        elif cmd_type == 'fan':
            if action == 'on':
                devices.control_fan(True)
            elif action == 'off':
                devices.control_fan(False)
        
        # 모든 기기 끄기
        elif cmd_type == 'all':
            if action == 'off':
                devices.turn_off_all()
        
        # 카메라 촬영
        elif cmd_type == 'camera':
            if action == 'capture':
                img_path = camera.capture_image()
                if img_path:
                    ws.send_image(img_path)
        
        # 기기 상태 전송
        status = devices.get_all_device_status() # 명령 처리 후 현재 상태 전송
        ws.send_device_status(status) # 서버에 현재 상태 알려줌
        
    except Exception as e:
        print(f"명령 처리 오류: {e}")


# ==================== 메인 ====================

def main():
    """메인 함수"""
    print("=" * 50)
    print("스마트팜 시스템 시작")
    print("=" * 50)
    
    # 웹소켓 명령 콜백 등록
    ws.set_command_callback(handle_command) # 서버에서 명령 오면 handle_command() 실행
    
    # 서버 연결
    print("\n서버 연결 중...")
    if ws.connect_to_server():
        print("✓ 서버 연결 성공\n")
    else:
        print("! 서버 연결 실패 - 센서만 작동\n")
    
    # 센서 루프를 별도 스레드로 실행
    sensor_thread = threading.Thread(target=sensor_loop, daemon=True) # 실행할 함수, 메인 종료시 같이 종료
    sensor_thread.start() # 스레드 시작 -> 스레드가 있어야 센서를 전송하면서 다른 코드도 실행 됨
    
    print("시스템 가동 중...")
    print("종료하려면 Ctrl+C\n")
    
    try:
        # 메인 스레드는 계속 실행
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n시스템 종료 중...")
        devices.turn_off_all()  # 모든 기기 끄기
        ws.disconnect_from_server()
        print("✓ 종료 완료")


if __name__ == "__main__":
    main()