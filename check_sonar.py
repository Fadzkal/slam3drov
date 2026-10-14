import urllib.request
import json

def check():
    print("Checking for Sonar/Distance sensor on BlueROV2...")
    # Check mavlink DISTANCE_SENSOR
    try:
        url = "http://192.168.2.2/mavlink2rest/mavlink/vehicles/1/components/1/messages/DISTANCE_SENSOR"
        with urllib.request.urlopen(url, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            print("FOUND MAVLink DISTANCE_SENSOR:", data)
    except Exception as e:
        print("MAVLink DISTANCE_SENSOR:", e)

    # Check BlueOS services
    for path in ["/ping/v1.0/devices", "/v1.0/endpoints", "/v1.0/services"]:
        try:
            url = f"http://192.168.2.2{path}"
            with urllib.request.urlopen(url, timeout=2) as resp:
                print(f"BlueOS {path}:", resp.read().decode()[:200])
        except Exception as e:
            print(f"BlueOS {path}:", e)

if __name__ == "__main__":
    check()
