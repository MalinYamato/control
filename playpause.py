#!/usr/bin/env python3

import requests
import asyncio
import math
import _thread
import time
import sys
import threading
import socket
from enum import Enum, IntEnum
from dataclasses import dataclass

import setuptools
from socketIO_client import SocketIO, LoggingNamespace
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from unicornhatmini import UnicornHATMini
from colorsys import hsv_to_rgb

unicornhatmini = UnicornHATMini()
unicornhatmini.set_brightness(0.5)
unicornhatmini.set_rotation(0)
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


#################################################################

def distance(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))


def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


def set_pixels(u, row, r, g, b):
    for i in range(17):
        u.set_pixel(i, row, r, g, b)


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

def seek_get_seconds():
    jres = requests.get('http://localhost:3000/api/v1/getState').json()
    return int(jres["seek"] / 1000)


def seek():
    d = int(seek_get_seconds() / 15)
    if d > 16:
        set_pixels(unicornhatmini, 6, 255, 0, 0)
        dd = d - 17
        if dd > 16:
            set_pixels(unicornhatmini, 6, 102, 0, 153)
        else:
            for p in range(dd):
                unicornhatmini.set_pixel(p, 6, 102, 0, 153)
    else:
        for x in range(d):
            unicornhatmini.set_pixel(x, 6, 255, 0, 0)


_seconds = 0


def reSeek():
    global _seconds
    seconds = int(time.time())
    diff = int(seconds - _seconds)
    print(diff)
    if _seconds == 0:
        _seconds = seconds
    if diff > 1:
        print("Do seek to current position " + str(diff))
        socketIO.emit('seek', seek_get_seconds())
        _seconds = seconds
    else:
        print("diff less than 1")


#################################################################################

class Dots:
    def __init__(self):
        self.doDots = False
        self.i = 0
        self.timer = threading.Timer(1, self.run)

    def reset(self):
        self.i = 0

    def stop(self):
        self.i = 0
        self.pause()
        self.clear()

    def pause(self):
        self.doDots = False
        self.timer.cancel()

    def do(self):
        return self.doDots

    def add(self):
        self.i = self.i + 1

    def dots(self):
        return self.i

    def clear(self):
        for p in range(8):
            unicornhatmini.set_pixel(3 + p, 5, 0, 0, 0)

    async def loop(self):
        print("dot")
        #seek()
        self.doDots = True
        while self.do():
            self.add()
            for p in range(self.dots()):
                unicornhatmini.set_pixel(4 + p, 5, 255, 0, 0)
            unicornhatmini.show()
            if self.dots() > 8:
                seek()
                for p in range(self.dots()):
                    unicornhatmini.set_pixel(4 + p, 5, 0, 0, 0)
                self.reset()
            await asyncio.sleep(1)

    def run(self):
        asyncio.run(_dots.loop())

    def start(self):
        seek()
        if self.do():
            print("Already running, issue stop to to run it again!")
            return
        if self.timer.is_alive():
            self.timer.cancel()
        self.timer = threading.Timer(0.1, self.run)
        self.timer.start()


class Text:
    def __init__(self):
        self.loops = -1
        self._text = ""
        self._timer = threading.Timer(1, self.looptext)
        self._stop = True
        self.rainbow = False

    async def textFlow(self):
        rotation = 0
        if len(sys.argv) > 1:
            try:
                rotation = int(sys.argv[1])
            except ValueError:
                print("Usage: {} <rotation>".format(sys.argv[0]))
                sys.exit(1)

        unicornhatmini.set_rotation(rotation)
        display_width, display_height = unicornhatmini.get_shape()
        unicornhatmini.set_brightness(0.1)
        font = ImageFont.truetype("5x7.ttf", 8)
        text_width, text_height = font.getsize(self._text)
        image = Image.new('P', (text_width + display_width + display_width, display_height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((display_width, -1), self._text, font=font, fill=255)

        offset_x = 0
        loops = 1

        while not self._stop:
            if self.loops != -1 and loops >= self.loops:
                self._stop = True
            for y in range(display_height):
                for x in range(display_width):
                    hue = (time.time() / 10.0) + (x / float(display_width * 2))
                    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                    if image.getpixel((x + offset_x, y)) == 255:
                        if self.rainbow:
                            unicornhatmini.set_pixel(x, y, r, g, b)
                        else:
                            unicornhatmini.set_pixel(x, y, 0, 100, 255)

                    else:
                        unicornhatmini.set_pixel(x, y, 0, 0, 0)

            offset_x += 1
            if offset_x + display_width > image.size[0]:
                offset_x = 0

            unicornhatmini.show()
            await asyncio.sleep(0.10)
            loops = loops + 1
        self.loops = -1

    def looptext(self):
        asyncio.run(self.textFlow())

    def start(self, text):
        if self.stop is False:
            print(" cannot start twice ")
            return
        self.stop()
        self._text = text
        self._timer = threading.Timer(0.1, self.looptext)
        self._timer.start()
        self._stop = False

    def stop(self):
        self._stop = True
        if self._timer.is_alive():
            print("thread cancel")
            self._timer.cancel()
        time.sleep(0.2)


class ModeEnum(IntEnum):
    Position = 1
    BitRate = 2
    DetailFlow = 3
    SysInfo = 4
    EditPlayList = 5
    Last = 6

    def describe(self):
        return self.name


class Status:
    def __init__(self, status):
        self.s_service = get(status, 'service')
        self.s_status = get(status, 'status')
        self.s_artist = get(status, 'artist')
        self.s_title = get(status, 'title')
        self.s_bitdepth = get(status, 'bitdepth')
        self.s_samplerate = get(status, 'samplerate')
        self.s_position = get(status, 'position')
        self.s_bitrate = get(status, 'bitrate')
        if self.s_bitrate == "":
            self.s_bitrate = getBitrate()
        self.s_bitrate = self.s_bitrate.split(' ')[0]

    @classmethod
    def getStatus(self):
        return requests.get('http://localhost:3000/api/v1/getState').json()

    def dump(self, aStatus):
        print(self.s_status, self.s_service, self.s_position, self.s_artist, self.s_title, self.s_bitrate,
              self.s_samplerate, self.s_bitdepth)
        print(aStatus)


class Mode:
    def __init__(self):
        self._modeEnum = ModeEnum.Position
        self._status = Status(Status.getStatus())

    def cycle(self, aStatus):
        self._status = aStatus
        self._modeEnum = 1 + int(self._modeEnum)
        if (self._modeEnum == ModeEnum.EditPlayList and self._status.s_service != "webradio") or self._modeEnum == ModeEnum.Last:
            self._modeEnum = 1
        self.set(self._status)

    def set(self, aStatus):
        self._status = aStatus
        if (self._status.s_status == "stop" or self._status.s_status == "") and self._modeEnum != ModeEnum.SysInfo:
            dotext("M" +  str( self._modeEnum))
            return
        if self._modeEnum == ModeEnum.BitRate:
            self.setBitrate()
        elif self._modeEnum == ModeEnum.Position:
            self.setPosition()
        elif self._modeEnum == ModeEnum.DetailFlow:
            self.setDetailFlow()
        elif self._modeEnum == ModeEnum.SysInfo:
            self.setSysInfo()
        elif self._modeEnum == ModeEnum.EditPlayList:
            self.editPlaylist()

    def isA(self, enum):
        return enum == self._modeEnum

    def getValue(self):
        return ModeEnum(self._modeEnum).describe()

    def setBitrate(self):
        _text.stop()
        dotext(self._status.s_bitrate)
        display_play(self._status)
        _dots.start()

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

    def setPosition(self):
        _text.stop()
        if self._status.s_service == "webradio":
            dotext(self._status.s_title)
        else:
            dotext(self._status.s_position)
            display_play(self._status)
            _dots.start()

    def setSysInfo(self):
        _text.stop()
        _dots.stop()
        _text.rainbow = False
        _text.start(getNetworkIp())

    def editPlaylist(self):
        _text.stop()
        _dots.stop()
        dotext("+0-")

    def dump(self):
        print("Mode :", self.getValue())
        self._status.dump(Status.getStatus())


_dots = Dots()
_text = Text()
_mode = Mode()

_bitrate = ""
def updateBitrate():
    global _bitrate
    global _bitrateTimer
    if _mode.isA(ModeEnum.BitRate):
        bitrate = getBitrate()
        if bitrate != _bitrate:
            _bitrate = bitrate
            dotext(_bitrate)
            seek()
    _bitrateTimer = threading.Timer(10, updateBitrate)
    _bitrateTimer.start()


def dotext(text):
    if text is None:
        print("a None value, returning")
        return False
    display_width, display_height = unicornhatmini.get_shape()
    unicornhatmini.set_brightness(0.1)
    font = ImageFont.truetype("5x7.ttf", 8)
    text_width, text_height = font.getsize(text)
    image = Image.new('P', (text_width + display_width + display_width, display_height), 0)
    draw = ImageDraw.Draw(image)
    draw.text((display_width, -1), text, font=font, fill=255)

    offset_x = 17

    text = text.split(' ')[0]

    if len(text) == 1:
        offset_x = 11
    elif len(text) == 2:
        offset_x = 13
    elif len(text) == 3:
        offset_x = 15

    for y in range(display_height):
        for x in range(display_width):
            atime = 1640879509  # time.time())
            hue = (atime / 10.0) + (1 / float(display_width * 2))
            r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
            if image.getpixel((x + offset_x, y)) == 255:
                unicornhatmini.set_pixel(x, y, 255, g, b)
            else:
                unicornhatmini.set_pixel(x, y, 0, 0, 0)

    offset_x += 0
    if offset_x + display_width > image.size[0]:
        offset_x = 0

    unicornhatmini.show()


def pressed(button):
    global splash_origin, splash_time
    global _mode
    button_name, x, y = button_map[button.pin.number]
    url = ''
    r = 0
    g = 255
    b = 0
    i = 0
    _text.stop()
    command = ""
    if button_name == "X":
        print('button X')
        command = "toggle"
    if button_name == "Y":
        _mode.cycle(Status(Status.getStatus()))
        print('button Y new mode ' + _mode.getValue())
        return

    if button_name == "A":
        print('button A')
        if _mode.isA(ModeEnum.EditPlayList):
            dotext("Add")
            return
        if Status.getStatus()["service"] == "webradio":
            return
        if _mode.isA(ModeEnum.SysInfo):
            _dots.stop()
            _text.rainbow = True
            _text.start("Volumio is live at " + getNetworkIp() )
            return

        command = "prev"
        unicornhatmini.set_pixel(0, 1, r, g, b)
        unicornhatmini.set_pixel(0, 2, r, g, b)
        unicornhatmini.set_pixel(1, 1, r, g, b)
        unicornhatmini.set_pixel(1, 2, r, g, b)
        unicornhatmini.show()
    if button_name == "B":
        print('button B')
        if _mode.isA(ModeEnum.EditPlayList):
            dotext("Del")
            return
        if Status.getStatus()["service"] == "webradio":
            return
        if Status.getStatus()["service"] == "webradio":
            dotext("Del")
            return

        command = "next"
        unicornhatmini.set_pixel(0, 4, r, g, b)
        unicornhatmini.set_pixel(0, 5, r, g, b)
        unicornhatmini.set_pixel(1, 4, r, g, b)
        unicornhatmini.set_pixel(1, 5, r, g, b)
        unicornhatmini.show()

    socketIO.emit(command, '')


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
