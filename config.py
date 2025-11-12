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

# ==================== HTU21D 온습도 센서 (I2C 통신 - 고정 핀) ====================
I2C_SDA = 2   # GPIO 2번 핀
I2C_SCL = 3   # GPIO 3번 핀

# ==================== MCP3202 조도 센서 (SPI 통신 - 고정 핀) ====================
SPI_CLK = 11   # GPIO 11번
SPI_MISO = 9   # GPIO 9번
SPI_MOSI = 10  # GPIO 10번
SPI_CS = 8     # GPIO 8번

# ==================== CO2 센서 (아날로그 - MCP3008 ADC 사용) ====================
ADC_CO2_CHANNEL = 0   # MCP3008의 0번 채널

# ==================== EC 센서 (아날로그 - MCP3008 ADC 사용) ====================
ADC_EC_CHANNEL = 1    # MCP3008의 1번 채널

# ==================== GPIO 핀 설정 (기기 제어 - 자유롭게 변경 가능) ====================
PIN_PUMP = 17   # GPIO 17번 - 물 펌프
PIN_LED = 27    # GPIO 27번 - LED
PIN_FAN = 22    # GPIO 22번 - 팬

# ==================== 카메라 설정 ====================
CAMERA_RESOLUTION = (640, 480)  # 해상도
CAMERA_QUALITY = 85             # JPEG 품질 (0-100)

# ==================== 로깅 설정 ====================
DEBUG = True  # 디버그 메시지 출력