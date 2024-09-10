import requests
import time

def send_command(command):
  """Sends a GET request to a URL with the specified command and timestamp.

  Args:
      command: The command to send (e.g., "go", "left", "stop").
  """
  url = f"http://192.168.186.92/{command}?{int(time.time()*1000)}"  # Using time.time() for timestamp
  response = requests.get(url)

  # Handle response (optional)
  if response.status_code == 200:
    print(f"Command '{command}' sent successfully.")
  else:
    print(f"Error sending command: {response.status_code}")

# Example usage
send_command("bling")