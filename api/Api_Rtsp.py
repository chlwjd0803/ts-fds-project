from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import uvicorn

# HTTP 응답 모델 (기존 코드에서 사용됨)
from HttpResponseJson import HttpResponseJson 

# 새로 작성한 RTSP 스트림 관리 모듈 임포트
from RtspStreamManager import RtspStreamManager 

app = FastAPI()

# **RTSP 관리자 객체 싱글톤**
RTSP_MANAGER = RtspStreamManager(rtsp_url="rtsp://127.0.0.1:8554/live/stream")


@app.post("/api/rtsp/start") 
async def start_rtsp_transmission():
    """FFmpeg을 사용하여 RTSP 스트리밍을 시작합니다."""
    if RTSP_MANAGER.start_stream():
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=HttpResponseJson(
                status=200, 
                message=f"RTSP 스트리밍이 시작되었습니다. URL: rtsp://<요청주소>:8554/live/stream"
            ).model_dump()
        )
    else :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=HttpResponseJson(
                status=400, 
                message="RTSP 스트리밍이 이미 실행 중이거나 시작에 실패했습니다."
            ).model_dump()
        )

@app.post("/api/rtsp/stop") 
async def stop_rtsp_transmission():
    """실행 중인 FFmpeg RTSP 스트리밍을 중지합니다."""
    if RTSP_MANAGER.stop_stream():
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=HttpResponseJson(
                status=200, 
                message="RTSP 스트리밍이 성공적으로 중지되었습니다."
            ).model_dump()
        )
    else : 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=HttpResponseJson(
                status=400, 
                message="RTSP 스트리밍이 이미 중지된 상태입니다."
            ).model_dump()
        )
        
@app.get("/api/rtsp/status") 
async def get_rtsp_status():
    """RTSP 스트리밍 상태 정보를 조회합니다."""
    rtsp_info = RTSP_MANAGER.get_status()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=HttpResponseJson(
            status=200,
            message=f"현재 RTSP 스트리밍 상태: {rtsp_info['status']}",
            data=rtsp_info
        ).model_dump()
    )



if __name__ == "__main__":
    # 서버 실행 명령어: uvicorn ai_server:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8080)