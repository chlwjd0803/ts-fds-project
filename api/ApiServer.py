from fastapi import FastAPI, WebSocket, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn
import cv2
import numpy as np
import asyncio

from HttpResponseJson import HttpResponseJson

app = FastAPI()

# 0. 관리 전역변수
is_streaming = True  # 웹캠 스트리밍 상태 플래그


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
                message="웹캠이 정상적으로 연결되었으며 접근 가능합니다. 웹캠 스트리밍 상태 : " + ("전송중" if is_streaming else "일시중지")
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
    
# **새로운 제어 API:** 프레임 전송 시작 or 재개
@app.post("/api/frame/start")
async def start_frame_transmission():
    global is_streaming
    if not is_streaming:
        is_streaming = True
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=HttpResponseJson(
                status=200, 
                message="프레임 전송이 재개되었습니다. 현재 상태 : " + ("전송중" if is_streaming else "일시중지")
            ).model_dump()
        )
    else :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=HttpResponseJson(
                status=200, 
                message="프레임 전송이 이미 실행 중입니다. 현재 상태 : " + ("전송중" if is_streaming else "일시중지")
            ).model_dump()
        )

# **새로운 제어 API:** 프레임 전송 일시 중지
@app.post("/api/frame/stop")
async def stop_frame_transmission():
    global is_streaming
    if is_streaming:
        is_streaming = False
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=HttpResponseJson(
                status=200, 
                message="프레임 전송이 일시 중지되었습니다. 현재 상태 : " + ("전송중" if is_streaming else "일시중지")
            ).model_dump()
        )
    else : 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=HttpResponseJson(
                status=200, 
                message="프레임 전송이 이미 중지된 상태입니다. 현재 상태 : " + ("전송중" if is_streaming else "일시중지")
            ).model_dump()
        )


# 2. 웹소켓 엔드포인트 구현 (실시간 영상 수신)
# 해당 부분은 일단 구현 상 보류합니다.

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    RPi 서버 -> 중앙 서버로 WebSocket 실시간 영상 프레임을 송신합니다.
    """
    global is_streaming
    
    # 웹소켓 연결 수락 (중앙 서버와의 연결)
    await websocket.accept()
    print(f"\n✅ 중앙 서버의 웹소켓 연결 수락: {websocket.client}")
    
    # 웹캠 캡처 객체 생성
    cap = cv2.VideoCapture(0) 
    
    # 웹캠 연결 확인
    if not cap.isOpened():
        print("웹캠 연결을 찾을 수 없습니다. WebSocket 연결을 종료합니다.")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Webcam not available")
        return

    try:
        while True:
            # 1. REST API로 제어된 전송 상태 확인
            if is_streaming:
                # 2. 웹캠에서 프레임 읽기
                ret, frame = cap.read()
                
                if ret:
                    # 3. 프레임을 JPEG로 인코딩 (바이트 데이터 준비)
                    # 품질을 50으로 설정하여 대역폭을 절약합니다. (0~100)
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                    ret, buffer = cv2.imencode('.jpg', frame, encode_param)
                    image_data = buffer.tobytes()
                    
                    # 4. 중앙 서버로 데이터 "송신"
                    await websocket.send_bytes(image_data)

                else:
                    pass
            
            # 전송 속도 조절: 24fps 세팅
            await asyncio.sleep(0.041666) 
            
    except Exception as e:
        # 웹소켓 연결 단절, 예외 처리
        print(f"\n❌ 웹소켓 연결 종료/오류 발생: {websocket.client} - {e}")
        
    finally:
        # 웹캠 객체 해제 및 웹소켓 연결 종료
        cap.release()
        await websocket.close()
        print(f"연결 종료 및 웹캠 해제 완료: {websocket.client}")


if __name__ == "__main__":
    # 서버 실행 명령어: uvicorn ai_server:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8080)