import json
import struct
import os
import datetime as dt
from zoneinfo import ZoneInfo

def main():
    filename = "2023-05.wlk"
    with open(filename, "rb") as f:
        head = f.read(212)
        print(head[:6])
        year, month = [
            int(x) for x in os.path.split(filename)[1].split(".")[0].split("-")
        ]
        for day in range(1, 32):
            i = 20 + (day * 6)
            j = i + 6
            day_index = head[i:j]

            records_in_day = struct.unpack("<h", day_index[:2])[0]
            start_pos = struct.unpack("<l", day_index[2:])[0]
            if records_in_day != 0:
                print("----------------------------------------------------------")
                print("records: " + str(records_in_day) + " Position: " + str(start_pos))
                all_decoded = {}
                for r in range(records_in_day):
                    f.seek(212 + (start_pos+r) *88)
                    record = f.read(88)
                    if record[0] != b"\x01"[0]:
                        continue
                    decoded = decode(record)
                    timestamp = dt.datetime(
                        year=year, month=month, day=day, tzinfo=ZoneInfo("Europe/Rome")
                    ) + dt.timedelta(minutes=decoded["packedtime"])
                    

                    decoded["timestamp"] = timestamp.isoformat()
                    all_decoded[r] = decoded
                
                print(json.dumps(all_decoded, indent=4), "\n")
                    
def decode(record):
    wdat_record_format = [
        "<b dataType",
        "<b archiveInterval",
        "<b iconFlags",
        "<b moreFlags",
        "<h packedTime",
        "<h outsideTemp",
        "<h hiOutsideTemp",
        "<h lowOutsideTemp",
        "<h insideTemp",
        "<h barometer",
        "<h outsideHum",
        "<h insideHum",
        "<H rain",
        "<h hiRainRate",
        "<h windSpeed",
        "<h hiWindSpeed",
        "<b windDirection",
        "<b hiWindDirection",
        "<h numWindSamples",
        "<h solarRad",
        "<h hiSolarRad",
        "<B UV",
        "<B hiUV",
        "<b leafTemp1",
        "<b leafTemp2",
        "<b leafTemp3",
        "<b leafTemp4",
        "<h extraRad",
        "<h newSensors1",
        "<h newSensors2",
        "<h newSensors3",
        "<h newSensors4",
        "<h newSensors5",
        "<h newSensors6",
        "<b forecast",
        "<B ET",
        "<b soilTemp1",
        "<b soilTemp2",
        "<b soilTemp3",
        "<b soilTemp4",
        "<b soilTemp5",
        "<b soilTemp6",
        "<b soilMoisture1",
        "<b soilMoisture2",
        "<b soilMoisture3",
        "<b soilMoisture4",
        "<b soilMoisture5",
        "<b soilMoisture6",
        "<b leafWetness1",
        "<b leafWetness2",
        "<b leafWetness3",
        "<b leafWetness4",
        "<b extraTemp1",
        "<b extraTemp2",
        "<b extraTemp3",
        "<b extraTemp4",
        "<b extraTemp5",
        "<b extraTemp6",
        "<b extraTemp7",
        "<b extraHum1",
        "<b extraHum2",
        "<b extraHum3",
        "<b extraHum4",
        "<b extraHum5",
        "<b extraHum6",
        "<b extraHum7",
    ]
    result = {}

    # Read raw values
    offset = 0
    for item in wdat_record_format:
        fmt, name = item.split()
        result[name.lower()] = struct.unpack_from(fmt, record, offset)[0]
        offset += struct.calcsize(fmt)

    for x in ["outsidetemp", "hioutsidetemp", "lowoutsidetemp", "insidetemp"]:
        result[x] = ((result[x] / 10.0) - 32) * 5 / 9.0


    # Convert pressure
    result["barometer"] = (
        result["barometer"] / 1000.0 * 25.4 * 1.33322387415
    )

    # Convert humidity
    for x in ["outsidehum", "insidehum"]:
        result[x] = result[x] / 10.0

    # Convert rain
    rain_collector_type = result["rain"] & 0xF000
    rain_clicks = result["rain"] & 0x0FFF
    depth_per_click = {
        0x0000: 0.1 * 25.4,
        0x1000: 0.01 * 25.4,
        0x2000: 0.2,
        0x3000: 1.0,
        0x6000: 0.1,
    }[rain_collector_type]
    depth = depth_per_click * rain_clicks
    result["rain"] = depth
    rate = result["hirainrate"] * depth_per_click
    result["hirainrate"] = rate

    # Convert wind speed
    def convert_wind_speed(x):
        return x / 10.0 * 1609.344 / 3600

    result["windspeed"] = convert_wind_speed(result["windspeed"])
    result["hiwindspeed"] = convert_wind_speed(result["hiwindspeed"])

    # Convert wind direction
    for x in ["winddirection", "hiwinddirection"]:
        result[x] = result[x] / 16.0 * 360 if result[x] >= 0 else "NaN"

    # Convert UV index
    result["uv"] = result["uv"] / 10.0
    result["hiuv"] = result["hiuv"] / 10.0

    # Convert evapotranspiration
    result["et"] = result["et"] / 1000.0
    

    # Convert matric potential
    for i in range(1, 7):
        varname = "soilmoisture" + str(i)
        result[varname] = result[varname] / 9.80638

    # Convert extraTemp etc.
    extratemps = [
        "extratemp1",
        "extratemp2",
        "extratemp3",
        "extratemp4",
        "extratemp5",
        "extratemp6",
        "extratemp7",
        "soiltemp1",
        "soiltemp2",
        "soiltemp3",
        "soiltemp4",
        "soiltemp5",
        "soiltemp6",
        "leaftemp1",
        "leaftemp2",
        "leaftemp3",
        "leaftemp4",
    ]
    for x in extratemps:
        result[x] = ((result[x] - 90) - 32) * 5 / 9.0

    return result

main()
