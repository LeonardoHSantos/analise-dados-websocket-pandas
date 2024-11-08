from time import sleep
import datetime


def check_datetime_to_M5(timestamp_ms):
  
    timestamp_s = timestamp_ms / 1000
    dt = datetime.datetime.utcfromtimestamp(timestamp_s)

    print(dt)

    if dt.minute in [4,9,14,19,24,29,34,39,44,49,54,59]:
        if dt.second >= 50 and dt.second <= 55:
            print(f"\n MIN: {dt.minute} | SEG: {dt.second} | CHAMAR OP: {True}")
            return True
    
    print(f">> MIN: {dt.minute} | SEG: {dt.second} | CHAMAR OP: {False} \n")
    
    return False