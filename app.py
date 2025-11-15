"""
스마트팜 메인 프로그램 (MQTT 버전)

주요 기능:
1. 센서 데이터 주기적 수집 및 MQTT 전송
   - HTU21D: 온도/습도 (I2C)
   - MCP3008: ADC 변환기 (SPI)
   - LightSensor: 조도 센서 (MCP3008 CH0)
   - CO2Sensor: CO2 센서 (UART)
   - TDSSensor: EC/TDS 센서 (MCP3008 CH1)

2. MQTT 명령 수신 및 기기 제어
   - 펌프, LED, 팬 제어
   - 카메라 촬영

3. 안전한 종료 처리
   - Ctrl+C 시 모든 기기 OFF
   - MQTT 연결 해제
"""

import time
import threading
import signal
import sys
from datetime import datetime

# 설정 파일 import
from config import *

# MQTT 클라이언트 import
from modules import mqtt_client as mqtt

# ==================== 센서 및 디바이스 모듈 Import ====================

# 센서 모듈들을 개별적으로 import
try:
    from sensors.htu21d import HTU21DSensor
    from sensors.light import LightSensor
    from sensors.co2 import CO2Sensor
    from sensors.tds import TDSSensor
    SENSORS_AVAILABLE = True
    print("✓ 센서 모듈 import 성공")
except ImportError as e:
    print(f"⚠ 센서 모듈 import 실패: {e}")
    SENSORS_AVAILABLE = False

# 디바이스 제어 모듈 import
# TODO: 나중에 라즈베리파이에 디바이스 연결 시 주석 해제
# try:
#     from modules import devices
#     DEVICES_AVAILABLE = True
#     print("✓ 디바이스 모듈 import 성공")
# except ImportError as e:
#     print(f"⚠ 디바이스 모듈 import 실패: {e}")
#     DEVICES_AVAILABLE = False
DEVICES_AVAILABLE = False  # 현재는 디바이스 미사용

# 카메라 모듈 import
# TODO: 나중에 카메라 사용 시 주석 해제
# try:
#     from modules import camera
#     CAMERA_AVAILABLE = True
#     print("✓ 카메라 모듈 import 성공")
# except ImportError as e:
#     print(f"⚠ 카메라 모듈 import 실패: {e}")
#     CAMERA_AVAILABLE = False
CAMERA_AVAILABLE = False  # 현재는 카메라 미사용

print()  # 줄바꿈

# ==================== 센서 객체 초기화 ====================

# 전역 센서 객체들
htu21d_sensor = None
light_sensor = None
co2_sensor = None
tds_sensor = None

def init_sensors():
    """
    모든 센서 초기화
    
    각 센서를 개별적으로 초기화하고 전역 변수에 저장합니다.
    초기화 실패한 센서는 None으로 유지됩니다.
    """
    global htu21d_sensor, light_sensor, co2_sensor, tds_sensor
    
    print("=" * 60)
    print("센서 초기화 시작...")
    print("=" * 60)
    
    if not SENSORS_AVAILABLE:
        print("⚠ 센서 모듈이 없어 테스트 모드로 실행됩니다\n")
        return
    
    # HTU21D 온습도 센서 (I2C)
    try:
        htu21d_sensor = HTU21DSensor()
    except Exception as e:
        print(f"✗ HTU21D 초기화 실패: {e}")
    
    # 조도 센서 (MCP3008 CH0)
    try:
        light_sensor = LightSensor(channel=ADC_LIGHT_CHANNEL)
    except Exception as e:
        print(f"✗ 조도 센서 초기화 실패: {e}")
    
    # CO2 센서 (UART)
    try:
        co2_sensor = CO2Sensor(port=CO2_SERIAL_PORT, baudrate=CO2_BAUDRATE)
    except Exception as e:
        print(f"✗ CO2 센서 초기화 실패: {e}")
    
    # TDS/EC 센서 (MCP3008 CH1)
    try:
        tds_sensor = TDSSensor(channel=ADC_TDS_CHANNEL)
    except Exception as e:
        print(f"✗ TDS 센서 초기화 실패: {e}")
    
    print("=" * 60)
    print()


def get_all_sensor_data():
    """
    모든 센서에서 데이터 수집
    
    Returns:
        dict: 센서 데이터 딕셔너리
        {
            'temperature': float,  # 온도 (°C)
            'humidity': float,     # 습도 (%)
            'light': int,          # 조도 (lux)
            'co2': int,            # CO2 (ppm)
            'ec': float,           # EC (mS/cm)
            'tds': float,          # TDS (ppm)
            'timestamp': float     # Unix timestamp
        }
    
    Note:
        - 센서가 없거나 읽기 실패 시 해당 값은 None
        - 테스트 모드에서는 랜덤 데이터 반환
    """
    # 테스트 모드: 가상 센서 데이터
    if not SENSORS_AVAILABLE:
        import random
        return {
            'temperature': round(random.uniform(20, 30), 1),
            'humidity': round(random.uniform(50, 70), 1),
            'light': round(random.uniform(400, 900), 0),
            'co2': round(random.uniform(400, 600), 0),
            'ec': round(random.uniform(1.0, 2.0), 2),
            'tds': round(random.uniform(500, 1000), 1),
            'timestamp': time.time()
        }
    
    # 실제 센서 데이터 수집
    data = {'timestamp': time.time()}
    
    # HTU21D - 온도/습도
    if htu21d_sensor:
        try:
            data['temperature'] = htu21d_sensor.read_temperature()
            data['humidity'] = htu21d_sensor.read_humidity()
        except Exception as e:
            print(f"✗ HTU21D 읽기 오류: {e}")
            data['temperature'] = None
            data['humidity'] = None
    else:
        data['temperature'] = None
        data['humidity'] = None
    
    # 조도 센서
    if light_sensor:
        try:
            data['light'] = light_sensor.read_lux()
        except Exception as e:
            print(f"✗ 조도 센서 읽기 오류: {e}")
            data['light'] = None
    else:
        data['light'] = None
    
    # CO2 센서
    if co2_sensor:
        try:
            data['co2'] = co2_sensor.read_co2()
        except Exception as e:
            print(f"✗ CO2 센서 읽기 오류: {e}")
            data['co2'] = None
    else:
        data['co2'] = None
    
    # TDS/EC 센서
    if tds_sensor:
        try:
            # HTU21D에서 읽은 온도로 보정 (없으면 기본값 25°C)
            temp = data.get('temperature', 25.0) or 25.0
            data['ec'] = tds_sensor.read_ec(temperature=temp)
            data['tds'] = tds_sensor.read_tds(temperature=temp)
        except Exception as e:
            print(f"✗ TDS 센서 읽기 오류: {e}")
            data['ec'] = None
            data['tds'] = None
    else:
        data['ec'] = None
        data['tds'] = None
    
    return data


# ==================== 가상 디바이스 (테스트용) ====================

class MockDevices:
    """
    테스트용 가상 디바이스
    
    실제 하드웨어 없이도 명령 처리를 테스트할 수 있습니다.
    """
    pump_state = False
    led_state = False
    fan_state = False
    
    @classmethod
    def control_pump(cls, state):
        """펌프 제어 (테스트)"""
        cls.pump_state = state
        print(f"[테스트] 펌프 {'ON' if state else 'OFF'}")
        return True
    
    @classmethod
    def control_led(cls, state):
        """LED 제어 (테스트)"""
        cls.led_state = state
        print(f"[테스트] LED {'ON' if state else 'OFF'}")
        return True
    
    @classmethod
    def control_fan(cls, state):
        """팬 제어 (테스트)"""
        cls.fan_state = state
        print(f"[테스트] 팬 {'ON' if state else 'OFF'}")
        return True
    
    @classmethod
    def get_all_device_status(cls):
        """모든 기기 상태 조회"""
        return {
            'pump': cls.pump_state,
            'led': cls.led_state,
            'fan': cls.fan_state
        }
    
    @classmethod
    def turn_off_all(cls):
        """모든 기기 끄기"""
        cls.control_pump(False)
        cls.control_led(False)
        cls.control_fan(False)


class MockCamera:
    """
    테스트용 가상 카메라
    
    실제 카메라 없이도 촬영 명령을 테스트할 수 있습니다.
    """
    @staticmethod
    def capture_image():
        """카메라 촬영 (테스트)"""
        print("[테스트] 카메라 촬영 (실제 하드웨어 없음)")
        return None


# 실제/가상 모듈 선택
# TODO: 나중에 디바이스와 카메라 연결 시 아래 주석 해제하고 Mock 클래스 사용 중지
# device_module = devices if DEVICES_AVAILABLE else MockDevices()
# camera_module = camera if CAMERA_AVAILABLE else MockCamera()

# 현재는 테스트용 Mock 클래스만 사용
device_module = MockDevices()
camera_module = MockCamera()


# ==================== 센서 데이터 전송 ====================

def sensor_loop():
    """
    센서 데이터 주기적으로 읽고 MQTT 전송
    
    SENSOR_INTERVAL(기본 5초)마다 실행됩니다.
    무한 루프로 동작하며, 오류 발생 시 재시도합니다.
    """
    print("✓ 센서 모니터링 시작...")
    print(f"  주기: {SENSOR_INTERVAL}초마다 데이터 수집 및 전송\n")
    
    while True:
        try:
            # 모든 센서 데이터 읽기
            data = get_all_sensor_data()
            
            # 데이터 로깅 (DEBUG 모드일 때만)
            if DEBUG:
                timestamp_str = datetime.fromtimestamp(data['timestamp']).strftime('%H:%M:%S')
                print(f"[{timestamp_str}] 센서 데이터:")
                print(f"  온도: {data['temperature']}°C")
                print(f"  습도: {data['humidity']}%")
                print(f"  조도: {data['light']} lux")
                print(f"  CO2: {data['co2']} ppm")
                print(f"  EC: {data['ec']} mS/cm")
                print(f"  TDS: {data['tds']} ppm")
                print()
            
            # MQTT를 통해 서버로 전송
            mqtt.send_sensor_data(data)
            
            # 다음 측정까지 대기
            time.sleep(SENSOR_INTERVAL)
            
        except Exception as e:
            print(f"✗ 센서 루프 오류: {e}")
            print("  5초 후 재시도...\n")
            time.sleep(5)


# ==================== 명령 처리 ====================

def handle_command(data):
    """
    MQTT로 수신한 제어 명령 처리
    
    Args:
        data (dict): 명령 데이터
        {
            "type": "pump" | "led" | "fan" | "all" | "camera",
            "action": "on" | "off" | "capture"
        }
    
    처리 흐름:
        1. 명령 타입과 액션 확인
        2. 해당 기기 제어
        3. 현재 기기 상태를 MQTT로 전송
    
    지원 명령:
        - pump on/off: 물펌프 제어 (현재 비활성화)
        - led on/off: LED 조명 제어 (현재 비활성화)
        - fan on/off: 환풍기 제어 (현재 비활성화)
        - all off: 모든 기기 끄기 (현재 비활성화)
        - camera capture: 사진 촬영 및 전송 (현재 비활성화)
    
    Note:
        현재 디바이스가 연결되지 않아 테스트 모드로 동작합니다.
        실제 디바이스 연결 후에는 정상적으로 제어됩니다.
    """
    try:
        cmd_type = data.get('type')
        action = data.get('action')
        
        print(f"[명령 수신] {cmd_type} - {action} (테스트 모드)")
        
        # ========== 펌프 제어 (테스트) ==========
        if cmd_type == 'pump':
            if action == 'on':
                device_module.control_pump(True)
            elif action == 'off':
                device_module.control_pump(False)
            else:
                print(f"  ⚠ 알 수 없는 액션: {action}")
                return
        
        # ========== LED 제어 (테스트) ==========
        elif cmd_type == 'led':
            if action == 'on':
                device_module.control_led(True)
            elif action == 'off':
                device_module.control_led(False)
            else:
                print(f"  ⚠ 알 수 없는 액션: {action}")
                return
        
        # ========== 팬 제어 (테스트) ==========
        elif cmd_type == 'fan':
            if action == 'on':
                device_module.control_fan(True)
            elif action == 'off':
                device_module.control_fan(False)
            else:
                print(f"  ⚠ 알 수 없는 액션: {action}")
                return
        
        # ========== 모든 기기 끄기 (테스트) ==========
        elif cmd_type == 'all':
            if action == 'off':
                device_module.turn_off_all()
                print("  ✓ 모든 기기 OFF (테스트)")
            else:
                print(f"  ⚠ 알 수 없는 액션: {action}")
                return
        
        # ========== 카메라 촬영 (테스트) ==========
        elif cmd_type == 'camera':
            if action == 'capture':
                print("  📷 카메라 촬영 시작... (테스트)")
                img_path = camera_module.capture_image()
                
                if img_path:
                    print(f"  ✓ 촬영 완료: {img_path}")
                    # 이미지를 MQTT로 전송
                    mqtt.send_image(img_path)
                else:
                    print("  ⚠ 카메라 촬영 실패 (테스트 모드)")
            else:
                print(f"  ⚠ 알 수 없는 액션: {action}")
                return
        
        # ========== 알 수 없는 명령 ==========
        else:
            print(f"  ✗ 알 수 없는 명령 타입: {cmd_type}")
            return
        
        # ========== 기기 상태 전송 (테스트) ==========
        # 명령 처리 후 현재 상태를 서버로 전송
        if cmd_type in ['pump', 'led', 'fan', 'all']:
            status = device_module.get_all_device_status()
            mqtt.send_device_status(status)
            
            if DEBUG:
                print(f"[상태 전송] 펌프:{status['pump']}, LED:{status['led']}, 팬:{status['fan']} (테스트)\n")
        
    except Exception as e:
        print(f"✗ 명령 처리 오류: {e}\n")


# ==================== 종료 처리 ====================

def signal_handler(sig, frame):
    """
    Ctrl+C 시그널 핸들러
    
    사용자가 Ctrl+C를 누르면 안전하게 종료합니다.
    """
    print("\n\n종료 신호 수신 (Ctrl+C)...")
    cleanup()
    sys.exit(0)


def cleanup():
    """
    프로그램 종료 전 정리 작업
    
    1. 모든 센서 종료
    2. 모든 기기 OFF
    3. MQTT 연결 해제
    """
    print("=" * 60)
    print("시스템 종료 중...")
    print("=" * 60)
    
    # 1. 센서 정리
    if SENSORS_AVAILABLE:
        try:
            if light_sensor:
                light_sensor.close()
            if tds_sensor:
                tds_sensor.close()
            if co2_sensor:
                co2_sensor.close()
            print("✓ 센서 종료 완료")
        except Exception as e:
            print(f"⚠ 센서 종료 오류: {e}")
    
    # 2. 모든 기기 끄기 (현재는 테스트 모드)
    # TODO: 나중에 실제 디바이스 연결 시 활성화
    try:
        device_module.turn_off_all()
        print("✓ 모든 기기 OFF (테스트 모드)")
    except Exception as e:
        print(f"⚠ 기기 종료 오류: {e}")
    
    # 3. MQTT 연결 해제
    try:
        mqtt.disconnect_from_broker()
        print("✓ MQTT 연결 해제")
    except Exception as e:
        print(f"⚠ MQTT 해제 오류: {e}")
    
    print("=" * 60)
    print("시스템 종료 완료")
    print("=" * 60)


# ==================== 메인 ====================

def main():
    """
    메인 함수
    
    프로그램 실행 순서:
        1. 시스템 정보 출력
        2. 시그널 핸들러 등록
        3. 센서 초기화
        4. MQTT 브로커 연결
        5. 센서 루프 스레드 시작
        6. 메인 루프 (명령 대기)
    """
    
    # ========== 시스템 정보 출력 ==========
    print()
    print("=" * 60)
    print("    🌱 스마트팜 시스템 시작 (MQTT 버전) 🌱")
    print("=" * 60)
    print(f"디바이스 ID: {DEVICE_ID}")
    print(f"MQTT 브로커: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"센서 읽기 주기: {SENSOR_INTERVAL}초")
    print()
    print("사용 가능한 모듈:")
    print(f"  센서: {'✓' if SENSORS_AVAILABLE else '✗ (테스트 모드)'}")
    print(f"  디바이스: {'✓' if DEVICES_AVAILABLE else '✗ (테스트 모드)'}")
    print(f"  카메라: {'✓' if CAMERA_AVAILABLE else '✗ (테스트 모드)'}")
    print("=" * 60)
    print()
    
    # ========== 시그널 핸들러 등록 ==========
    # Ctrl+C 누르면 signal_handler 함수 호출
    signal.signal(signal.SIGINT, signal_handler)
    
    # ========== 센서 초기화 ==========
    init_sensors()
    
    # ========== MQTT 명령 콜백 등록 ==========
    # MQTT로 명령이 오면 handle_command 함수 호출
    mqtt.set_command_callback(handle_command)
    
    # ========== MQTT 브로커 연결 ==========
    print("MQTT 브로커 연결 중...")
    if mqtt.connect_to_broker():
        print("✓ MQTT 연결 성공\n")
    else:
        print("✗ MQTT 연결 실패")
        print("  브로커가 실행 중인지 확인하세요:")
        print(f"  sudo systemctl status mosquitto\n")
        
        # 오프라인 모드 계속 여부 확인
        response = input("오프라인 모드로 계속할까요? (y/n): ")
        if response.lower() != 'y':
            print("종료합니다.")
            return
        print("\n⚠ 오프라인 모드로 실행 (센서만 작동)\n")
    
    # ========== 센서 루프 스레드 시작 ==========
    # 별도 스레드에서 센서 데이터를 주기적으로 읽음
    # daemon=True: 메인 스레드 종료 시 자동으로 종료
    sensor_thread = threading.Thread(target=sensor_loop, daemon=True)
    sensor_thread.start()
    
    # ========== 시스템 가동 메시지 ==========
    print("=" * 60)
    print("✓ 시스템 가동 중...")
    print("  - 센서 모니터링: 백그라운드 실행")
    print("  - MQTT 명령 대기: 활성")
    print()
    print("종료하려면 Ctrl+C를 누르세요")
    print("=" * 60)
    print()
    
    # ========== 메인 루프 (명령 대기) ==========
    # 메인 스레드는 여기서 대기하며 프로그램 실행 유지
    # 실제 작업은 센서 스레드와 MQTT 콜백에서 수행
    try:
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Ctrl+C 입력 시 (signal_handler가 처리하지만 여기도 대비)
        pass
    
    # ========== 종료 처리 ==========
    cleanup()


# ==================== 프로그램 시작점 ====================

if __name__ == "__main__":
    main()