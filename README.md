# 🚀 낙상 감지 시스템 Raspberry Pi 서버 프로젝트

## 💡 프로젝트 개요 (Project Overview)
본 프로젝트는 **라즈베리파이(Raspberry Pi)**를 엣지 디바이스로 활용하여 연결된 웹캠의 실시간 영상 스트림을 중앙 서버로 전송하는 시스템을 구현합니다. **FastAPI**를 기반으로 구축되어, 안정적인 **WebSocket** 기반의 고속 프레임 송신 채널과 서버 기능을 제어하기 위한 **REST API** 엔드포인트를 제공합니다.

---

## ✨ 주요 기능 (Key Features)

| 분류 | 기능 설명 | 관련 파일 |
| :--- | :--- | :--- |
| **웹소켓 실시간 스트리밍** | **OpenCV**를 사용하여 웹캠 프레임을 **JPEG**로 인코딩한 후, **WebSocket**을 통해 중앙 서버로 실시간 전송합니다. | `Api_Websocket.py`, `WebsocketClient.py` |
| **제어 API** | 카메라와 스트리밍에 대한 제어와 관련하여 Fast API를 구현하였습니다. | `Api_Websocket.py`, `Api_Rtsp` |
| **RTSP 실시간 스트리밍** | RTSP 프로토콜을 통한 실시간 스트리밍 모듈을 분리하여 구현하였습니다. | `Api_Rtsp` |

---

## 🛠️ 기술 스택 (Tech Stack)

* **언어:** Python
* **프레임워크:** FastAPI
* **영상 처리:** OpenCV
* **서버:** uvicorn (ASGI 서버)
* **데이터전송:** Websockets, RTSP

---

## 🗓️ 진행 현황 (Development Log)

### **[11월 24일]** 서버 API 및 클라이언트 구현

* **RTSP 전송 모듈 구현**
* **FastAPI 엣지 서버 API 구현 완료**:
    * `POST /api/frame/start`: 프레임 전송 시작/재개 기능 구현.
    * `POST /api/frame/stop`: 프레임 전송 일시 중지 기능 구현.
    * `POST /api/frame/rate/{new_rate}`: 프레임 전송 속도 동적 변경 기능 구현.
    * `GET /ws/stream`: WebSocket을 통한 실시간 영상 송신 엔드포인트 구현.
* **WebSocket 클라이언트 모듈 구현** (중앙 서버 측 모의 코드).

### **[11월 20일]** 웹캠 연속 촬영 기능 개발
* OpenCV를 활용한 웹캠 프레임 단위 연속 촬영 및 파일 저장 기능 구현.

### **[11월 19일]** 라즈베리파이 환경 설정
* 라즈베리파이 기본 세팅 및 명령어 저장.
* VS Code 원격 연결 및 웹캠 연결 확인 완료.

---

## 💻 주요 명령어 (Key Commands)

| 명령어 | 설명 |
| :--- | :--- |
| `python -m venv myenv` | Python 가상 환경 생성 |
| `source myenv/bin/activate` | 가상 환경 실행 |
| `deactiavate` | 가상 환경 종료 |
| `lsusb` | USB 포트에 연결된 기기 목록 확인 |
| `fswebcam image.jpg` | 웹캠으로 사진 촬영 명령어 (테스트용) |
| `sudo shutdown now` | 라즈베리파이 즉시 종료 |
| `mediamtx mediamtx.yml` | RTSP 서버를 열기위한 필수 실행 명령어 |

---

## ⚙️ 서버 실행 (Server Execution)

```bash
# ApiServer.py 실행 (Uvicorn 사용)
uvicorn ApiServer:app --host 0.0.0.0 --port 8080
```


## RTSP 필수 세팅 과정
```
sudo apt update
sudo apt install ffmpeg

# MediaMTX 최신 버전 다운로드 (ARMv7 아키텍처용)
# 주소는 최신 버전에 따라 달라질 수 있으므로, 공식 GitHub 페이지에서 확인하거나 아래 명령어를 사용해 보세요.
wget https://github.com/bluenviron/mediamtx/releases/download/v1.7.0/mediamtx_v1.7.0_linux_armv7.tar.gz

# 압축 해제
tar -zxvf mediamtx_v1.7.0_linux_armv7.tar.gz

# 압축 해제 후 생성된 실행 파일을 원하는 디렉토리로 이동 (예: /usr/local/bin)
sudo mv mediamtx /usr/local/bin/

# mediamtx.yml 첨부되어있는 것처럼 수정
# 이후 실행

mediamtx mediamtx.yml
```