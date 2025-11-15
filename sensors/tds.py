"""
TDS/EC 센서 모듈 (MCP3008 ADC 사용)

Analog TDS Sensor V1.0은 물의 전기전도도(EC)와 총용존고형물(TDS)을 측정하는 아날로그 센서입니다.
MCP3008 ADC를 통해 아날로그 값을 디지털로 변환하여 읽습니다.
"""

from .mcp3008 import MCP3008
from config import SPI_BUS, SPI_DEVICE, ADC_TDS_CHANNEL


class TDSSensor:
    """
    TDS/EC 센서 클래스
    
    MCP3008 ADC의 특정 채널에서 TDS/EC 값을 읽습니다.
    """
    
    # 센서 보정 상수
    VREF = 3.3  # 기준 전압 (V)
    KVALUE = 1.0  # TDS 보정 계수 (실측값에 따라 조정 필요)
    
    def __init__(self, channel=ADC_TDS_CHANNEL):
        """
        TDS 센서 초기화
        
        Args:
            channel (int): MCP3008 ADC 채널 번호 (기본값: config에서 가져옴)
        """
        self.channel = channel  # ADC 채널 번호
        self.adc = MCP3008(bus=SPI_BUS, device=SPI_DEVICE)  # MCP3008 객체 생성
        
        print(f"✓ TDS 센서 초기화 완료 (CH{channel})")
    
    
    def read_raw(self):
        """
        ADC 원시 값 읽기
        
        Returns:
            int: ADC 값 (0~1023)
        """
        return self.adc.read_adc(self.channel)
    
    
    def read_voltage(self):
        """
        전압 값 읽기
        
        Returns:
            float: 전압 (V), 소수점 3자리
        """
        voltage = self.adc.read_voltage(self.channel, vref=self.VREF)
        if voltage is not None:
            return round(voltage, 3)
        return None
    
    
    def read_tds(self, temperature=25.0):
        """
        TDS 값 읽기 (총용존고형물)
        
        Args:
            temperature (float): 물 온도 (°C), 온도 보정용
        
        Returns:
            float: TDS 값 (ppm), 소수점 1자리
                   오류 시 None
        
        Note:
            TDS 변환 공식 (Gravity TDS Sensor 기준):
            1. 전압 읽기
            2. 온도 보정 계수 계산
            3. TDS = (133.42 * 전압^3 - 255.86 * 전압^2 + 857.39 * 전압) * 0.5 * K값
            
            TODO: 실제 센서로 캘리브레이션 필요
        """
        voltage = self.read_voltage()
        
        if voltage is None:
            return None
        
        try:
            # 온도 보정 계수 (25°C 기준)
            temp_coefficient = 1.0 + 0.02 * (temperature - 25.0)
            
            # 전압을 보정된 전압으로 변환
            compensated_voltage = voltage / temp_coefficient
            
            # TDS 계산 (3차 다항식 근사)
            # 출처: DFRobot Gravity TDS Sensor 공식
            tds_value = (133.42 * compensated_voltage**3 
                        - 255.86 * compensated_voltage**2 
                        + 857.39 * compensated_voltage) * 0.5
            
            # K값으로 보정
            tds_value *= self.KVALUE
            
            # 음수 방지
            if tds_value < 0:
                tds_value = 0
            
            return round(tds_value, 1)
            
        except Exception as e:
            print(f"✗ TDS 계산 오류: {e}")
            return None
    
    
    def read_ec(self, temperature=25.0):
        """
        EC 값 읽기 (전기전도도)
        
        Args:
            temperature (float): 물 온도 (°C), 온도 보정용
        
        Returns:
            float: EC 값 (mS/cm), 소수점 2자리
                   오류 시 None
        
        Note:
            EC와 TDS 관계: TDS (ppm) ≈ EC (mS/cm) * 500
            따라서: EC = TDS / 500
        """
        tds = self.read_tds(temperature)
        
        if tds is not None:
            # TDS를 EC로 변환
            ec = tds / 500.0
            return round(ec, 2)
        
        return None
    
    
    def set_kvalue(self, kvalue):
        """
        TDS 보정 계수 설정
        
        Args:
            kvalue (float): 보정 계수
                           - 표준 용액으로 측정하여 조정
                           - K = 실제값 / 측정값
        """
        self.KVALUE = kvalue
        print(f"✓ TDS K값 설정: {kvalue}")
    
    
    def close(self):
        """
        센서 종료
        
        MCP3008 SPI 통신을 닫습니다.
        """
        self.adc.close()


# 테스트 코드
if __name__ == "__main__":
    print("=== TDS/EC 센서 테스트 ===\n")
    
    # TDS 센서 객체 생성
    sensor = TDSSensor()
    
    # 다양한 방식으로 읽기
    print(f"ADC 원시값: {sensor.read_raw()}")
    print(f"전압: {sensor.read_voltage()}V")
    print(f"TDS: {sensor.read_tds()} ppm")
    print(f"EC: {sensor.read_ec()} mS/cm")
    
    # 온도 보정 테스트
    print(f"\nTDS (20°C): {sensor.read_tds(temperature=20.0)} ppm")
    print(f"TDS (25°C): {sensor.read_tds(temperature=25.0)} ppm")
    print(f"TDS (30°C): {sensor.read_tds(temperature=30.0)} ppm")
    
    # 센서 종료
    sensor.close()