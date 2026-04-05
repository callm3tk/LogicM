import requests
import random
import time
from datetime import datetime

# Backend URL
API_URL = "http://localhost:8000/predict"

def send_sensor_data():
    """Gửi dữ liệu cảm biến giả lập tới API"""
    
    print("🌱 Smart Watering System - Sensor Simulator")
    print("=" * 50)
    print(f"API URL: {API_URL}")
    print(f"Started at: {datetime.now()}\n")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            
            # Tạo dữ liệu cảm biến giả lập (realistic values)
            soil = random.uniform(0, 100)      # 20-80% độ ẩm đất
            temp = random.uniform(0, 45)      # 15-35°C nhiệt độ
            hum = random.uniform(0, 100)       # 30-90% độ ẩm không khí
            
            # Format dữ liệu
            data = {
                "soil": round(soil, 1),
                "temp": round(temp, 1),
                "hum": round(hum, 1)
            }
            
            try:
                # Gửi request
                response = requests.get(API_URL, params=data, timeout=5)
                
                if response.status_code == 200:
                    result = response.json()
                    misting = result.get("misting", 0)
                    
                    print(f"[{iteration:3d}] {datetime.now().strftime('%H:%M:%S')}")
                    print(f"  🌍 Soil:      {data['soil']:6.1f}%")
                    print(f"  🌡️  Temp:      {data['temp']:6.1f}°C")
                    print(f"  💨 Humidity:  {data['hum']:6.1f}%")
                    print(f"  💧 Misting:   {misting:6.1f}% {'✅' if misting > 0 else '⛔'}")
                    print()
                    
                else:
                    print(f"❌ Error: Status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"❌ Cannot connect to backend. Is it running?")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                break
            
            # Đợi 3 giây trước khi gửi request tiếp
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n✅ Simulation stopped by user")

if __name__ == "__main__":
    send_sensor_data()
