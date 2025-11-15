"""
HTU21D 온습도 센서 모듈 (I2C 통신)

HTU21D는 온도와 습도를 측정하는 디지털 센서입니다.
I2C 통신을 사용하며, 라즈베리파이의 GPIO 2(SDA), GPIO 3(SCL)에 연결됩니다.
"""

# 라이브러리 import 시도
try:
    from adafruit_htu21d import HTU21D  # HTU21D 센서 제어 라이브러리
    import board  # 라즈베리파이 GPIO 핀 정의
    import busio  # I2C 통신 라이브러리
    I2C_AVAILABLE = True  # I2C 사용 가능 플래그
except ImportError:
    # 라이브러리 없으면 테스트 모드로 동작
    I2C_AVAILABLE = False


class HTU21DSensor:
    """
    HTU21D 온습도 센서 클래스
    
    I2C 통신으로 온도와 습도를 읽어옵니다.
    센서가 없으면 테스트용 더미 데이터를 반환합니다.
    """
    
    def __init__(self):
        """
        센서 초기화
        
        I2C 통신을 설정하고 HTU21D 센서 객체를 생성합니다.
        초기화 실패 시 테스트 모드로 동작합니다.
        """
        self.sensor = None  # 센서 객체 초기화
        
        if I2C_AVAILABLE:
            try:
                # I2C 통신 객체 생성 (SCL=GPIO3, SDA=GPIO2)
                i2c = busio.I2C(board.SCL, board.SDA)
                
                # HTU21D 센서 객체 생성
                self.sensor = HTU21D(i2c)
                
                print("✓ HTU21D 초기화 완료")
            except Exception as e:
                print(f"✗ HTU21D 초기화 실패: {e}")
                self.sensor = None
        else:
            print("⚠ HTU21D 테스트 모드 (라이브러리 없음)")
    
    
    def read_temperature(self):
        """
        온도 읽기
        
        Returns:
            float: 섭씨 온도 (°C), 소수점 1자리
                   센서 없으면 25.0 (테스트용)
                   오류 시 None
        """
        try:
            if self.sensor:
                # 센서에서 온도 읽기
                temp = float(self.sensor.temperature)
                return round(temp, 1)  # 소수점 1자리 반올림
            else:
                # 테스트 모드: 더미 데이터 반환
                return 25.0
                
        except Exception as e:
            print(f"✗ 온도 읽기 오류: {e}")
            return None
    
    
    def read_humidity(self):
        """
        습도 읽기
        
        Returns:
            float: 상대습도 (%), 소수점 1자리
                   센서 없으면 60.0 (테스트용)
                   오류 시 None
        """
        try:
            if self.sensor:
                # 센서에서 습도 읽기
                humidity = float(self.sensor.relative_humidity)
                return round(humidity, 1)  # 소수점 1자리 반올림
            else:
                # 테스트 모드: 더미 데이터 반환
                return 60.0
                
        except Exception as e:
            print(f"✗ 습도 읽기 오류: {e}")
            return None
    
    
    def read_all(self):
        """
        온도와 습도를 한 번에 읽기
        
        Returns:
            dict: {
                'temperature': float,  # 온도 (°C)
                'humidity': float      # 습도 (%)
            }
        """
        return {
            'temperature': self.read_temperature(),
            'humidity': self.read_humidity()
        }


# 테스트 코드 (이 파일을 직접 실행했을 때만 동작)
if __name__ == "__main__":
    print("=== HTU21D 센서 테스트 ===\n")
    
    # 센서 객체 생성
    sensor = HTU21DSensor()
    
    # 개별 읽기 테스트
    print(f"온도: {sensor.read_temperature()}°C")
    print(f"습도: {sensor.read_humidity()}%")
    
    # 전체 읽기 테스트
    print("\n전체 데이터:")
    print(sensor.read_all())