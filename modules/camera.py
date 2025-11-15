"""
카메라 모듈 - USB 카메라 (APC850)

Pi Camera에서 USB 카메라로 변경됨
opencv-python 라이브러리 사용
"""

import time
import os
from datetime import datetime
from config import *

# OpenCV 초기화 (USB 카메라용)
try:
    import cv2  # OpenCV 라이브러리
    
    # USB 카메라 객체 생성
    # 0: 첫 번째 연결된 카메라 (보통 USB 카메라)
    camera = cv2.VideoCapture(0)
    
    if camera.isOpened():
        # 해상도 설정
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])   # 640
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])  # 480
        print("✓ USB 카메라 초기화 완료 (APC850)")
        print(f"  해상도: {CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]}")
    else:
        camera = None
        print("✗ USB 카메라를 찾을 수 없습니다")
        
except ImportError:
    camera = None
    print("⚠ opencv-python이 설치되지 않았습니다")
    print("  설치: pip install opencv-python")
except Exception as e:
    camera = None
    print(f"✗ 카메라 초기화 실패: {e}")

# 이미지 저장 폴더
IMAGE_DIR = "./images"  # 현재 폴더의 images 폴더

if not os.path.exists(IMAGE_DIR):  # 폴더 없으면
    os.makedirs(IMAGE_DIR)  # 폴더 생성
    print(f"✓ 이미지 저장 폴더 생성: {IMAGE_DIR}")


# ==================== 사진 촬영 ====================

def capture_image(filename=None):
    """
    USB 카메라로 사진 촬영
    
    Args:
        filename (str, optional): 저장할 파일명. 없으면 자동 생성
    
    Returns:
        str: 저장된 이미지 경로
        None: 촬영 실패 시
    
    Note:
        - OpenCV로 프레임을 읽어서 JPEG로 저장
        - CAMERA_QUALITY 설정값으로 JPEG 압축률 조정
    """
    try:
        if camera is None or not camera.isOpened():
            print("✗ 카메라가 연결되지 않았습니다")
            return None
        
        # 파일명 생성
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 예: "20251115_143052"
            filename = f"smartfarm_{timestamp}.jpg"
            # 예: "smartfarm_20251115_143052.jpg"
        
        # 전체 경로
        filepath = os.path.join(IMAGE_DIR, filename)
        
        # 카메라 워밍업 (몇 프레임 버리기)
        # USB 카메라는 첫 프레임이 어두울 수 있음
        for _ in range(5):
            camera.read()
            time.sleep(0.1)
        
        # 실제 촬영
        ret, frame = camera.read()
        
        if ret:
            # JPEG 저장 (품질 설정 적용)
            # cv2.IMWRITE_JPEG_QUALITY: 0~100 (높을수록 고품질)
            cv2.imwrite(
                filepath, 
                frame, 
                [cv2.IMWRITE_JPEG_QUALITY, CAMERA_QUALITY]
            )
            print(f"✓ 촬영 완료: {filepath}")
            return filepath
        else:
            print("✗ 프레임 읽기 실패")
            return None
        
    except Exception as e:
        print(f"✗ 촬영 오류: {e}")
        return None


def get_latest_image():
    """
    최근 촬영한 이미지 경로 반환
    
    Returns:
        str: 가장 최근 이미지 경로
        None: 이미지 없을 시
    """
    try:
        files = os.listdir(IMAGE_DIR)  # images 폴더의 모든 파일
        images = [f for f in files if f.endswith('.jpg')]  # jpg만 필터
        
        if images:
            images.sort(reverse=True)  # 최신순 정렬 (파일명에 타임스탬프 있음)
            latest_path = os.path.join(IMAGE_DIR, images[0])
            return latest_path
        
        return None
        
    except Exception as e:
        print(f"✗ 이미지 조회 오류: {e}")
        return None


def release_camera():
    """
    카메라 리소스 해제
    
    프로그램 종료 시 호출하여 카메라 연결 종료
    """
    if camera is not None:
        camera.release()
        print("✓ 카메라 리소스 해제")


# ==================== 테스트 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("=== USB 카메라 테스트 ===")
    print("=" * 60)
    print()
    
    if camera is None:
        print("카메라가 연결되지 않았습니다")
        print("다음을 확인하세요:")
        print("  1. USB 카메라가 연결되어 있는지")
        print("  2. opencv-python이 설치되어 있는지")
        print("     설치: pip install opencv-python")
    else:
        # 촬영 테스트
        print("촬영 시작...")
        img_path = capture_image()
        
        if img_path:
            print(f"✓ 이미지 저장: {img_path}")
            
            # 최신 이미지 조회 테스트
            latest = get_latest_image()
            print(f"✓ 최신 이미지: {latest}")
        else:
            print("✗ 촬영 실패")
        
        # 카메라 해제
        release_camera()
    
    print()
    print("=" * 60)