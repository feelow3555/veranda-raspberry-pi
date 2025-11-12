"""
기기 제어 모듈 - 펌프, LED, 팬 제어
"""
from config import *

# GPIO 초기화 (라즈베리파이에서만)
try:
    import RPi.GPIO as GPIO
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # GPIO 핀을 출력 모드로 설정
    GPIO.setup(PIN_PUMP, GPIO.OUT)
    GPIO.setup(PIN_LED, GPIO.OUT)
    GPIO.setup(PIN_FAN, GPIO.OUT)
    
    # 초기 상태: 모두 꺼짐
    GPIO.output(PIN_PUMP, GPIO.LOW)
    GPIO.output(PIN_LED, GPIO.LOW)
    GPIO.output(PIN_FAN, GPIO.LOW)
    
    print("✓ 기기 제어 GPIO 초기화 완료")
except:
    GPIO = None
    print("! GPIO 없음 - 테스트 모드")


# ==================== 펌프 제어 ====================

def control_pump(state):
    """
    물 펌프 제어
    state: True (켜기) / False (끄기)
    """
    try:
        if state:
            GPIO.output(PIN_PUMP, GPIO.HIGH)
            print("펌프 ON")
        else:
            GPIO.output(PIN_PUMP, GPIO.LOW)
            print("펌프 OFF")
        return True
    except Exception as e:
        print(f"펌프 제어 오류: {e}")
        return False


def get_pump_status():
    """
    펌프 상태 확인
    반환: True (켜짐) / False (꺼짐)
    """
    return GPIO.input(PIN_PUMP) == GPIO.HIGH
    # GPIO.input(핀): 현재 핀 전압 읽기
    # GPIO.HIGH와 같으면 True (켜짐)
    # 다르면 False (꺼짐)  


# ==================== LED 제어 ====================

def control_led(state):
    """
    LED 제어
    state: True (켜기) / False (끄기)
    """
    try:
        if state:
            GPIO.output(PIN_LED, GPIO.HIGH)
            print("LED ON")
        else:
            GPIO.output(PIN_LED, GPIO.LOW)
            print("LED OFF")
        return True
    except Exception as e:
        print(f"LED 제어 오류: {e}")
        return False


def get_led_status():
    """LED 상태 확인"""
    return GPIO.input(PIN_LED) == GPIO.HIGH


# ==================== 팬 제어 ====================

def control_fan(state):
    """
    팬 제어
    state: True (켜기) / False (끄기)
    """
    try:
        if state:
            GPIO.output(PIN_FAN, GPIO.HIGH)
            print("팬 ON")
        else:
            GPIO.output(PIN_FAN, GPIO.LOW)
            print("팬 OFF")
        return True
    except Exception as e:
        print(f"팬 제어 오류: {e}")
        return False


def get_fan_status():
    """팬 상태 확인"""
    return GPIO.input(PIN_FAN) == GPIO.HIGH


# ==================== 전체 상태 확인 ====================

def get_all_device_status():
    """
    모든 기기 상태 확인
    반환: dict
    """
    return {
        'pump': get_pump_status(),
        'led': get_led_status(),
        'fan': get_fan_status()
    }


def turn_off_all():
    """모든 기기 끄기 (비상 정지)"""
    control_pump(False)
    control_led(False)
    control_fan(False)
    print("모든 기기 OFF")

# ==================== 테스트 ====================

if __name__ == "__main__":
    import time
    
    print("=== 기기 제어 테스트 ===")
    
    # 펌프 테스트
    print("\n1. 펌프 테스트")
    control_pump(True)
    time.sleep(2)
    control_pump(False)
    
    # LED 테스트
    print("\n2. LED 테스트")
    control_led(True)
    time.sleep(2)
    control_led(False)
    
    # 팬 테스트
    print("\n3. 팬 테스트")
    control_fan(True)
    time.sleep(2)
    control_fan(False)
    
    # 전체 상태
    print("\n4. 전체 상태")
    status = get_all_device_status()
    print(status)