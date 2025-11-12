"""
MQTT 클라이언트 모듈 - 센서 데이터 전송 및 제어 명령 수신
"""
import json
import time
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
from config import *

# 전역 변수
client = None
is_connected = False
command_callback = None

# ==================== MQTT 이벤트 핸들러 ====================

def on_connect(client, userdata, flags, rc, properties=None):
    """브로커 연결 시 호출"""
    global is_connected
    
    if rc == 0:
        is_connected = True
        print(f"✓ MQTT 브로커 연결 성공: {MQTT_BROKER}:{MQTT_PORT}")
        
        # 제어 명령 토픽 구독
        client.subscribe(MQTT_TOPIC_CONTROL)
        print(f"✓ 토픽 구독: {MQTT_TOPIC_CONTROL}")
        
        # 연결 알림 전송
        status = {
            "deviceId": DEVICE_ID,
            "status": "online",
            "timestamp": time.time()
        }
        client.publish(MQTT_TOPIC_STATUS, json.dumps(status), qos=1)
        
    else:
        is_connected = False
        print(f"✗ MQTT 연결 실패 (코드: {rc})")
        error_messages = {
            1: "잘못된 프로토콜 버전",
            2: "잘못된 클라이언트 ID",
            3: "서버 사용 불가",
            4: "잘못된 사용자명/비밀번호",
            5: "인증 실패"
        }
        print(f"  원인: {error_messages.get(rc, '알 수 없는 오류')}")


def on_disconnect(client, userdata, rc, properties=None):
    """브로커 연결 끊김 시 호출"""
    global is_connected
    is_connected = False
    
    if rc == 0:
        print("✓ MQTT 브로커 정상 연결 해제")
    else:
        print(f"✗ MQTT 연결 끊김 (코드: {rc})")
        print("  재연결 시도 중...")


def on_message(client, userdata, msg):
    """메시지 수신 시 호출 (제어 명령)"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        if DEBUG:
            print(f"← 메시지 수신 [{topic}]: {payload}")
        
        # 명령 콜백 실행
        if command_callback and topic == MQTT_TOPIC_CONTROL:
            command_callback(payload)
            
    except json.JSONDecodeError as e:
        print(f"✗ JSON 파싱 오류: {e}")
    except Exception as e:
        print(f"✗ 메시지 처리 오류: {e}")


def on_publish(client, userdata, mid, rc=None, properties=None):
    """메시지 발행 완료 시 호출"""
    if DEBUG:
        print(f"  → 메시지 발행 완료 (ID: {mid})")


# ==================== MQTT 연결 관리 ====================

def connect_to_broker():
    """MQTT 브로커에 연결"""
    global client
    
    try:
        # 클라이언트 생성
        client = mqtt.Client(
            client_id=DEVICE_ID,
            callback_api_version=CallbackAPIVersion.VERSION2
        )
        
        # 이벤트 핸들러 등록
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        client.on_publish = on_publish
        
        # 인증 설정 (필요시)
        if MQTT_USERNAME and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        # Last Will & Testament (비정상 종료 시 자동 전송)
        lwt_payload = {
            "deviceId": DEVICE_ID,
            "status": "offline",
            "timestamp": time.time()
        }
        client.will_set(
            MQTT_TOPIC_STATUS, 
            json.dumps(lwt_payload), 
            qos=1, 
            retain=True
        )
        
        # 브로커 연결
        print(f"MQTT 브로커 연결 중: {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        
        # 백그라운드 네트워크 루프 시작
        client.loop_start()
        
        # 연결 대기 (최대 5초)
        timeout = 5
        start_time = time.time()
        while not is_connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        return is_connected
        
    except Exception as e:
        print(f"✗ MQTT 연결 오류: {e}")
        return False


def disconnect_from_broker():
    """MQTT 브로커 연결 해제"""
    global client, is_connected
    
    if client and is_connected:
        try:
            # 오프라인 상태 전송
            status = {
                "deviceId": DEVICE_ID,
                "status": "offline",
                "timestamp": time.time()
            }
            client.publish(MQTT_TOPIC_STATUS, json.dumps(status), qos=1)
            
            # 연결 해제
            client.loop_stop()
            client.disconnect()
            is_connected = False
            print("✓ MQTT 브로커 연결 해제")
            
        except Exception as e:
            print(f"✗ MQTT 연결 해제 오류: {e}")


# ==================== 데이터 전송 ====================

def send_sensor_data(data):
    """센서 데이터 전송"""
    if not is_connected:
        if DEBUG:
            print("⚠ MQTT 미연결 - 센서 데이터 전송 불가")
        return False
    
    try:
        # 디바이스 ID 추가
        payload = {
            "deviceId": DEVICE_ID,
            **data
        }
        
        # JSON으로 변환
        message = json.dumps(payload)
        
        # 토픽에 발행
        result = client.publish(MQTT_TOPIC_SENSOR, message, qos=0)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            if DEBUG:
                print(f"→ 센서 데이터 전송: {payload}")
            return True
        else:
            print(f"✗ 센서 데이터 전송 실패 (코드: {result.rc})")
            return False
            
    except Exception as e:
        print(f"✗ 센서 데이터 전송 오류: {e}")
        return False


def send_device_status(data):
    """디바이스 상태 전송"""
    if not is_connected:
        if DEBUG:
            print("⚠ MQTT 미연결 - 상태 전송 불가")
        return False
    
    try:
        # 디바이스 ID 추가
        payload = {
            "deviceId": DEVICE_ID,
            "timestamp": time.time(),
            **data
        }
        
        # JSON으로 변환
        message = json.dumps(payload)
        
        # 토픽에 발행 (QoS 1로 보장)
        result = client.publish(MQTT_TOPIC_STATUS, message, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            if DEBUG:
                print(f"→ 디바이스 상태 전송: {payload}")
            return True
        else:
            print(f"✗ 디바이스 상태 전송 실패 (코드: {result.rc})")
            return False
            
    except Exception as e:
        print(f"✗ 디바이스 상태 전송 오류: {e}")
        return False


def send_image(image_path):
    """이미지 전송 (base64 인코딩)"""
    if not is_connected:
        if DEBUG:
            print("⚠ MQTT 미연결 - 이미지 전송 불가")
        return False
    
    try:
        import base64
        import os
        
        # 이미지 파일 읽기
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 페이로드 구성
        payload = {
            "deviceId": DEVICE_ID,
            "filename": os.path.basename(image_path),
            "timestamp": time.time(),
            "image": image_data
        }
        
        # JSON으로 변환
        message = json.dumps(payload)
        
        # 토픽에 발행 (QoS 1로 보장)
        result = client.publish(MQTT_TOPIC_IMAGE, message, qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"→ 이미지 전송: {image_path} ({len(image_data)} bytes)")
            return True
        else:
            print(f"✗ 이미지 전송 실패 (코드: {result.rc})")
            return False
            
    except FileNotFoundError:
        print(f"✗ 이미지 파일 없음: {image_path}")
        return False
    except Exception as e:
        print(f"✗ 이미지 전송 오류: {e}")
        return False


# ==================== 명령 콜백 ====================

def set_command_callback(callback):
    """
    제어 명령 수신 시 실행할 콜백 함수 등록
    callback(data) 형식
    """
    global command_callback
    command_callback = callback
    if DEBUG:
        print("✓ 명령 콜백 함수 등록 완료")


# ==================== 상태 확인 ====================

def get_connection_status():
    """현재 MQTT 연결 상태 반환"""
    return is_connected


# ==================== 테스트 ====================

if __name__ == "__main__":
    print("=== MQTT 클라이언트 테스트 ===\n")
    
    # 테스트 명령 핸들러
    def test_command_handler(data):
        print(f"[테스트] 명령 수신: {data}")
    
    # 콜백 등록
    set_command_callback(test_command_handler)
    
    # 브로커 연결
    if connect_to_broker():
        print("\n연결 성공! 10초간 대기...\n")
        
        # 테스트 센서 데이터 전송
        test_data = {
            "temperature": 25.5,
            "humidity": 60.2,
            "light": 820,
            "co2": 430,
            "ec": 1.5,
            "timestamp": time.time()
        }
        send_sensor_data(test_data)
        
        # 테스트 상태 전송
        test_status = {
            "pump": True,
            "led": False,
            "fan": True
        }
        send_device_status(test_status)
        
        # 대기
        time.sleep(10)
        
        # 연결 해제
        disconnect_from_broker()
    else:
        print("\n연결 실패!")
    
    print("\n테스트 종료")