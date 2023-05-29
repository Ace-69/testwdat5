from test import *
import datetime as dt
import configparser as cp
import requests as req
import json
import schedule
import time

def main():
    config = cp.ConfigParser()
    config.read('config.ini')

    if "BASE" in config.sections():
        base = config["BASE"]
    else:
        base = {
            "remote": "http://localhost/api/Push.php", # URL to the page to process data
            "authUser": "username", # Username for HTTP auth
            "authPassword": "password" # Password for HTTP auth
        }
        config["BASE"] = base
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    if "Parameters" in config.sections():
        parameters = config["Parameters"]
    else: 
        parameters = {
            "station_id": 0, # any int
            "path": "/path/to/wlk/file", # global path to where you store wlk files
            "timezone": "Europe/Rome", # your weather station timezone
            "storage_format": "wdat5", # useless parameter but needed for the program to run 
        }
        config["Parameters"] = parameters
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    wdat = wdat5(parameters)
    date = dt.datetime.now()
#   format day mont year of today for the date and filename
    day = str(date.day) if date.day >= 10 else "0" + str(date.day)
    month = str(date.month) if date.month >= 10 else "0" + str(date.month)
    year = str(date.year-2000) if (date.year-2000) >= 10 else "0" + str(date.year-2000)

    strdatetoday = day + "/" +month + "/" + year
    filename = str(date.year) + "-" + month + ".wlk"

#   get info from the file
    a = wdat._get_tail_part("18/05/23", filename)
#   get last measurement
    b = a[len(a)-1]
#   get only the needed data
    data = {
        "datetime": dt.datetime.strftime(b["timestamp"], '%d/%m/%Y %X'), # date and time of the measurement
        "temperature": round((b["hioutsidetemp"]+b["lowoutsidetemp"])/2), # avg min and max temperatures (?)
        "winddirection": degToCompass(b["winddirection"]),
        "windspeed": round(b["windspeed"]),
        "humidity": round(b["outsidehum"]),
        "pressure": round(b["barometer"], 1)
    }


#   output
    print("fetched:")
    print(data)

    res = HTTPAuthPostRequest(base["remote"], data ,base["authUser"], base["authPassword"])

    try:
        res = json.loads(res)

        if res["Response"] == "Done":
            print("Data sent succesfully")
        elif res["Response"] == "No data":
            print("Error: No data")
        else:
            print(res["Response"])
    except json.JSONDecodeError as e:
        print("Server error")
    
#    look for all the values in the array b

#    for p, q in b.items():
#        print(p + " : " + str(q))

#   used to put to string a float value

def HTTPAuthPostRequest(url , data:list , username, password):
    res = req.post(url, data, auth=(username, password))
    return res.content.decode()

def degToCompass(num):
    val = int((num/22.5)+.5)
    arr = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]

if __name__ == "__main__":
    main()

schedule.every(30).minutes.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
