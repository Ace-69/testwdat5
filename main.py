from test import *
def main():
    print("start", "|")
    parameters = {
        "station_id":1,
        "path": "C:\\Users\\5E_2022_23\\Desktop\\Somma Francesco\\test",
        "timezone": "Europe/Rome",
        "storage_format": "wdat5"
    }
    wdat = wdat5(parameters)
    print("test")
    a = wdat._get_tail_part("18/05/23", "2023-05.wlk")
    print(a, " | ")

if __name__ == "__main__":
    main()