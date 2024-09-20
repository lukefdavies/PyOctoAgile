import requests
import sys

# Replace with your Home Assistant URL and Long-Lived Access Token
HOME_ASSISTANT_URL = "http://127.0.0.1:8123"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNTBkM2M3NTg3NDA0ZWE4YWNiMzA4ODgwMDlhMTUxYSIsImlhdCI6MTcyNjYwNzQ1MywiZXhwIjoyMDQxOTY3NDUzfQ.1nTSbBVstb2yE1H6QnjnK0_RJuX1E7yv_FIFUS6n3f4"

# Thermostat entity ID
ENTITY_ID = "climate.living_room"

# Define the service URL to call the climate.set_temperature service
url = f"{HOME_ASSISTANT_URL}/api/services/climate/set_temperature"

# Headers to authenticate with Home Assistant
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <temperature>")
        sys.exit(1)

    try:
        TARGET_TEMPERATURE = float(sys.argv[1])
    except ValueError:
        print("Invalid temperature value")
        sys.exit(1)

    # Payload to control the thermostat
    payload = {
        "entity_id": ENTITY_ID,
        "temperature": TARGET_TEMPERATURE
    }

    # Send the request
    response = requests.post(url, json=payload, headers=headers)

    # Check the response
    if response.status_code == 200:
        print(f"Successfully set temperature to {TARGET_TEMPERATURE}°C")
    else:
        print(f"Failed to set temperature. Status code: {response.status_code}, Response: {response.text}")
