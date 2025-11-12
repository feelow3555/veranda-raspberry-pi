"""
센서 모듈 - 온습도, 조도, CO2, EC 센서 읽기
"""

import time
from config import *

# GPIO 초기화 (라즈베리파이에서만)
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM) # BCM 모드: GPIO 번호로 핀 지정
    GPIO.setwarnings(False) # 경고 메시지 끄기
except:
    GPIO = None
    print("! GPIO 없음 - 테스트 모드")

# ==================== 온습도 센서 (HTU21D) ====================

# HTU21D 센서 초기화
try:
    from adafruit_htu21d import HTU21D # HTU21D 센서 라이브러리
    import busio # I2C 통신 라이브러리

    # I2C 통신 설정 (GPIO 2=SDA, GPIO 3=SCL)
    i2c = busio.I2C(I2C_SCL, I2C_SDA) # I2C 통신 객체 생성
    htu_sensor = HTU21D(i2c) # HTU21D 센서 객체 생성
    print("HTU21D 온습도 센서 초기화 완료")
except Exception as e:
    htu_sensor = None
    print(f"HTU21D 초기화 실패 (라즈베리파이 아니면 정상): {e}")


def read_temperature():
    """
    온도 읽기
    반환: float (섭씨 온도)
    """
    try:
        if htu_sensor:
            temp = float(htu_sensor.temperature)
            return round(temp, 1) # 소수점 1자리까지
        else:
            # 센서 없을때 테스트용 값
            return 25.0
    except Exception as e:
        print(f"온도 읽기 오류: {e}")
        return 0.0
    

def read_humidity():
    """
    습도 읽기
    반환: float (상대습도 %)
    """

    try:
        if htu_sensor:
            humidity = float(htu_sensor.relative_humidity)
            return round(humidity, 1) # 소수점 1자리까지
        else:
            # 센서 없을때 테스트용 값
            return 60.0
    except Exception as e:
        print(f"습도 읽기 오류: {e}")
        return 0.0
    



# ==================== 조도 센서 (MCP3202) ====================

# MCP3202 초기화 (SPI 통신)
try:
    import Adafruit_MCP3008

    # SPI 핀 연결 (CLK, CS, MISO, MOSI)
    mcp3202 = Adafruit_MCP3008.MCP3008(
        clk=SPI_CLK,    # GPIO 11 - 타이밍 신호 (박자)
        cs=SPI_CS,      # GPIO 8 - 라즈베리파이에서 MCP3202 데이터 전송
        miso=SPI_MISO,  # GPIO 9 - 라즈베리파이 데이터 수신
        mosi=SPI_MOSI   # GPIO 10 - 지금 너랑 얘기할게 하는 신호
    )
    print("MCP3202 조도 센서 초기화 완료")
except Exception as e:
    mcp3202 = None
    print(f"MCP3202 초기화 실패: {e}")


def read_light():
    """
    조도 읽기
    반환: int (lux 단위)
    """
    try:
        if mcp3202:
            raw_value = mcp3202.read_adc(0)  # 0-1023
            
            # lux로 변환 (센서 스펙에 따라 다름, 일반적인 공식) 나중에 백분율로 수정하거나 센서 보고 오류나면 수정
            lux = raw_value * 1000 / 1023  # 0-1000 lux
            return round(lux, 0)
        else:
            return 500  # 테스트용
    except Exception as e:
        print(f"조도 읽기 오류: {e}")
        return 0
    

# ==================== CO2 센서 (MCP3008) ====================

# MCP3008 ADC 초기화 (아날로그 센서용) - ec CO2 둘다 아날로그 -> 디지털이라 MCP3008에 연결해서 빵판에 꽂아야함 라즈베리파이는 디지털 밖에 못 읽음

try:
    import spidev
    
    spi = spidev.SpiDev()
    spi.open(0, 0)  # SPI 버스 0, 디바이스 0
    spi.max_speed_hz = 1000000  # 1MHz 속도
    print("✓ MCP3008 ADC 초기화 완료")
except Exception as e:
    spi = None
    print(f"! MCP3008 초기화 실패: {e}")


def read_adc(channel):
    """
    MCP3008 ADC에서 아날로그 값 읽기
    channel: 0-7 (MCP3008은 8채널)
    반환: 0-1023
    """
    if spi is None:
        return 512  # 테스트용 중간값
    
    try:
        # MCP3008 통신 프로토콜
        adc = spi.xfer2([1, (8 + channel) << 4, 0]) # MCP3008과 통신
        data = ((adc[1] & 3) << 8) + adc[2] # 받은 데이터를 0-1023 숫자로 변환
        return data
    except Exception as e:
        print(f"ADC 읽기 오류: {e}")
        return 0


def read_co2():
    """
    CO2 센서 읽기
    반환: float (ppm)
    """
    try:
        # ADC 채널 0에서 값 읽기
        raw_value = read_adc(ADC_CO2_CHANNEL)
        
        # CO2 센서 변환 공식 (센서마다 다름!)
        # 일반적인 CO2 센서: 0-5000 ppm 범위
        co2_ppm = (raw_value / 1023) * 5000
        
        return round(co2_ppm, 0)
    except Exception as e:
        print(f"CO2 읽기 오류: {e}")
        return 430.0  # 테스트용 기본값 (실내 평균)
    # 공식은 임시고 데이터 시트 보고 수정

# ==================== EC 센서 ====================

def read_ec():
    """
    EC (전기전도도) 센서 읽기
    반환: float (mS/cm)
    """
    try:
        # ADC 채널 1에서 값 읽기
        raw_value = read_adc(ADC_EC_CHANNEL)
        
        # EC 센서 변환 공식 (센서마다 다름!)
        # 일반적인 EC 센서: 0-20 mS/cm 범위
        ec_value = (raw_value / 1023) * 20
        
        return round(ec_value, 2)  # 소수점 2자리
    except Exception as e:
        print(f"EC 읽기 오류: {e}")
        return 1.5  # 테스트용 기본값
    

# ==================== 전체 센서 데이터 ====================

def get_all_sensor_data():
    """
    모든 센서 데이터 한 번에 읽기
    반환: dict (딕셔너리)
    """
    return {
        'temperature': read_temperature(),
        'humidity': read_humidity(),
        'light': read_light(),
        'co2': read_co2(),
        'ec': read_ec(),
        'timestamp': time.time()  # 현재 시간 (유닉스 타임스탬프)
    }

if __name__ == "__main__":
    print("=== 센서 테스트 ===")
    
    # 개별 테스트
    print(f"온도: {read_temperature()}°C")
    print(f"습도: {read_humidity()}%")
    print(f"조도: {read_light()} lux")
    print(f"CO2: {read_co2()} ppm")
    print(f"EC: {read_ec()} mS/cm")
    
    print("\n=== 전체 데이터 ===")
    data = get_all_sensor_data()
    print(data)