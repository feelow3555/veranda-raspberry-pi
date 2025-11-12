"""
카메라 모듈 - Pi Camera Rev 1.3
"""
import time
import os
from datetime import datetime
from config import *

# PiCamera 초기화 (라즈베리파이 4B에서는 picamera2)
try:
    from picamera2 import Picamera2 # 라즈베리파이 4B용 카메라 라이브러리
    
    camera = Picamera2()
    config = camera.create_still_configuration(
        main={"size": CAMERA_RESOLUTION} # 해상도 설정 (640x480 등)
    )
    camera.configure(config)
    print("Pi Camera 초기화 완료")
except Exception as e:
    camera = None
    print(f"! 카메라 초기화 실패: {e}")

# 이미지 저장 폴더
IMAGE_DIR = "./images" # 현재 폴더의 images 폴더
if not os.path.exists(IMAGE_DIR): # 폴더 없으면
    os.makedirs(IMAGE_DIR) # 폴더 생성


# ==================== 사진 촬영 ====================

def capture_image(filename=None):
    """
    사진 촬영 (PDF 예제 4-1 기반)
    """
    try:
        if camera is None:
            return None
        
        # 파일명 생성
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 예: "20251109_143052"
            filename = f"smartfarm_{timestamp}.jpg"
            # 예: "smartfarm_20251109_143052.jpg"
        
        # 전체 경로
        filepath = os.path.join(IMAGE_DIR, filename)
        
        # 촬영
        camera.start()
        time.sleep(2)  # 2초 대기 (PDF: warm-up time) -> 카메라가 초점, 밝기 자동 조절하는 시간
        camera.capture_file(filepath) # 사진 찍어서 파일 저장
        camera.stop() # 카메라 종료
        
        print(f"촬영 완료: {filepath}")
        return filepath # 파일 경로 반환
        
    except Exception as e:
        print(f"촬영 오류: {e}")
        return None


def get_latest_image():
    """최근 촬영한 이미지 경로"""
    try:
        files = os.listdir(IMAGE_DIR) # images 폴더의 모든 파일
        images = [f for f in files if f.endswith('.jpg')] # jpg만 필터

        if images:
            images.sort(reverse=True) # 최신순 정렬
            return os.path.join(IMAGE_DIR, images[0]) # 첫번째 (최신)
        
        return None
    except:
        return None
    

# ==================== 테스트 ====================

if __name__ == "__main__":
    print("=== 카메라 테스트 ===")
    
    # 촬영
    img_path = capture_image()
    
    if img_path:
        print(f"이미지 저장: {img_path}")
    else:
        print("촬영 실패")