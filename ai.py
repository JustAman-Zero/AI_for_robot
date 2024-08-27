import requests
import time

def send_command(command, timestamp):
    """Sends a GET request to a URL with the specified command and timestamp.

    Args:
        command: The command to send (e.g., "go", "left", "stop").
        timestamp: The timestamp to attach to the command.
    """
    url = f"http://192.168.238.245/{command}?time={timestamp}"  # Timestamp as a parameter
    response = requests.get(url)

    # Handle response (optional)
    if response.status_code == 200:
        print(f"Command '{command}' sent successfully with timestamp {timestamp}.")
    else:
        print(f"Error sending command: {response.status_code}")

# Example usage
commands = ["left", "right", "stop"]

for command in commands:
    current_time = int(time.time() * 2000)  # Get current time in milliseconds
    send_command(command, current_time)
    time.sleep(2)  # Wait for 2 seconds between each command