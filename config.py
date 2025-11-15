"""
스마트팜 설정 파일 - MQTT 버전
"""

# ==================== MQTT 브로커 설정 ====================
MQTT_BROKER = "localhost"  # 실제 브로커 주소로 변경 (예: 192.168.0.100)
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60

# 디바이스 ID (고유 식별자)
DEVICE_ID = "raspberry-pi-001"

# MQTT 토픽
MQTT_TOPIC_SENSOR = f"farm/{DEVICE_ID}/sensor"       # 센서 데이터 발행
MQTT_TOPIC_STATUS = f"farm/{DEVICE_ID}/status"       # 디바이스 상태 발행
MQTT_TOPIC_CONTROL = f"farm/{DEVICE_ID}/control"     # 제어 명령 구독
MQTT_TOPIC_IMAGE = f"farm/{DEVICE_ID}/image"         # 이미지 발행

# MQTT 인증 (필요시 사용)
MQTT_USERNAME = None  # "username"
MQTT_PASSWORD = None  # "password"

# ==================== 센서 읽기 주기 ====================
SENSOR_INTERVAL = 5  # 초

# ==================== 센서 설정 (라즈베리파이 GPIO 연결) =================================================

# ==================== HTU21D 온습도 센서 (I2C 통신 - 고정 핀) ====================
I2C_BUS = 1       # I2C 버스 번호
I2C_SDA = 2       # GPIO 2번 핀
I2C_SCL = 3       # GPIO 3번 핀
HTU21D_ADDR = 0x40  # I2C 주소

# ==================== CO2 센서 (UART 통신) ====================
CO2_SERIAL_PORT = "/dev/ttyAMA0"  # 또는 "/dev/serial0"
CO2_BAUDRATE = 9600

# ==================== MCP3008 ADC (SPI 통신 - 고정 핀) ====================
SPI_BUS = 0       # SPI 버스 번호
SPI_DEVICE = 0    # CE0
SPI_CLK = 11      # GPIO 11번
SPI_MISO = 9      # GPIO 9번
SPI_MOSI = 10     # GPIO 10번
SPI_CS = 8        # GPIO 8번

# ==================== EC/TDS 센서 (아날로그 - MCP3008 ADC 사용) ====================
ADC_TDS_CHANNEL = 1   # MCP3008의 CH1

# ==================== 조도 센서 (아날로그 - MCP3008 ADC 사용) ====================
ADC_LIGHT_CHANNEL = 0   # MCP3008의 CH0






# ==================== 기기 제어 모드 설정 =============================================================
# 제어 방식 선택: "USB" 또는 "GPIO"
# - USB: 기기가 Suda AI 서버에 USB로 연결됨 (현재 사용)
# - GPIO: 기기가 라즈베리파이 GPIO에 연결됨 (나중에 사용)

DEVICE_CONTROL_MODE = "USB"

# ==================== USB 포트 설정 (USB 모드 - 현재 사용) ====================
# Suda AI 서버에 연결된 USB 포트 번호
# ** 실제 연결 후 'uhubctl' 명령어로 포트 번호 확인 필요 **
# ** 명령어: uhubctl (USB 포트 목록 표시) **

USB_PORT_FAN = "1-1.2"    # UC-CP79 USB 쿨러 80mm (시스템 팬)
USB_PORT_PUMP = "1-1.3"   # 딩동펫 워터퓨어 USB 수중 펌프
USB_PORT_LED = "1-1.4"    # 루아즈 LED 네온 스트립 조명

# ==================== GPIO 핀 설정 (GPIO 모드 - 나중에 사용) ====================
# 라즈베리파이로 기기를 옮길 때 사용할 GPIO 핀 번호
# ** 주의: USB 기기를 GPIO로 제어하려면 릴레이 모듈 필요 **
# ** USB 기기는 5V 전원이므로 GPIO 3.3V로 직접 제어 불가 **

# PIN_FAN = 17    # GPIO 17번 - 팬 (릴레이 모듈로 5V 제어)
# PIN_PUMP = 27   # GPIO 27번 - 펌프 (릴레이 모듈로 5V 제어)
# PIN_LED = 22    # GPIO 22번 - LED (릴레이 모듈로 5V 제어)

# ==================== 카메라 설정 ====================
CAMERA_RESOLUTION = (640, 480)  # 해상도
CAMERA_QUALITY = 85             # JPEG 품질 (0-100)

# ==================== 로깅 설정 ====================
DEBUG = True  # 디버그 메시지 출력