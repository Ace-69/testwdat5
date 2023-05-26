from test import *
import datetime as dt
def main():
    parameters = {
        "station_id": 0, # any int
        "path": "/path/to/wlk/file", # global path to where you store wlk files
        "timezone": "Europe/Rome", # your weather station timezone
        "storage_format": "wdat5" # useless parameter but needed for the program to run 
    }
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
    c = {
        "datetime": dt.datetime.strftime(b["timestamp"], '%d/%m/%Y %X'), # date and time of the measurement
        "temperature": round((b["hioutsidetemp"]+b["lowoutsidetemp"])/2), # avg min and max temperatures (?)
        "winddirection": degToCompass(b["winddirection"]),
        "windspeed": round(b["windspeed"]),
        "humidity": round(b["outsidehum"]),
        "pressure": round(b["barometer"], 1)
    }
#   output
    print(c)

    
#    look for all the values in the array b

#    for p, q in b.items():
#        print(p + " : " + str(q))

#   used to put to string a float value
def degToCompass(num):
    val = int((num/22.5)+.5)
    arr = ["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]

if __name__ == "__main__":
    main()