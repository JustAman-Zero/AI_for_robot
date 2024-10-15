import cv2
import numpy as np
import requests
import time
from ultralytics import YOLO
import random

# ESP32-CAM stream URL
ip = "192.168.137.171"
esp32_cam_url = f"http://{ip}:81/stream"
model = YOLO('yolov8n.pt') 

# โหลด Haar Cascade สำหรับการตรวจจับใบหน้า

# stream = requests.get(esp32_cam_url, stream=True)

# print("starting")

def send_command(command,direction,step):
  """Sends a GET request to a URL with the specified command and timestamp.

  Args:
      command: The command to send (e.g., "go", "left", "stop").
  """
  ip2 = "192.168.137.171"
  # url = f"http://192.168.55.92/{command}?{int(time.time()*1000)}"  # Using time.time() for timestamp
  url = f"http://{ip2}/{command}?direction={direction}&step={step}"  # Using time.time() for timestamp
  response = requests.get(url)

  # Handle response (optional)
  # response = requests.get(url)

  # Handle response (optional)
  if response.status_code == 200:
    print(f"Command '{command}' sent successfully.")
  else:
    print(f"Error sending command: {response.status_code}")

# Example usage
# send_command("step_command", "forward", "1000")

def send_command_old(ip,command):
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
      print(label,x1,y1,(x2-x1),(y2-y1))
      # Draw the bounding box
      cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green bounding box with thickness 2

      # Add the label for the detected object
      cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


def find_objects_id(img,model,id):
  results = model(img)
  class_names = model.names


# Loop through the detected objects and draw bounding boxes for 'person' class (class index 0 in COCO dataset)
  for i, box in enumerate(results[0].boxes.xyxy):
      # Get bounding box coordinates (convert to int)
      x1, y1, x2, y2 = map(int, box)
      w = abs(x2-x1)
      h = abs(y2-y1)
      
      # Get the class index and score
      class_idx = int(results[0].boxes.cls[i])
      print(class_idx)
      score = results[0].boxes.conf[i]
      label = f"{class_idx} {class_names[class_idx]} {score:.2f}"

      if class_idx == id:
        # send_command(ip,"bling")
        # print(label)
        return w*h, x1, y1, w, h
      # Get the class label from the class index
      
  return 0,0,0,0,0

print("before while")

last_step = "" 

while True:
  frame = get_frame_img(esp32_cam_url)
  a,x,y,w,h = find_objects_id(frame, model,3)
  
  print(a,x+w/2)


  if a == 0:
    if last_step == "step_left":
      # send_command_old(ip,"step_right")
      send_command("step_command","left","100")
      last_step = "step_left"
      print(f"left")
    elif last_step == "step_right":
      send_command("step_command","right","100")
      last_step = "step_right"
      print(f"right")
      # send_command_old(ip,"step_left")
      # last_step=""
    elif "step_go step_left" in last_step:
        send_command("step_command","right","100")
        last_step = ""
        print(f"right")
    elif "step_go step_right" in last_step:
        send_command("step_command","left","100")
        last_step = ""
        print(f"left")
    else:
        x = random.choice(["left", "right", "forward"])
        y = random.random()*900+100
        send_command("step_command",x,str(y))
        # send_command("step_command",x,"100")
        

  else:
    if x+w//2 > 150:
      # send_command_old(ip,"step_left")
      send_command("step_command","left",str(int(((x+w/2)-120)/120*100)))
      last_step = "step_left"
      print(f"left")
    elif x+w//2 < 90:
      # send_command_old(ip,"step_right")
      # send_command("step_command","right","100")
      send_command("step_command","right",str(int((120-(x+w/2))/120*100)))
      last_step = "step_right"
      print(f"right")


  if a>0 and a<5000:
    
    m = int((5000-a)/10)
    if 110<=(x+w//2) or (x+w//2)>=130:
      m = 100
    send_command("step_command","forward",str(m))
    # send_command_old(ip,"step_go")
    print(f"forward area:{m}")
    last_step = "step_go "+ last_step

  time.sleep(0.2)



