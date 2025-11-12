"""
스마트팜 설정 파일
"""

# 스프링 부트 서버 설정
SPRING_BOOT_URL = "ws://localhost:8080/smartfarm"  # 백엔드 팀한테 받아서 수정

# 센서 읽기 주기 (초)
SENSOR_INTERVAL = 5

# HTU21D 온습도 센서 (I2C 통신) - 고정
I2C_SDA = 2   # GPIO 2번 핀
I2C_SCL = 3   # GPIO 3번 핀

# MCP3202 조도 센서 (SPI 통신) - 고정
SPI_CLK = 11   # GPIO 11번
SPI_MISO = 9   # GPIO 9번
SPI_MOSI = 10  # GPIO 10번
SPI_CS = 8     # GPIO 8번

# CO2 센서 (아날로그 - 일반적으로 MCP3008 ADC 사용)
ADC_CO2_CHANNEL = 0   # MCP3008의 0번 채널

# EC 센서 (아날로그 - MCP3008 ADC 사용)
ADC_EC_CHANNEL = 1    # MCP3008의 1번 채널

# GPIO 핀 설정 (기기 제어 - 릴레이)
PIN_PUMP = 17   # GPIO 17번 - 물 펌프
PIN_LED = 27    # GPIO 27번 - LED
PIN_FAN = 22    # GPIO 22번 - 팬

# 카메라 설정
CAMERA_RESOLUTION = (640, 480)  # 해상도