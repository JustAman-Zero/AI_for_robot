import requests
import time

def send_command(command,direction,step):
  """Sends a GET request to a URL with the specified command and timestamp.
  Args:
      command: The command to send (e.g., "go", "left", "stop").
  """
  # url = f"http://192.168.55.92/{command}?{int(time.time()*1000)}"  # Using time.time() for timestamp
  url = f"http://192.168.137.35/{command}?direction={direction}&step={step}"  # Using time.time() for timestamp
  response = requests.get(url)

  # Handle response (optional)
  # response = requests.get(url)
  # Handle response (optional)
  if response.status_code == 200:
    print(f"Command '{command}' sent successfully.")
  else:
    print(f"Error sending command: {response.status_code}")

send_command("step_command", "stop", "1000")
# Example usage
#   send_command("step_command", "forward", "1000")
#   send_command("step_command", "right_rotate", "1000")
#   send_command("step_command", "left_rotate", "1000")
#   send_command("step_command", "right_rotate", "1000")