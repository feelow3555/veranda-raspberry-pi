"""
센서 모듈 패키지

스마트팜 센서들을 통합 관리합니다.
- HTU21D: 온습도 센서 (I2C)
- MCP3008: ADC 변환기 (SPI)
- LightSensor: 조도 센서 (MCP3008 사용)
- CO2Sensor: CO2 센서 (UART)
- TDSSensor: TDS/EC 센서 (MCP3008 사용)
"""

from .htu21d import HTU21DSensor
from .mcp3008 import MCP3008
from .light import LightSensor
from .co2 import CO2Sensor
from .tds import TDSSensor

# 패키지에서 import 가능한 클래스 목록
__all__ = [
    'HTU21DSensor',
    'MCP3008', 
    'LightSensor',
    'CO2Sensor',
    'TDSSensor'
]