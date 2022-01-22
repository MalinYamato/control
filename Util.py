#!/usr/bin/env python3

from socketIO_client import SocketIO
import requests
import time
import math

def seek_get_seconds():
    jres = requests.get('http://localhost:3000/api/v1/getState').json()
    print(jres)
    if "seek" in jres:
        seek = jres["seek"]
        if seek is not None:
            return int(jres["seek"] / 1000)
        else:
            return 0
    else:
        return 0


_seconds = 0
def reSeek(soc : SocketIO):
    global _seconds
    seconds = int(time.time())
    diff = int(seconds - _seconds)
    if _seconds == 0:
        _seconds = seconds
    if diff > 2:
        print("Do seek to current position " + str(diff))
        soc.emit('seek', str(seek_get_seconds()))
        _seconds = seconds

def distance(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))

def get(d, key):
    if key in d:
        v = d[key]
        if v is None:
            return ""
        elif type(v) == str:
            return v
        else:
            return str(v)
    return ""


