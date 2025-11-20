import cv2
camera = cv2.VideoCapture(0, cv2.CAP_V4L)

fourcc = cv2.VideoWriter_fourcc(*'MJPG') # 💡 더 안정적인 코덱으로 변경
writer = cv2.VideoWriter("video_test.avi", fourcc, 30.0, (640, 480)) # 💡 해상도를 640x480으로 변경

while True:
    ret, image = camera.read()
    if ret == True:
        writer.write(image)
    else:
        print('카메라로부터 프레임의 캡처할 수 없습니다.')
        break

writer.release()
camera.release()