# 해당 코드는 중앙서버에서 실행되는 WebSocket 클라이언트 코드 입니다.
# 테스트 시 데스크탑 또는 랩탑으로 같은 네트워크 환경임을 확인 후 연결 바랍니다.
# 서버IP와 포트는 라즈베리파이 서버의 IP와 포트로 설정해야 합니다.

import asyncio
import websockets
import cv2
import numpy as np
import base64


SERVER_IP = "192.168.0.11" 
SERVER_PORT = 8080
WEBSOCKET_URL = f"ws://{SERVER_IP}:{SERVER_PORT}/ws/stream"


async def receive_stream():
    """웹소켓을 통해 이미지 프레임을 수신하고 화면에 표시하는 클라이언트"""
    print(f"서버에 연결 시도: {WEBSOCKET_URL}")
    
    try:
        async with websockets.connect(WEBSOCKET_URL, max_size=None) as websocket:
            print("✅ WebSocket 연결 성공. 스트리밍 시작 대기중")

            cv2.namedWindow('Received Stream', cv2.WINDOW_NORMAL) # 윈도우 생성
            
            while True:
                try:
                    # 1. 서버로부터 바이너리 데이터(JPEG 프레임) 수신
                    image_data = await websocket.recv()
                    
                    # 2. 수신된 바이트 데이터를 NumPy 배열로 변환
                    nparr = np.frombuffer(image_data, np.uint8)
                    
                    # 3. OpenCV를 사용하여 JPEG 디코딩
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if frame is not None:
                        # 4. 화면에 이미지 표시
                        cv2.imshow('Received Stream', frame)
                        
                        # 5. 'q'를 누르면 종료
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    
                except websockets.exceptions.ConnectionClosedOK:
                    print("서버에 의해 연결이 정상적으로 닫혔습니다.")
                    break
                except websockets.exceptions.ConnectionClosedError as e:
                    print(f"❌ 연결 오류 발생: {e}")
                    break
                except Exception as e:
                    print(f"❌ 데이터 처리 중 오류 발생: {e}")
                    break
                    
    except ConnectionRefusedError:
        print(f"❌ 연결 거부: 서버가 {SERVER_IP}:{SERVER_PORT}에서 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        
    finally:
        cv2.destroyAllWindows()
        print("✅ 스트리밍 클라이언트 종료.")


if __name__ == "__main__":
    try:
        asyncio.run(receive_stream())
    except KeyboardInterrupt:
        print("✅ 사용자에 의해 클라이언트가 종료됩니다.")