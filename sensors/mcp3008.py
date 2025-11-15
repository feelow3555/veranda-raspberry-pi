"""
MCP3008 ADC 모듈 (SPI 통신)

MCP3008은 8채널 10비트 ADC(아날로그-디지털 변환기)입니다.
아날로그 센서(조도, EC/TDS)의 값을 디지털로 변환합니다.
SPI 통신을 사용하며, 라즈베리파이의 SPI0에 연결됩니다.
"""

try:
    import spidev  # SPI 통신 라이브러리
    SPI_AVAILABLE = True
except ImportError:
    SPI_AVAILABLE = False


class MCP3008:
    """
    MCP3008 ADC 클래스
    
    8개 채널(CH0~CH7)에서 아날로그 값을 읽어 0~1023 디지털 값으로 변환합니다.
    """
    
    def __init__(self, bus=0, device=0):
        """
        MCP3008 초기화
        
        Args:
            bus (int): SPI 버스 번호 (기본 0)
            device (int): SPI 디바이스 번호 (기본 0, CE0)
        """
        self.spi = None
        
        if SPI_AVAILABLE:
            try:
                # SPI 통신 객체 생성
                self.spi = spidev.SpiDev()
                self.spi.open(bus, device)  # SPI 버스 열기
                self.spi.max_speed_hz = 1000000  # 통신 속도 1MHz
                
                print(f"✓ MCP3008 초기화 완료 (SPI{bus}.{device})")
            except Exception as e:
                print(f"✗ MCP3008 초기화 실패: {e}")
                self.spi = None
        else:
            print("⚠ MCP3008 테스트 모드 (spidev 라이브러리 없음)")
    
    
    def read_adc(self, channel):
        """
        MCP3008의 특정 채널에서 아날로그 값 읽기
        
        Args:
            channel (int): ADC 채널 번호 (0~7)
        
        Returns:
            int: 디지털 변환 값 (0~1023)
                 - 0: 0V
                 - 1023: 기준전압(3.3V)
                 센서 없으면 512 (중간값, 테스트용)
                 오류 시 None
        """
        # 채널 범위 체크
        if not 0 <= channel <= 7:
            print(f"✗ 잘못된 채널 번호: {channel} (0~7 사용 가능)")
            return None
        
        try:
            if self.spi:
                # MCP3008 통신 프로토콜
                # [start bit, mode|channel, don't care]
                command = [1, (8 + channel) << 4, 0]
                
                # SPI 통신으로 데이터 송수신
                response = self.spi.xfer2(command)
                
                # 받은 데이터를 10비트 값으로 변환 (0~1023)
                # response[1]의 하위 2비트 + response[2]의 8비트
                adc_value = ((response[1] & 3) << 8) + response[2]
                
                return adc_value
            else:
                # 테스트 모드: 중간값 반환
                return 512
                
        except Exception as e:
            print(f"✗ ADC 읽기 오류 (CH{channel}): {e}")
            return None
    
    
    def read_voltage(self, channel, vref=3.3):
        """
        MCP3008의 특정 채널에서 전압 값 읽기
        
        Args:
            channel (int): ADC 채널 번호 (0~7)
            vref (float): 기준 전압 (기본 3.3V)
        
        Returns:
            float: 전압 값 (V), 소수점 2자리
                   오류 시 None
        """
        adc_value = self.read_adc(channel)
        
        if adc_value is not None:
            # ADC 값을 전압으로 변환
            # 전압 = (ADC값 / 1023) * 기준전압
            voltage = (adc_value / 1023.0) * vref
            return round(voltage, 2)
        
        return None
    
    
    def close(self):
        """
        SPI 통신 종료
        
        프로그램 종료 시 SPI 연결을 닫습니다.
        """
        if self.spi:
            self.spi.close()
            print("✓ MCP3008 SPI 통신 종료")


# 테스트 코드
if __name__ == "__main__":
    print("=== MCP3008 ADC 테스트 ===\n")
    
    # MCP3008 객체 생성
    adc = MCP3008(bus=0, device=0)
    
    # 전체 채널 읽기 테스트
    print("채널별 ADC 값:")
    for ch in range(8):
        value = adc.read_adc(ch)
        voltage = adc.read_voltage(ch)
        print(f"  CH{ch}: {value} (ADC) = {voltage}V")
    
    # SPI 종료
    adc.close()