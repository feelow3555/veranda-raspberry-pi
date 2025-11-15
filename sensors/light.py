"""
CDS 조도 센서 모듈 (MCP3008 ADC 사용)

CDS(광저항) 센서는 빛의 양에 따라 저항이 변하는 아날로그 센서입니다.
MCP3008 ADC를 통해 아날로그 값을 디지털로 변환하여 읽습니다.
"""

from .mcp3008 import MCP3008
from config import SPI_BUS, SPI_DEVICE, ADC_LIGHT_CHANNEL


class LightSensor:
    """
    CDS 조도 센서 클래스
    
    MCP3008 ADC의 특정 채널에서 조도 값을 읽습니다.
    """
    
    def __init__(self, channel=ADC_LIGHT_CHANNEL):
        """
        조도 센서 초기화
        
        Args:
            channel (int): MCP3008 ADC 채널 번호 (기본값: config에서 가져옴)
        """
        self.channel = channel  # ADC 채널 번호
        self.adc = MCP3008(bus=SPI_BUS, device=SPI_DEVICE)  # MCP3008 객체 생성
        
        print(f"✓ 조도 센서 초기화 완료 (CH{channel})")
    
    
    def read_raw(self):
        """
        ADC 원시 값 읽기
        
        Returns:
            int: ADC 값 (0~1023)
                 - 0: 어두움 (0V)
                 - 1023: 밝음 (3.3V)
        """
        return self.adc.read_adc(self.channel)
    
    
    def read_voltage(self):
        """
        전압 값 읽기
        
        Returns:
            float: 전압 (V), 소수점 2자리
        """
        return self.adc.read_voltage(self.channel)
    
    
    def read_lux(self):
        """
        조도 값 읽기 (Lux 단위로 변환)
        
        Returns:
            int: 조도 (lux)
                 - 0~1000 lux 범위로 변환
                 - 실제 센서 특성에 따라 보정 필요
        
        Note:
            현재는 간단한 선형 변환 사용
            정확한 측정이 필요하면 센서 캘리브레이션 필요
        """
        raw_value = self.read_raw()
        
        if raw_value is not None:
            # 간단한 선형 변환: 0~1023 → 0~1000 lux
            # TODO: 실제 센서 특성에 맞게 변환식 조정
            lux = int((raw_value / 1023.0) * 1000)
            return lux
        
        return None
    
    
    def read_percentage(self):
        """
        조도를 백분율로 읽기
        
        Returns:
            int: 조도 백분율 (0~100%)
                 - 0%: 완전 어두움
                 - 100%: 최대 밝기
        """
        raw_value = self.read_raw()
        
        if raw_value is not None:
            # 백분율 변환: 0~1023 → 0~100%
            percentage = int((raw_value / 1023.0) * 100)
            return percentage
        
        return None
    
    
    def close(self):
        """
        센서 종료
        
        MCP3008 SPI 통신을 닫습니다.
        """
        self.adc.close()


# 테스트 코드
if __name__ == "__main__":
    print("=== 조도 센서 테스트 ===\n")
    
    # 조도 센서 객체 생성
    sensor = LightSensor()
    
    # 다양한 방식으로 읽기
    print(f"ADC 원시값: {sensor.read_raw()}")
    print(f"전압: {sensor.read_voltage()}V")
    print(f"조도: {sensor.read_lux()} lux")
    print(f"백분율: {sensor.read_percentage()}%")
    
    # 센서 종료
    sensor.close()