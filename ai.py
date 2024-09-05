import cv2
import numpy as np
import requests
import time
import threading

# ESP32-CAM stream URL
esp32_cam_url = "http://192.168.186.92:81/stream"

# โหลด Haar Cascade สำหรับการตรวจจับใบหน้า
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# ฟังก์ชันสำหรับการส่งคำสั่งไปยังรถ
def send_command(command, timestamp):
    url = f"http://192.168.186.92/{command}?time={timestamp}"  # Timestamp as a parameter
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Command '{command}' sent successfully with timestamp {timestamp}.")
    else:
        print(f"Error sending command: {response.status_code}")

# ฟังก์ชันสำหรับการหมุนรถและหยุดในลูป
def rotate_car():
    while not stop_event.is_set():  # ทำงานจนกว่า stop_event จะถูกตั้งค่า
        current_time = int(time.time() * 1000)  # Get current time in milliseconds
        send_command("left", current_time)  # หรือ "right" ถ้าต้องการให้หมุนขวา
        time.sleep(0.5)  # หมุนเป็นเวลา 

        current_time = int(time.time() * 1000)  # Update timestamp
        send_command("stop", current_time)  # หยุดรถ
        time.sleep(0.5)  # หยุดเป็นเวลา 


def sent_rotate_car():
    while not stop_event.is_set():  # ทำงานจนกว่า stop_event จะถูกตั้งค่า
        current_time = int(time.time() * 1000)  # Get current time in milliseconds
        send_command("step_left", current_time)  # หรือ "right" ถ้าต้องการให้หมุนขวา
        time.sleep(0.5)  # หมุนเป็นเวลา 

        current_time = int(time.time() * 1000)  # Update timestamp
        send_command("stop", current_time)  # หยุดรถ
        time.sleep(0.5)  # หยุดเป็นเวลา 

# เปิดการเชื่อมต่อสตรีม
stream = requests.get(esp32_cam_url, stream=True)

# ตรวจสอบว่าสามารถเข้าถึงสตรีมได้หรือไม่
if stream.status_code != 200:
    print("Error: Unable to open video stream")
    exit()

# ใช้ threading เพื่อให้ฟังก์ชัน rotate_car ทำงานใน background
stop_event = threading.Event()
rotate_thread = threading.Thread(target=sent_rotate_car)
rotate_thread.daemon = True  # ให้ thread นี้หยุดเมื่อโปรแกรมหลักหยุด
rotate_thread.start()

# อ่านและแสดงวิดีโอสตรีมเฟรมต่อเฟรม
bytes = b''
for chunk in stream.iter_content(chunk_size=1024):
    bytes += chunk
    a = bytes.find(b'\xff\xd8')  # Start of JPEG
    b = bytes.find(b'\xff\xd9')  # End of JPEG
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        
        if len(jpg) > 0:
            try:
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # หมุนภาพ 90 องศาทวนเข็มนาฬิกา (หรือใช้ cv2.ROTATE_90_CLOCKWISE สำหรับตามเข็ม)
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                    
                    # แปลงภาพเป็น grayscale สำหรับการตรวจจับใบหน้า
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # ตรวจจับใบหน้าในภาพ
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    # ถ้ามีการตรวจจับใบหน้าได้
                    if len(faces) > 0:
                        print(f"Detected {len(faces)} face(s). Stopping the car.")
                        stop_event.set() # ตั้งค่า event เพื่อหยุด rotate_car
                        current_time = int(time.time() * 1000)
                        send_command("stop", current_time)  # หยุดรถ
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                            print(x," ",y)
                        cv2.imwrite(r"D:/AI-Studied/face-found.jpg", frame)
                        print("write face to file")
                        break  # หยุดการทำงานของลูป

                    # วาดกรอบสี่เหลี่ยมรอบใบหน้าที่ตรวจจับได้
                

                    # แสดงผลภาพที่มีกล่องรอบใบหน้า
                    cv2.imshow('ESP32-CAM Face Detection (Vertical)', frame)
                    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except cv2.error as e:
                print(f"Error decoding frame: {e}")
        else:
            print("Warning: Received empty jpg frame")

# Cleanup
cv2.destroyAllWindows()