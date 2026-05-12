import requests

def test_api():
    base_url = "http://localhost:8000"
    
    # Test Root
    try:
        r = requests.get(f"{base_url}/")
        print("Root:", r.status_code, r.json())
    except Exception as e:
        print("Root failed:", e)

    # Test Health
    try:
        r = requests.get(f"{base_url}/health")
        print("Health:", r.status_code, r.json())
    except Exception as e:
        print("Health failed:", e)

    # Test Telemetry
    try:
        r = requests.get(f"{base_url}/telemetry")
        print("Telemetry:", r.status_code, r.json() if r.status_code == 200 else r.text)
    except Exception as e:
        print("Telemetry failed:", e)

    # Test Route
    try:
        r = requests.get(f"{base_url}/route")
        print("Route:", r.status_code, r.json() if r.status_code == 200 else r.text)
    except Exception as e:
        print("Route failed:", e)

    # Test IoT Update
    try:
        payload = {
            "bin_id": 1,
            "fill_level": 85,
            "gas_level": 12.0,
            "temperature": 34.5,
            "humidity": 45.0,
            "battery": 90.0,
            "latitude": 28.7041,
            "longitude": 77.1025
        }
        r = requests.post(f"{base_url}/iot/update", json=payload)
        print("IoT Update:", r.status_code, r.json() if r.status_code == 200 else r.text)
    except Exception as e:
        print("IoT Update failed:", e)

if __name__ == "__main__":
    test_api()
