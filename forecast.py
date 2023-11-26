import json
from datetime import datetime
import sys

def parse_forecast(json_str):
    data = json.loads(json_str)
    forecast = data['ForecastSeries']
    payload = []

    for item in forecast:
        timestamp = item['TimeStamp']['DateTime']
        pv_watt = item['PvMeanPower']['Amount']

        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        unix_time_seconds = int(dt.timestamp()) * 1000

        payload_forecast = {
            "time": unix_time_seconds,
            "watt": float(pv_watt)
        }
        payload.append(payload_forecast)
    payload = json.dumps(payload)
    return payload

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python forecast.py forecast.json")
        sys.exit(1)

    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as file:
            json_data = file.read()
            result = parse_forecast(json_data)
            print(result) 
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        sys.exit(1)
