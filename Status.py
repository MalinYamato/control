#!/usr/bin/env python3

import json
import requests
from Util import *
from socketIO_client import SocketIO

def getBitrate(soc: SocketIO):
    jres = requests.get('http://localhost:3000/api/v1/getState').json()
    bitrate = ""

    if "bitrate" not in jres:
        return bitrate
    elif jres["bitrate"] is None:
        print("no bitrate,,, trying again")
        reSeek(soc)
        jres = requests.get('http://localhost:3000/api/v1/getState').json()
        if "bitrate" not in jres:
            return bitrate
        if jres["bitrate"] is None:
            print("No bitrate after second try!")
            bitrate = ""
        else:
            bitrate = str(jres["bitrate"])
    else:
        bitrate = str(jres["bitrate"])

    return bitrate.split(' ')[0]

_seconds = 0


class Status:
    def __init__(self, status):
        self.raw = status
        self.s_service = get(status, 'service')
        self.s_status = get(status, 'status')
        self.s_artist = get(status, 'artist')
        self.s_title = get(status, 'title')
        self.s_bitdepth = get(status, 'bitdepth')
        self.s_samplerate = get(status, 'samplerate')
        self.s_position = get(status, 'position')
        self.s_bitrate = get(status, 'bitrate')
        self.s_trackType = get(status, 'trackType')
        self.s_uri =  get(status, 'uri')
      #  if self.s_bitrate == "":
      #      self.s_bitrate = getBitrate()
      #  self.s_bitrate = self.s_bitrate.split(' ')[0]

    @classmethod
    def getStatus(self):
        return Status(requests.get('http://localhost:3000/api/v1/getState').json())

    def dump(self):
        print(self.s_status, self.s_service, self.s_position, self.s_artist, self.s_title, self.s_bitrate,
              self.s_samplerate, self.s_bitdepth)
        print(self.raw)

    def isFLAC(self):
        raw = json.dumps( self.raw )
        if raw.find("FLAC") != -1:
            return True
        if raw.find("flac") != -1:
            return True
        return False

    def isDLNA(self):
        raw = json.dumps(self.raw)
        return raw.find("AirMusic") != -1

    def isAirPlay(self):
        return self.s_trackType == "airplay"