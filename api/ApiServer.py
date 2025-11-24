from fastapi import FastAPI, WebSocket, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import cv2
import numpy as np

from HttpResponseJson import HttpResponseJson

app = FastAPI()

# 1. REST API 엔드포인트 구현 (기본 정보 및 엣지 명령 전송 모의)


# 테스트
@app.get("/", response_class=HTMLResponse)
async def get_status():
    """서버 상태 확인용 기본 페이지"""
    return """
    <html>
        <head>
            <title>AI Server Status</title>
        </head>
        <body>
            <h1>라즈베리 서버가 정상적으로 작동 중입니다.</h1>
            <p>WebSocket: ws://localhost:8000/ws/stream</p>
            <p>REST API: http://localhost:8000/api/status</p>
        </body>
    </html>
    """


# 라즈베리 서버 확인 API
@app.get("/api/server_status")
async def get_api_status():
    """
    서버 API 상태 정보 제공

    라즈베리파이 서버가 정상적으로 동작하는지에 대해 보여줍니다.
    
    """
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=HttpResponseJson(
                status=200, 
                message="라즈베리 서버 준비완료"
            ).model_dump()
        )

# 라즈베리에 연결된 웹캠 상태 확인 API
@app.get("/api/webcam_status")
async def get_webcam_status():
    
    """
    서버 외부장치(웹캠) 상태 정보 제공

    라즈베리파이에 연결되어있는 웹캠 장치가 정상적으로 연결되어있는지 확인합니다.
    
    """
    cap = cv2.VideoCapture(0) 
    
    # **웹캠이 성공적으로 열렸는지 확인**
    if cap.isOpened():
        # 웹캠이 연결되어있음
        cap.release()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=HttpResponseJson(
                status=200, 
                message="웹캠이 정상적으로 연결되었으며 접근 가능합니다."
            ).model_dump()
        )
        
    else:
        # 웹캠이 연결되어있지않음
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=HttpResponseJson(
                status=500, # 응답 본문에 포함될 내부 상태 코드
                message="웹캠 연결을 찾을 수 없거나 접근할 수 없습니다 (인덱스 0)."
            ).model_dump()
        )

# 중앙(AI)서버 측에서 요청을 보내야할 API -> 중앙서버와 라즈베리서버의 역할이 분리됨
# @app.post("/api/command")
# async def send_control_command(command: SpeakerCommand):
#     """
#     엣지 컴퓨터 명령 전송(REST API) 모의. 
#     AI 분석 결과를 스피커 제어용 명령으로 변환 후 엣지로 전송합니다. 
#     """
#     print(f"--- IOT 제어 명령 수신 ---")
#     print(f"수신된 명령: {command}")
    
#     # 실제 구현: MQTT Publish 로직 또는 다른 로직 수행
#     # 현재는 모의 구현으로 단순 받았던 JSON을 그대로 반환합니다.
    
#     return {"result": "success", "command_sent": command}



# 2. 웹소켓 엔드포인트 구현 (실시간 영상 수신)
# 해당 부분은 일단 구현 상 보류합니다.

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):

    """
    중앙서버(AI서버)와의 WebSocket 실시간 영상 스트리밍 송수신

    중앙서버로 웹캠으로 촬영한 영상을 프레임단위로 잘라 전송합니다.

    1. 연결 수립: 클라이언트(엣지 컴퓨터)에서 WebSocket 연결 요청 시 인증 및 연결 승인 처리
    2. 영상 송신: 웹캠에서 캡처한 프레임을 JPEG로 인코딩하여 WebSocket을 통해 중앙서버로 전송
    
    """
    
    # 연결 인증 및 식별 모의: 연결 수립 시 인증 토큰 검증 로직 추가 가능
    await websocket.accept()
    
    # 웹캠 연결상태 관리: 연결 승인
    print(f"\n✅ 새로운 웹캠 연결 수립: {websocket.client}")
    
    try:
        while True:
            # 웹캠 영상정보 수신: 클라이언트로부터 이진 데이터(JPEG) 수신
            image_data = await websocket.receive_bytes()
            
            # 💡 서버 CPU 부하 지점: JPEG 디코딩 및 AI 분석
            
            # 바이트 데이터를 NumPy 배열로 변환
            nparr = np.frombuffer(image_data, np.uint8)
            # JPEG 디코딩
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                # 영상 데이터 수신(websocket) 
                print(f"프레임 수신 성공. 크기: {len(image_data) / 1024:.2f} KB, 해상도: {frame.shape[1]}x{frame.shape[0]}")
                
                # 💡 YOLO 객체 탐지 및 CLIP 상황 분석 로직 추가 위치 
                # analyze_result = yolo_model.predict(frame)
                # ...
                
            else:
                print("오류: 수신된 데이터를 프레임으로 디코딩할 수 없습니다.")

    except Exception as e:
        # 웹캠 연결상태 관리: 비정상적 단절 시 예외 처리 및 세션 정리 [cite: 1, 2]
        print(f"\n❌ 웹캠 연결 종료/오류 발생: {websocket.client} - {e}")
        
    finally:
        # 연결 종료 처리
        await websocket.close()
        print(f"연결 종료 처리 완료: {websocket.client}")


if __name__ == "__main__":
    # 서버 실행 명령어: uvicorn ai_server:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8080)