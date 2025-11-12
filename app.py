"""
스마트팜 메인 프로그램
- 센서 데이터 주기적으로 읽고 전송
- 서버 명령 받아서 기기 제어
"""
import time
import threading # 멀티 스레드
from config import *
import signal
import sys

# 모듈 import (실제 하드웨어 연결 시 주석 해제)
try:
    from modules import sensors
    from modules import devices
    from modules import camera
    HARDWARE_AVAILABLE = True
except ImportError as e:
    print(f"⚠ 하드웨어 모듈 import 실패: {e}")
    print("  테스트 모드로 실행합니다 (가상 센서 데이터 사용)\n")
    HARDWARE_AVAILABLE = False

# MQTT 클라이언트 import
from modules import mqtt_client as mqtt

# ==================== 가상 센서 (테스트용) ====================

class MockSensors:
    """테스트용 가상 센서"""
    @staticmethod
    def get_all_sensor_data():
        import random
        return {
            'temperature': round(random.uniform(20, 30), 1),
            'humidity': round(random.uniform(50, 70), 1),
            'light': round(random.uniform(400, 900), 0),
            'co2': round(random.uniform(400, 600), 0),
            'ec': round(random.uniform(1.0, 2.0), 2),
            'timestamp': time.time()
        }


class MockDevices:
    """테스트용 가상 디바이스"""
    pump_state = False
    led_state = False
    fan_state = False
    
    @classmethod
    def control_pump(cls, state):
        cls.pump_state = state
        print(f"[테스트] 펌프 {'ON' if state else 'OFF'}")
        return True
    
    @classmethod
    def control_led(cls, state):
        cls.led_state = state
        print(f"[테스트] LED {'ON' if state else 'OFF'}")
        return True
    
    @classmethod
    def control_fan(cls, state):
        cls.fan_state = state
        print(f"[테스트] 팬 {'ON' if state else 'OFF'}")
        return True
    
    @classmethod
    def get_all_device_status(cls):
        return {
            'pump': cls.pump_state,
            'led': cls.led_state,
            'fan': cls.fan_state
        }
    
    @classmethod
    def turn_off_all(cls):
        cls.control_pump(False)
        cls.control_led(False)
        cls.control_fan(False)


class MockCamera:
    """테스트용 가상 카메라"""
    @staticmethod
    def capture_image():
        print("[테스트] 카메라 촬영 (실제 하드웨어 없음)")
        return None


# 실제/가상 모듈 선택
if HARDWARE_AVAILABLE:
    sensor_module = sensors
    device_module = devices
    camera_module = camera
else:
    sensor_module = MockSensors()
    device_module = MockDevices()
    camera_module = MockCamera()

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
            mqtt.send_sensor_data(data)
            
            # 대기
            time.sleep(SENSOR_INTERVAL)
            break
        except Exception as e:
            print(f"센서 루프 오류: {e}")
            time.sleep(5)


# ==================== 명령 처리 ====================

def handle_command(data):
    """
    서버로부터 받은 명령 처리
    data 예시: 
                "type": "pump" | "led" | "fan" | "all" | "camera",
                "action": "on" | "off" | "capture"
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
                    mqtt.send_image(img_path)
                else:
                    print("  카메라 촬영 실패 또는 하드웨어 없음")
                
        else:
            print(f"  알 수 없는 명령 타입: {cmd_type}")
            return
        
        # 기기 상태 전송
        status = devices.get_all_device_status() # 명령 처리 후 현재 상태 전송
        mqtt.send_device_status(status) # 서버에 현재 상태 알려줌

        print(f"[명령 완료] 현재 상태: {status}\n")
        
    except Exception as e:
        print(f"명령 처리 오류: {e}")


# ==================== 종료 처리 ====================

def signal_handler(sig, frame):
    """Ctrl+C 시그널 핸들러"""
    print("\n\n시스템 종료 신호 수신...")
    cleanup()
    sys.exit(0)


def cleanup():
    """종료 전 정리 작업"""
    print("시스템 종료 중...")
    
    # 모든 기기 끄기
    if HARDWARE_AVAILABLE:
        try:
            device_module.turn_off_all()
            print("✓ 모든 기기 OFF")
        except Exception as e:
            print(f"⚠ 기기 종료 오류: {e}")
    
    # MQTT 연결 해제
    mqtt.disconnect_from_broker()
    
    print("✓ 종료 완료")


# ==================== 메인 ====================

def main():
    """메인 함수"""
    print("=" * 60)
    print("    🌱 스마트팜 시스템 시작 (MQTT 버전) 🌱")
    print("=" * 60)
    print(f"디바이스 ID: {DEVICE_ID}")
    print(f"MQTT 브로커: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"센서 읽기 주기: {SENSOR_INTERVAL}초")
    print(f"하드웨어 모드: {'실제' if HARDWARE_AVAILABLE else '테스트'}")
    print("=" * 60)
    print()
    
    # Ctrl+C 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    
    # MQTT 명령 콜백 등록
    mqtt.set_command_callback(handle_command)
    
    # MQTT 브로커 연결
    print("MQTT 브로커 연결 중...")
    if mqtt.connect_to_broker():
        print("✓ MQTT 연결 성공\n")
    else:
        print("✗ MQTT 연결 실패")
        print("  브로커가 실행 중인지 확인하세요:")
        print(f"  sudo systemctl status mosquitto\n")
        
        response = input("오프라인 모드로 계속할까요? (y/n): ")
        if response.lower() != 'y':
            print("종료합니다.")
            return
        print("\n⚠ 오프라인 모드로 실행 (센서만 작동)\n")
    
    # 센서 루프를 별도 스레드로 실행
    sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
    sensor_thread.start()
    
    print("✓ 시스템 가동 중...")
    print("종료하려면 Ctrl+C를 누르세요\n")
    print("-" * 60)
    
    # 메인 루프 (명령 대기)
    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    
    # 종료 처리
    cleanup()


if __name__ == "__main__":
    main()