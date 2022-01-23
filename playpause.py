#!/usr/bin/env python3

# Copyright 2022 Malin Yamato --  All rights reserved.
# https://github.com/MalinYamato
#
# MIT License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Rakuen. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import time

import requests
import asyncio
import math
import _thread
import threading
import socket
import json
from enum import Enum, IntEnum

import Text
from Text import RGB
import PlayList
import Dots

from socketIO_client import SocketIO
from gpiozero import Button
from unicornhatmini import UnicornHATMini
from Status import *
from Draw import *
from Util import *


def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


class SystemMode(IntEnum):
    label = 1
    ip = 2
    brightness = 3
    flash = 4
    Last = 5
    Off = 6


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


class Mode:
    def __init__(self):
        self._modeEnum = ModeEnum.Position
        self._sysMode = SystemMode.ip
        self._status = Status.getStatus()

    def cycleSystemMode(self):
        self._sysMode = self._sysMode + 1
        if self._sysMode >= SystemMode.Last:
            self._sysMode = 1
        if self._sysMode == SystemMode.label:
            _text.dotext("sys")
        elif self._sysMode == SystemMode.ip:
            _text.start(getNetworkIp())
        elif self._sysMode == SystemMode.brightness:
            _text.stop()
            _draw.sun()
        elif self._sysMode == SystemMode.flash:
            _draw.flash()

    def cycle(self, aStatus):
        self._status = aStatus
        self._modeEnum = 1 + int(self._modeEnum)
        if self._modeEnum >= ModeEnum.Last:
            self._modeEnum = 1
        if self._modeEnum != ModeEnum.SysInfo:
            self._sysMode = SystemMode.Off
        if self._modeEnum == ModeEnum.Webradio:
            _draw.radio()
            return
        self.set(self._status)

    def set(self, aStatus):
        self._status = aStatus
        if self._status.s_trackType == "airplay" and self._modeEnum != ModeEnum.SysInfo and self._modeEnum != ModeEnum.Webradio:
            _draw.airplayDrawing()
            return
        if (self._status.s_status == "stop" or self._status.s_status == "") and self._modeEnum != ModeEnum.SysInfo:
            _text.dotext("M" + str(self._modeEnum))
            return
        elif self._modeEnum == ModeEnum.Position:
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
        if enum == self._modeEnum:
            return True
        if enum == self._sysMode:
            return True
        return False

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
            _draw.display_play(self._status)

    def setBitrate(self):
        if self._status.isFLAC():
            _text.dotext("FLAC")
        else:
            _text.dotext(self._status.s_bitrate)
        _draw.display_play(self._status)

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
                    " by " + self._status.s_artist + res + getBitrate(socketIO) + " bps " + self._status.s_service)

    def setSysInfo(self):
        _text.stop()
        _dots.stop()
        _text.rainbow = False
        _text.dotext("sys")

    def editPlaylist(self):
        self._modeEnum = ModeEnum.EditPlayList
        _text.stop()
        _dots.stop()
        _text.dotext("+O-")

    def setWebradio(self):
        _dots.stop()
        self._modeEnum = ModeEnum.Webradio
        _text.dotext(self._status.s_title)

    def dump(self):
        print("Mode :", self.getValue())
        Status.getStatus().dump()

    @property
    def modeEnum(self):
        return self._modeEnum


_playlist = PlayList.Playlist()
unicornhatmini = UnicornHATMini()
unicornhatmini.set_rotation(180)
width, height = unicornhatmini.get_shape()
socketIO = SocketIO('localhost', 3000)
status = 'unknown'
_timer = None
_bitrateTimer = None
_settings = Settings()
_dots = Dots.Dots(unicornhatmini, _settings)
_text = Text.Text(unicornhatmini, _settings)
_draw = Draw(unicornhatmini, _settings)
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
                # _dots.start()
            else:
                bitrate = getBitrate(socketIO)
                print("not flack")
                if bitrate != _bitrate:
                    _bitrate = bitrate
                    _dots.seek()
                    _text.dotext(_bitrate)
            _draw.display_play(stat)
        _bitrateTimer = threading.Timer(10, updateBitrate)
        _bitrateTimer.start()


def pressed(button):
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
        elif _mode.isA(ModeEnum.SysInfo):
            _mode.cycleSystemMode()
            return
        else:
            command = "toggle"

    if button_name == "X":
        _mode.cycle(Status.getStatus())
        print('button X new mode ' + _mode.getValue())
        return

    elif button_name == "B":
        print('button B')
        if _mode.isA(ModeEnum.SysInfo) and _mode.isA(SystemMode.brightness):
            _settings.increaes()
            unicornhatmini.set_brightness(_settings.get_brightness())
            return
        elif _mode.isA(SystemMode.flash):
            unicornhatmini.set_brightness(_settings.get_brightness())
            return
        if _mode.isA(ModeEnum.SysInfo):
            _dots.stop()
            _text.rainbow = True
            _text.start("Volumio is live at " + getNetworkIp())
            return
        elif _mode.isA(ModeEnum.EditPlayList):
            _playlist.addStatus(Status.getStatus())
            return
        elif _mode.isA(
                ModeEnum.Webradio) or Status.getStatus().s_service == "webradio" or Status.getStatus().s_service == "mpd":
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
        if _mode.isA(ModeEnum.SysInfo) and _mode.isA(SystemMode.brightness):
            _settings.decrease()
            unicornhatmini.set_brightness(_settings.get_brightness())
            return
        elif _mode.isA(ModeEnum.SysInfo) and _mode.isA(SystemMode.flash):
            unicornhatmini.set_brightness(1.0)
            return
        if _mode.isA(ModeEnum.EditPlayList):
            _playlist.delStatus(Status.getStatus())
            _text.dotext("del")
            return
        elif _mode.isA(
                ModeEnum.Webradio) or Status.getStatus().s_service == "webradio" or Status.getStatus().s_service == "mpd":
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
    global _dots
    global _mode

    status = Status(args[0])
    print("Volumio message ", status.s_status)
    Status.getStatus().dump()

    if status.s_status.find("stop") != -1:
        unicornhatmini.set_all(0, 0, 0)
        _dots.stop()
        _text.stop()
        _draw.display_stop()
    if status.s_status.find("pause") != -1:
        _text.stop()
        _draw.display_pause()
        _dots.pause()
    if status.s_status.find("play") != -1:
        if status.isAirPlay():
            _text.stop()
            _draw.airplayDrawing()
        elif status.isDLNA():
            _text.stop()
            _text.dotext("dlna", RGB(0, 255, 0))
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

        _draw.radio()
        time.sleep(10)

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
