#!/usr/bin/env python3

#// Copyright 2017 Malin Yamato --  All rights reserved.
#// https://github.com/MalinYamato
#//
#// MIT License
#// Redistribution and use in source and binary forms, with or without
#// modification, are permitted provided that the following conditions are
#// met:
#//
#//     * Redistributions of source code must retain the above copyright
#// notice, this list of conditions and the following disclaimer.
#//     * Redistributions in binary form must reproduce the above
#// copyright notice, this list of conditions and the following disclaimer
#// in the documentation and/or other materials provided with the
#// distribution.
#//     * Neither the name of Rakuen. nor the names of its
#// contributors may be used to endorse or promote products derived from
#// this software without specific prior written permission.
#//
#// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import requests
import asyncio
import math
import _thread
import time
import sys
import threading
import socket
import json
from enum import Enum, IntEnum

import Text
from Text import RGB
import PlayList
from PlayList import Station
import Dots

from Dots import seek_get_seconds

from socketIO_client import SocketIO, LoggingNamespace
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from unicornhatmini import UnicornHATMini
from colorsys import hsv_to_rgb

unicornhatmini = UnicornHATMini()
unicornhatmini.set_brightness(0.5)
unicornhatmini.set_rotation(180)
width, height = unicornhatmini.get_shape()

splash_origin = (0, 0)
splash_time = 0

socketIO = SocketIO('localhost', 3000)
status = 'unknown'

_debug = False
_i = 0
_doDots = False
_timer = None
_bitrateTimer = None

def distance(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))


def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

def airplayDrawing():
    global unicornhatmini
    u = unicornhatmini
    r = 0
    g = 184
    b = 230
    xo = 3
    xd = 10
    u.set_all(0,0,0)
    u.set_brightness(0.05)
    for x in range(xd):
        u.set_pixel(xo + x, 1, r, g, b)
    for y in range(4):
        u.set_pixel(xo, y+1, r, g, b)
    for y in range(4):
        u.set_pixel(xo+xd, y+1, r, g, b)
    u.set_pixel(xo + 1, 4, r, g, b)
    u.set_pixel(xo + xd-1, 4, r, g, b)
    for x in range(5):
        u.set_pixel(xo + 3 + x, 5, r, g, b)
    for x in range(3):
        u.set_pixel(xo + 4 + x, 4, r, g, b)
    u.set_pixel(xo + 5, 3, r, g, b)
    u.show()

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


def getBitrate():
    global _block_messages
    jres = requests.get('http://localhost:3000/api/v1/getState').json()
    bitrate = ""

    if "bitrate" not in jres:
        return bitrate
    elif jres["bitrate"] is None:
        print("no bitrate,,, trying again")
        _block_messages = True
        reSeek()
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


def bitdepth(unicornhatmini, bitdepth):
    r = 0
    g = 0
    b = 255
    y = 5
    if bitdepth.find("16") != -1:
        unicornhatmini.set_pixel(16, y, r, g, b)
    if bitdepth.find("24") != -1:
        unicornhatmini.set_pixel(15, y, r, g, b)
        unicornhatmini.set_pixel(16, y, r, g, b)
    if bitdepth.find("32") != -1:
        unicornhatmini.set_pixel(14, y, r, g, b)
        unicornhatmini.set_pixel(15, y, r, g, b)
        unicornhatmini.set_pixel(16, y, r, b, b)


def samplerate(unicornhatmini, samplerate):
    r = 0
    g = 0
    b = 255
    y = 5
    if samplerate.find("44") != -1:
        unicornhatmini.set_pixel(0, y, r, g, b)
    if samplerate.find("48") != -1:
        unicornhatmini.set_pixel(0, y, r, g, b)
        unicornhatmini.set_pixel(1, y, r, g, b)
    if samplerate.find("96") != -1 or samplerate.find("88.2") != -1:
        unicornhatmini.set_pixel(0, y, r, g, b)
        unicornhatmini.set_pixel(1, y, r, g, b)
        unicornhatmini.set_pixel(2, y, r, g, b)
    if samplerate.find("192") != -1:
        unicornhatmini.set_pixel(0, y, r, g, b)
        unicornhatmini.set_pixel(1, y, r, g, b)
        unicornhatmini.set_pixel(2, y, r, g, b)
        unicornhatmini.set_pixel(3, y, r, g, b)
    if samplerate.find("384") != -1:
        g = 255
        unicornhatmini.set_pixel(0, y, r, g, b)
        unicornhatmini.set_pixel(1, y, r, g, b)
        unicornhatmini.set_pixel(2, y, r, g, b)
        unicornhatmini.set_pixel(3, y, r, g, b)


def display_play(status):
    bitdepth(unicornhatmini, status.s_bitdepth)
    samplerate(unicornhatmini, status.s_samplerate)
    unicornhatmini.set_pixel(7, 5, 0, 0, 0)
    unicornhatmini.set_pixel(7, 6, 0, 0, 0)
    unicornhatmini.set_pixel(9, 5, 0, 0, 0)
    unicornhatmini.set_pixel(9, 6, 0, 0, 0)
    unicornhatmini.show()


def display_pause():
    r = 255
    g = 0
    b = 0
    unicornhatmini.set_pixel(14, 1, r, g, b)
    unicornhatmini.set_pixel(14, 2, r, g, b)
    unicornhatmini.set_pixel(16, 1, r, g, b)
    unicornhatmini.set_pixel(16, 2, r, g, b)
    unicornhatmini.show()


def display_stop():
    r = 255
    g = 0
    b = 0
    unicornhatmini.set_all(0, 0, 0)

    unicornhatmini.set_pixel(7, 2, r, g, b)
    unicornhatmini.set_pixel(8, 2, r, g, b)
    unicornhatmini.set_pixel(9, 2, r, g, b)
    unicornhatmini.set_pixel(7, 3, r, g, b)
    unicornhatmini.set_pixel(8, 3, r, g, b)
    unicornhatmini.set_pixel(9, 3, r, g, b)
    unicornhatmini.set_pixel(7, 4, r, g, b)
    unicornhatmini.set_pixel(8, 4, r, g, b)
    unicornhatmini.set_pixel(9, 4, r, g, b)
    unicornhatmini.show()


_seconds = 0


def reSeek():
    global _seconds
    seconds = int(time.time())
    diff = int(seconds - _seconds)
    if _seconds == 0:
        _seconds = seconds
    if diff > 2:
        print("Do seek to current position " + str(diff))
        socketIO.emit('seek', seek_get_seconds())
        _seconds = seconds


_playlist = PlayList.Playlist()



class ModeEnum(IntEnum):
    Position = 1
    BitRate = 2
    DetailFlow = 3
    Webradio = 4
    SysInfo = 5
    Last = 6
    EditPlayList = 7


    def describe(self):
        return self.name


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
        if self.s_bitrate == "":
            self.s_bitrate = getBitrate()
        self.s_bitrate = self.s_bitrate.split(' ')[0]

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

class Mode:
    def __init__(self):
        self._modeEnum = ModeEnum.Position
        self._status = Status.getStatus()

    def cycle(self, aStatus):
        self._status = aStatus
        self._modeEnum = 1 + int(self._modeEnum)
        if self._modeEnum >= ModeEnum.Last:
            self._modeEnum = 1
        self.set(self._status)

    def set(self, aStatus):
        self._status = aStatus
        if self._status.s_trackType == "airplay" and self._modeEnum != ModeEnum.SysInfo and self._modeEnum != ModeEnum.Webradio:
            airplayDrawing()
            return
        if (self._status.s_status == "stop" or self._status.s_status == "") and self._modeEnum != ModeEnum.SysInfo:
            _text.dotext("M" + str(self._modeEnum))
            return
        elif self._modeEnum == ModeEnum.Position :
            self.setPosition()
        if self._modeEnum == ModeEnum.BitRate:
            self.setBitrate()
        elif self._modeEnum == ModeEnum.DetailFlow:
            self.setDetailFlow()
        elif self._modeEnum == ModeEnum.SysInfo:
            self.setSysInfo()
        elif self._modeEnum == ModeEnum.Webradio:
            self.setWebradio()
        elif self._modeEnum == ModeEnum.EditPlayList:
            self.editPlaylist()

    def escape(self):
        self._modeEnum = 1
        self.set(Status.getStatus())

    def isA(self, enum):
        return enum == self._modeEnum

    def getValue(self):
        return ModeEnum(self._modeEnum).describe()

    def isPrevNextMode(self):
        return self._modeEnum < 4

    def setPosition(self):
        if self._status.s_service == "webradio":
            _text.dotext(self._status.s_title)
        else:
            _text.dotext(self._status.s_position)
            _dots.start()
            display_play(self._status)

    def setBitrate(self):
        if self._status.isFLAC():
            _text.dotext("FLAC")
        else:
            _text.dotext(self._status.s_bitrate)
        _dots.start()
        display_play(self._status)


    def setDetailFlow(self):
        _dots.stop()
        _text.stop()
        res = self._status.s_samplerate.split(' ')[0] + "/" + self._status.s_bitdepth.split(' ')[0]
        if len(res) < 2:
            res = " "
        else:
            res = " " + res + " "
        _text.rainbow = False
        _text.start(self._status.s_title +
                    " by " + self._status.s_artist + res + getBitrate() + " bps " + self._status.s_service)


    def setSysInfo(self):
        _text.stop()
        _dots.stop()
        _text.rainbow = False
        _text.start(getNetworkIp())

    def editPlaylist(self):
        self._modeEnum = ModeEnum.EditPlayList
        _text.stop()
        _dots.stop()
        _text.dotext("+O-")

    def setWebradio(self):
        self._modeEnum = ModeEnum.Webradio
        _text.dotext(self._status.s_title)

    def dump(self):
        print("Mode :", self.getValue())
        Status.getStatus().dump()

    @property
    def modeEnum(self):
        return self._modeEnum


_dots = Dots.Dots(unicornhatmini)
_text = Text.Text(unicornhatmini)
_mode = Mode()

_bitrate = ""


def updateBitrate():
    global _bitrate
    global _bitrateTimer
    if _mode.isA(ModeEnum.BitRate):
        stat = Status.getStatus()
        if stat.s_status != "pause" and stat.s_status != "stop" and not stat.isDLNA() and not stat.isAirPlay():
            if stat.isFLAC():
                _text.dotext("FLAC")
                _dots.start()
                display_play(stat)
            else:
                bitrate = getBitrate()
                print("not flack")
                if bitrate != _bitrate:
                    _bitrate = bitrate
                    _dots.seek()
                    _text.dotext(_bitrate)
        _bitrateTimer = threading.Timer(10, updateBitrate)
        _bitrateTimer.start()


def pressed(button):
    global splash_origin, splash_time
    global _mode
    button_name, x, y = button_map[button.pin.number]
    r = 0
    g = 255
    b = 0
    i = 0
    _text.stop()
    command = ""
    params = ""

    if button_name == "Y":
        print('button Y')
        if _mode.isA(ModeEnum.EditPlayList):
            _mode.setWebradio()
            return
        else:
            command = "toggle"

    if button_name == "X":
        _mode.cycle(Status.getStatus())
        print('button X new mode ' + _mode.getValue())
        return

    elif button_name == "B":
        print('button B')
        if _mode.isA(ModeEnum.SysInfo):
            _dots.stop()
            _text.rainbow = True
            _text.start("Volumio is live at " + getNetworkIp())
            print(Status.getStatus())
            return
        elif _mode.isA(ModeEnum.EditPlayList):
            _playlist.addStatus(Status.getStatus())
            return
        elif _mode.isA(ModeEnum.Webradio) or Status.getStatus().s_service == "webradio" or Status.getStatus().s_service == "mpd":
            _mode.editPlaylist()
            return
        else:
            command = "prev"
        unicornhatmini.set_pixel(0, 1, r, g, b)
        unicornhatmini.set_pixel(0, 2, r, g, b)
        unicornhatmini.set_pixel(1, 1, r, g, b)
        unicornhatmini.set_pixel(1, 2, r, g, b)
        unicornhatmini.show()
    elif button_name == "A":
        print('button A')
        print(_mode.getValue())
        print(Status.getStatus().s_status)
        if _mode.isA(ModeEnum.EditPlayList):
            _playlist.delStatus(Status.getStatus())
            _text.dotext("del")
            return
        elif _mode.isA(ModeEnum.Webradio) or Status.getStatus().s_service== "webradio" or Status.getStatus().s_service == "mpd":
            station = _playlist.next()
            params = station.__dict__
            command = "replaceAndPlay"
        elif _mode.isA(ModeEnum.EditPlayList):
            _playlist.delStatus(Status.getStatus())
            return
        else:
            command = "next"

        unicornhatmini.set_pixel(0, 4, r, g, b)
        unicornhatmini.set_pixel(0, 5, r, g, b)
        unicornhatmini.set_pixel(1, 4, r, g, b)
        unicornhatmini.set_pixel(1, 5, r, g, b)
        unicornhatmini.show()

    print(command, params)
    socketIO.emit(command, params)


button_map = {5: ("A", 0, 0),  # Top Left
              6: ("B", 0, 6),  # Bottom Left
              16: ("X", 16, 0),  # Top Right
              24: ("Y", 16, 7)}  # Bottom Right

button_a = Button(5)
button_b = Button(6)
button_x = Button(16)
button_y = Button(24)


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")

    _thread.start_new_thread(run, ())


def on_connect():
    print('connect')
    return 'connected'


def on_push_state(*args):
    global status
    global _timer
    global _doDots
    global _debug
    global _dots
    global _mode

    status = Status(args[0])
    print("Volumio message ", status.s_status)
    Status.getStatus().dump()

    if status.s_status.find("stop") != -1:
        unicornhatmini.set_all(0, 0, 0)
        _dots.stop()
        _text.stop()
        display_stop()
    if status.s_status.find("pause") != -1:
        _text.stop()
        display_pause()
        _dots.pause()
    if status.s_status.find("play") != -1:
        if status.isAirPlay():
            _text.stop()
            airplayDrawing()
        elif status.isDLNA():
            _text.stop()
            _text.dotext("dlna",RGB(0,255,0) )
        else:
            _mode.set(status)

    return 'ok'


async def main():
    global _timer
    global _bitrateTimer
    try:
        button_a.when_pressed = pressed
        button_b.when_pressed = pressed
        button_x.when_pressed = pressed
        button_y.when_pressed = pressed
        result = socketIO.on('pushState', on_push_state)
        socketIO.on('connect', on_connect)
        time.sleep(2)
        _text.rainbow = True
        _dots.stop()
        _text.start("Volumio is live!")
        _bitrateTimer = threading.Timer(10, updateBitrate)
        _bitrateTimer.start()

    except KeyboardInterrupt:
        button_a.close()
        button_b.close()
        button_x.close()
        button_y.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    print("socketio wait")
    socketIO.wait()
