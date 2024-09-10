import cv2
import numpy as np
import requests
import time
from ultralytics import YOLO

# ESP32-CAM stream URL
ip = "192.168.186.92"
esp32_cam_url = f"http://{ip}:81/stream"
model = YOLO('yolov8n.pt') 

# โหลด Haar Cascade สำหรับการตรวจจับใบหน้า

# stream = requests.get(esp32_cam_url, stream=True)

# print("starting")


def send_command(ip,command):
    ts = int(time.time() * 1000)
    url = f"http://{ip}/{command}?time={ts}"  # Timestamp as a parameter
    response = requests.get(url)

    if response.status_code == 200:
        print(f"Command '{command}' sent successfully with timestamp {ts}.")
    else:
        print(f"Error sending command: {response.status_code}")

def get_frame_img(esp32_cam_url):
  stream = requests.get(esp32_cam_url, stream=True)
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

                      return frame
              except cv2.error as e:
                  print(f"Error decoding frame: {e}")
          else:
              print("Warning: Received empty jpg frame")

    # ถ้าไม่มีการส่งข้อมูลให้กลับค่าเริ่มต้น
  return None

def find_objects(img,model):
  results = model(img)
  class_names = model.names
# Loop through the detected objects and draw bounding boxes for 'person' class (class index 0 in COCO dataset)
  for i, box in enumerate(results[0].boxes.xyxy):
      # Get bounding box coordinates (convert to int)
      x1, y1, x2, y2 = map(int, box)
      
      # Get the class index and score
      class_idx = int(results[0].boxes.cls[i])
      score = results[0].boxes.conf[i]
      # Get the class label from the class index
      label = f"{class_names[class_idx]} {score:.2f}"
      print(label)
      # Draw the bounding box
      cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green bounding box with thickness 2

      # Add the label for the detected object
      cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


print("before while")
while True:
  frame = get_frame_img(esp32_cam_url)
  find_objects(frame, model)
  time.sleep(0.2)

