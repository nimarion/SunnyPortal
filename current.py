import json
import sys

def parse_current(json_str):
    payload = []
    jsonObject = json.loads(json_str)
    entries = jsonObject.get("Entries")
    series = {}

    for entry in entries:
        entry_type = entry.get("Type")
        if entry_type not in ("DataSeries", "DataPoint"):
            continue

        optional_info = entry.get("OptionalInfo")
        serie = int(optional_info.get("SeriesNumber"))

        if entry_type == "DataSeries":
            key = optional_info.get("Key")
            series[serie] = key
        elif entry_type == "DataPoint":
            serie_value = series.get(serie)
            time = int(optional_info.get("RawValueX")) * 1000
            value = float(optional_info.get("ValueY").replace(",", ""))
            if "." in optional_info.get("ValueY"):
                value *= 1000

            payload_entry = {
                "time": time,
                "watt": value,
                "type": serie_value
            }
            payload.append(payload_entry)

    return json.dumps(payload)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python forecast.py PortalChartsAPI.aspx")
        sys.exit(1)

    input_file = ' '.join(sys.argv[1:])
    
    try:
        with open(input_file, 'r') as file:
            json_data = file.read()
            result = parse_current(json_data)
            print(result) 
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        sys.exit(1)
