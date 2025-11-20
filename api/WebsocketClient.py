import asyncio
import websockets
import cv2
import numpy as np
import time

# --- 설정 정보 ---
# 중앙 서버의 WebSocket 주소로 변경해야 합니다.
NVR_SERVER_URL = "ws://localhost:8000/ws/stream" 
# 카메라 고유 ID (IF-003 명세에 따라 전송해야 함)
CAMERA_ID = "CAM-RASPBERRY-01" 
# 캡처 인덱스 (0으로 가정)
WEBCAM_INDEX = 0 

async def send_frames_to_nvr():
    """웹캠 프레임을 캡처하여 중앙 서버로 WebSocket을 통해 전송합니다."""
    
    # 1. 웹캠 캡처기 초기화
    cap = cv2.VideoCapture(WEBCAM_INDEX)
    if not cap.isOpened():
        print(f"❌ 오류: 웹캠 장치(인덱스 {WEBCAM_INDEX})를 열 수 없습니다.")
        return

    print("✅ 웹캠 연결 성공. 프레임 전송을 시작합니다...")

    try:
        # 2. 중앙서버에 WebSocket 연결 시도
        async with websockets.connect(NVR_SERVER_URL) as websocket:
            print(f"🎉 서버에 WebSocket 연결 성공: {NVR_SERVER_URL}")

            while True:
                # 3. 프레임 캡처
                ret, frame = cap.read()
                if not ret:
                    print("⚠️ 경고: 프레임을 읽을 수 없습니다. (웹캠 연결 끊김?)")
                    await asyncio.sleep(1)
                    continue

                # 4. 이미지 인코딩 (JPEG로 압축하여 전송량을 줄임)
                # 프레임 품질을 높이려면 [cv2.IMWRITE_JPEG_QUALITY, 90] 등 조절
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50] 
                ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                if not ret:
                    print("❌ 오류: 프레임 인코딩 실패.")
                    continue
                
                # NumPy 배열을 바이트 데이터로 변환 (전송 준비)
                image_bytes = buffer.tobytes()

                # **메타데이터 추가 (IF-003에 맞게)**
                # WebSocket은 파일 외에 메타데이터를 함께 보내기 어려우므로, 
                # 여기서는 이미지 파일 자체만 보내고, 메타데이터는 연결 시 또는 서버에서 처리합니다.
                # *[대안: 메타데이터를 JSON으로 전송 후, 이진 데이터(프레임)를 분리 전송하는 2-step 방식 사용 가능]*

                # 5. 프레임 전송
                await websocket.send(image_bytes)
                print(f"➡️ 프레임 전송 완료. 크기: {len(image_bytes) / 1024:.2f} KB")

                # 서버의 응답을 기다릴 필요가 없다면 (단방향 통신), 이 부분은 생략 가능
                # response = await websocket.recv()
                # print(f"⬅️ 서버 응답: {response}") 

                # 6. 전송 주기 제어 (프레임 레이트 조절)
                # 실시간 전송을 위해 빠르게 반복하거나, sleep으로 주기 제어
                await asyncio.sleep(0.05) # 약 17프레임 평균으로 전송

    except websockets.exceptions.ConnectionClosedOK:
        print("✅ 서버와의 WebSocket 연결이 정상적으로 종료되었습니다.")
    except Exception as e:
        print(f"❌ 연결 중 오류 발생: {e}")
    finally:
        # 7. 종료 시 웹캠 해제
        cap.release()
        print("웹캠 장치 해제 완료.")


if __name__ == "__main__":
    # 비동기 이벤트 루프 실행
    try:
        asyncio.run(send_frames_to_nvr())
    except KeyboardInterrupt:
        print("\n프로그램 종료.")