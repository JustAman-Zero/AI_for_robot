import cv2
import numpy as np
import requests
import time
import threading

# ESP32-CAM stream URL
ip = "192.168.186.92"
esp32_cam_url = f"http://{ip}:81/stream"

# โหลด Haar Cascade สำหรับการตรวจจับใบหน้า
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# stream = requests.get(esp32_cam_url, stream=True)

print("starting")



def send_command(ip,command):
    ts = int(time.time() * 1000)
    url = f"http://{ip}/{command}?time={ts}"  # Timestamp as a parameter
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Command '{command}' sent successfully with timestamp {ts}.")
    else:
        print(f"Error sending command: {response.status_code}")

def get_frame(stream):
    bytes = b''  # Buffer สำหรับเก็บข้อมูลที่ได้รับมาจาก stream
    for chunk in stream.iter_content(chunk_size=1024):
        # เก็บข้อมูลแต่ละ chunk ลงใน buffer
        bytes += chunk
        
        # หาเริ่มต้นและจบของ JPEG frame
        a = bytes.find(b'\xff\xd8')  # Start of JPEG
        b = bytes.find(b'\xff\xd9')  # End of JPEG
        
        # ถ้าเจอ frame JPEG ที่สมบูรณ์
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]  # ดึงข้อมูล JPEG ออกมา
            bytes = bytes[b+2:]  # ลบข้อมูล JPEG ออกจาก buffer
            
            if len(jpg) > 0:
                try:
                    # แปลง JPEG เป็นภาพ
                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    

                    if frame is not None:
                        # หมุนภาพ 90 องศา
                        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                        print(frame.shape)
                        # แปลงเป็น grayscale เพื่อใช้ในการตรวจจับใบหน้า
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        
                        # ตรวจจับใบหน้า
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                        
                        if len(faces) > 0:
                            print(f"Detected {len(faces)} face(s). Stopping the car.")
                            max_area = 0
                            for (x, y, w, h) in faces:
                                if w * h > max_area:
                                    max_area = w * h
                                    face_x, face_y, face_w, face_h = x, y, w, h
                            
                            return max_area, face_x, face_y, face_w, face_h
                        else:
                            # ไม่มีการตรวจจับใบหน้า
                            return 0, 0, 0, 0, 0
                except cv2.error as e:
                    print(f"Error decoding frame: {e}")
            else:
                print("Warning: Received empty jpg frame")

    # ถ้าไม่มีการส่งข้อมูลให้กลับค่าเริ่มต้น
    return 0, 0, 0, 0, 0



def rotate_left_findface(esp32_cam_url):
  while (True):
    stream = requests.get(esp32_cam_url, stream=True)
    max_area, face_x, face_y, face_w, face_h = get_frame(stream)
    print(max_area, face_x, face_y, face_w, face_h)
    if max_area > 0:
      send_command(ip,"ledon")
      time.sleep(0.2)
      send_command(ip,"ledoff")
      break
    
    time.sleep(0.2)

    send_command(ip,"step_left")

  return max_area, face_x, face_y, face_w, face_h

max_area, face_x, face_y, face_w, face_h = rotate_left_findface(esp32_cam_url)

while(max_area < 100*100):
  send_command(ip,"step_go")
  time.sleep(0.2)

  stream = requests.get(esp32_cam_url, stream=True)
  max_area, face_x, face_y, face_w, face_h = get_frame(stream)
  print(max_area, face_x, face_y, face_w, face_h)
  if max_area > 0:
    send_command(ip,"ledon")
    time.sleep(0.2)
    send_command(ip,"ledoff")
  elif max_area == 0:
    max_area, face_x, face_y, face_w, face_h = rotate_left_findface(esp32_cam_url)








