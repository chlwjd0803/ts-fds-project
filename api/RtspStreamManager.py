import subprocess
import os
import signal
import time
from typing import Optional

# 본 코드는 GEMINI가 작성하였습니다.

class RtspStreamManager:
    """
    웹캠 RTSP 스트리밍을 위한 FFmpeg 프로세스를 관리하는 클래스입니다.
    FastAPI 애플리케이션의 싱글톤으로 사용됩니다.
    """
    
    # 클래스 수준 또는 인스턴스 변수로 관리 (여기서는 인스턴스 변수)
    def __init__(self, rtsp_url: str = "rtsp://127.0.0.1:8554/live/stream"):
        self.rtsp_url = rtsp_url  # RTSP 서버의 주소 및 스트림 경로
        self.ffmpeg_process: Optional[subprocess.Popen] = None
        
        # 라즈베리파이의 기본 웹캠 장치 경로
        self.webcam_device = "/dev/video0" 
        
    def _construct_ffmpeg_command(self) -> list:
        """FFmpeg 실행 명령어를 구성합니다."""
        # V4L2 (Video4Linux2)를 사용하여 웹캠 장치에서 영상을 가져와 H.264로 인코딩하고 RTSP로 송출하는 명령입니다.
        
        command = [
            'ffmpeg', 
            '-f', 'v4l2',             # 입력 포맷: Video4Linux2
            '-i', self.webcam_device, # 입력 장치 경로
            '-c:v', 'libx264',        # 비디오 코덱: H.264
            '-pix_fmt', 'yuv420p',    # 픽셀 포맷 (호환성 향상)
            '-preset', 'veryfast',    # 인코딩 속도 (CPU 사용량과 품질 트레이드오프)
            '-tune', 'zerolatency',   # 지연 시간 최소화 설정
            '-rtsp_transport', 'tcp', # 전송 프로토콜: TCP (안정성)
            '-f', 'rtsp',             # 출력 포맷: RTSP
            self.rtsp_url             # RTSP 출력 주소
        ]
        
        return command

    def is_streaming(self) -> bool:
        """현재 FFmpeg 스트리밍 프로세스가 실행 중인지 확인합니다."""
        if self.ffmpeg_process is None:
            return False
        
        # poll() 메서드는 프로세스가 종료되면 리턴 코드를, 아니면 None을 반환합니다.
        return self.ffmpeg_process.poll() is None

    def start_stream(self) -> bool:
        """RTSP 스트리밍을 시작합니다."""
        if self.is_streaming():
            print("🚨 RTSP 스트리밍이 이미 실행 중입니다.")
            return False
        
        try:
            command = self._construct_ffmpeg_command()
            
            # Popen을 사용하여 새로운 프로세스로 FFmpeg 실행
            # stdout/stderr를 DEVNULL로 리다이렉션하여 출력을 무시하고 백그라운드에서 실행
            self.ffmpeg_process = subprocess.Popen(
                command, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid # 프로세스 그룹 ID 설정 (종료를 깔끔하게 하기 위해)
            )
            print(f"✅ FFmpeg RTSP 스트리밍 시작됨 (PID: {self.ffmpeg_process.pid})")
            return True
            
        except FileNotFoundError:
            print("❌ 오류: 'ffmpeg' 명령어를 찾을 수 없습니다. FFmpeg이 설치되어 있나요?")
            return False
        except Exception as e:
            print(f"❌ RTSP 스트리밍 시작 중 예상치 못한 오류 발생: {e}")
            return False

    def stop_stream(self) -> bool:
        """RTSP 스트리밍을 중지합니다."""
        if not self.is_streaming():
            print("🚨 RTSP 스트리밍이 이미 중지 상태입니다.")
            return False
        
        try:
            # os.setsid로 설정된 전체 프로세스 그룹에 SIGTERM을 전송하여 하위 프로세스까지 안전하게 종료 시도
            os.killpg(os.getpgid(self.ffmpeg_process.pid), signal.SIGTERM)
            
            # 프로세스 종료 대기 (최대 5초)
            self.ffmpeg_process.wait(timeout=5)
            print("✅ FFmpeg RTSP 스트리밍 프로세스가 안전하게 종료되었습니다.")
            
        except subprocess.TimeoutExpired:
            # 5초 내에 종료되지 않으면 강제 종료 (SIGKILL)
            print("⚠️ 종료 시간 초과, 강제 종료 (SIGKILL) 시도.")
            os.killpg(os.getpgid(self.ffmpeg_process.pid), signal.SIGKILL)
            self.ffmpeg_process.wait()
            
        except Exception as e:
            print(f"❌ RTSP 스트리밍 중지 중 오류 발생: {e}")
            return False
            
        finally:
            self.ffmpeg_process = None # 프로세스 객체 초기화
            return True
        
    def get_status(self) -> dict:
        """현재 스트리밍 상태 정보를 반환합니다."""
        status = self.is_streaming()
        return {
            "status": "전송중" if status else "일시중지",
            "url": self.rtsp_url,
            "pid": self.ffmpeg_process.pid if status else None
        }