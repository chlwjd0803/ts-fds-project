# 강제종료를 하지 않으면 무한히 프레임을 저장하는 스크립트

import cv2
import time
import os
import sys

# --- 환경 설정 ---
CAMERA_INDEX = 0      # 보통 0번 카메라
OUTPUT_DIR = "captured_frames222"  # 프레임을 저장할 폴더 이름
# -----------------

def capture_and_save_frames():
    """웹캠에서 연속적인 프레임을 캡처하고 이미지 파일로 저장하는 함수"""
    
    # 1. 저장 폴더 생성
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"저장 폴더 생성: {OUTPUT_DIR}")

    # 2. 웹캠 초기화 
    # cv2.CAP_V4L: Linux 환경에서 V4L2 백엔드를 사용하도록 명시 (test.py 참고)
    camera = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L) 
    
    if not camera.isOpened():
        print(f"오류: {CAMERA_INDEX}번 웹캠을 열 수 없습니다.")
        # sys.exit(1)
        return # 함수 종료

    print("웹캠 초기화 완료. 프레임 캡처를 시작합니다. (q 키를 누르면 종료)")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            # 3. 프레임 캡처
            ret, image = camera.read()
            
            if not ret:
                print('카메라로부터 프레임을 캡처할 수 없습니다.')
                break
            
            current_time = time.time()
            
            # 4. 파일 이름 설정 (시간 기반으로 고유한 이름 생성)
            timestamp_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(current_time))
            # 밀리초 추가 (정확도 향상)
            milliseconds = int((current_time - int(current_time)) * 1000)
            filename = f"{OUTPUT_DIR}/{timestamp_str}_{milliseconds:03d}.jpg"
            
            # 5. 프레임을 JPEG 파일로 저장
            cv2.imwrite(filename, image)
            
            frame_count += 1
            
            # 초당 10프레임 전송을 모의하기 위해 sleep 시간을 조정합니다.
            # 1초 / 10프레임 = 0.1초 (전송 시간 고려)
            time.sleep(0.05) 
                
    except Exception as e:
        print(f"처리 중 예외 발생: {e}")
        
    finally:
        # 7. 자원 해제
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n자원 해제 및 종료 처리 중...")
        camera.release()
        
        if duration > 0:
            avg_fps = frame_count / duration
            print(f"총 {frame_count}개 프레임 저장됨. 평균 FPS: {avg_fps:.2f}")


if __name__ == "__main__":
    capture_and_save_frames()