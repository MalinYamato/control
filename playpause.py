#!/usr/bin/env python3

import requests
import asyncio
import math
import _thread
import time
import sys
import threading
import socket
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


def set_pixels(u, row, r, g, b):
    for i in range(17):
        u.set_pixel(i, row, r, g, b)


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
        seek()
        self.doDots = True
        while self.do():
            await asyncio.sleep(1)
            self.add()
            for p in range(self.dots()):
                unicornhatmini.set_pixel(4 + p, 5, 255, 0, 0)
            unicornhatmini.show()
            if self.dots() > 8:
                seek()
                for p in range(self.dots()):
                    unicornhatmini.set_pixel(4 + p, 5, 0, 0, 0)
                self.reset()
        self.clear()

    def run(self):
        asyncio.run(_dots.loop())

    def start(self):
        if self.do():
            print("Already running, issue stop to to run it again!")
            return
        if self.timer.is_alive():
            self.timer.cancel()
        self.timer = threading.Timer(1, self.run)
        self.timer.start()


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


def reSeek():
    socketIO.emit('seek', seek_get_seconds())


class Text:
    def __init__(self):
        self._text = ""
        self._timer = threading.Timer(1, self.looptext)
        self._stop = True

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
        while not self._stop:
            for y in range(display_height):
                for x in range(display_width):
                    hue = (time.time() / 10.0) + (x / float(display_width * 2))
                    r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                    if image.getpixel((x + offset_x, y)) == 255:
                        unicornhatmini.set_pixel(x, y, 0, 100, 255)
                    else:
                        unicornhatmini.set_pixel(x, y, 0, 0, 0)

            offset_x += 1
            if offset_x + display_width > image.size[0]:
                offset_x = 0

            unicornhatmini.show()
            await asyncio.sleep(0.10)

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


_dots = Dots()
_text = Text()


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

    if len(text) == 1:
        offset_x = 11
    elif len(text) == 2:
        offset_x = 13
    elif len(text) == 3:
        offset_x = 14

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
    if samplerate.find("193") != -1:
        unicornhatmini.set_pixel(0, y, r, g, b)
        unicornhatmini.set_pixel(1, y, r, g, b)
        unicornhatmini.set_pixel(2, y, r, g, b)
        unicornhatmini.set_pixel(3, y, r, g, b)
    if samplerate.find("384") != -1:
        unicornhatmini.set_pixel(0, y, 100, 100, 100)
        unicornhatmini.set_pixel(1, y, 100, 100, 100)
        unicornhatmini.set_pixel(2, y, 100, 100, 100)
        unicornhatmini.set_pixel(3, y, 100, 100, 100)
        unicornhatmini.set_pixel(4, y, 100, 100, 100)


def display_play(sr, bd):
    bitdepth(unicornhatmini, bd)
    samplerate(unicornhatmini, sr)
    unicornhatmini.set_pixel(7, 5, 0, 0, 0)
    unicornhatmini.set_pixel(7, 6, 0, 0, 0)
    unicornhatmini.set_pixel(9, 5, 0, 0, 0)
    unicornhatmini.set_pixel(9, 6, 0, 0, 0)


def display_pause():
    r = 255
    g = 0
    b = 0
    unicornhatmini.set_pixel(14, 1, r, g, b)
    unicornhatmini.set_pixel(14, 2, r, g, b)
    unicornhatmini.set_pixel(16, 1, r, g, b)
    unicornhatmini.set_pixel(16, 2, r, g, b)

def display_stop():
    r = 255
    g = 0
    b = 0
    unicornhatmini.set_pixel(16, 1, r, g, b)
    unicornhatmini.set_pixel(16, 2, r, g, b)
    unicornhatmini.set_pixel(15, 1, r, g, b)
    unicornhatmini.set_pixel(15, 2, r, g, b)



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

    print(bitrate)
    return bitrate.split(' ')[0]

def pressed(button):
    global timer2
    global splash_origin, splash_time
    global _mode
    button_name, x, y = button_map[button.pin.number]
    url = ''
    r = 0
    g = 255
    b = 0
    i = 0
    global _debug
    global _stop_flow
    _text.stop()
    command = ""
    if button_name == "X":
        print('button X')
        command = "toggle"
        url = 'http://localhost:3000/api/v1/commands?cmd=toggle'
    if button_name == "Y":
        print('button Y')
        jres = requests.get('http://localhost:3000/api/v1/getState').json()
        if not _debug:
            _debug = True
            _dots.stop()
            res = jres["samplerate"].split(' ')[0] + "/" + jres["bitdepth"].split(' ')[0]
            if len(res) < 2:
                res = " "
            else:
                res = " " + res + " "
            _text.start(jres["title"] + " by " + jres["artist"] + res + getBitrate() + " bps ")
        else:
            _debug = False
            if jres["service"] == "webradio":
                title = jres["title"]
                if len(title) > 4:
                    _dots.stop()
                    _text.start(jres["title"] + " " + getBitrate() + " bps")
                else:
                    dotext(jres["title"])
            else:
                _text.stop()
                _dots.start()
                dotext(str(jres["position"]))
                display_play(jres["samplerate"], jres["bitdepth"])

    if button_name == "A":
        print('button A')
        if _debug:
            _text.stop()
            _text.start(getNetworkIp())
            return
        jres = requests.get('http://localhost:3000/api/v1/getState').json()
        if jres["service"] == "webradio":
            return
        command = "prev"
        url = 'http://localhost:3000/api/v1/commands?cmd=prev'
        unicornhatmini.set_pixel(0, 1, r, g, b)
        unicornhatmini.set_pixel(0, 2, r, g, b)
        unicornhatmini.set_pixel(1, 1, r, g, b)
        unicornhatmini.set_pixel(1, 2, r, g, b)
    if button_name == "B":
        print('button B')
        if jres["service"] == "webradio":
            return
        command = "next"
        url = 'http://localhost:3000/api/v1/commands?cmd=next'
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


def distance(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))


def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


async def statusChecker():
    statusCheck(True)


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


_block_messages = False


def on_push_state(*args):
    global status
    global title
    global artist
    global album
    global albumart
    global _timer
    global _doDots
    global _debug
    global _dots
    global _block_messages
    global _stop_flow
    print("message")

    if _block_messages:
        _block_messages = False
        return

    status = args[0]['status'].encode('ascii', 'ignore')
    title = str(args[0]['title'])  # .encode('ascii', 'ignore')
    albumart = args[0]['albumart'].encode('ascii', 'ignore')
    a_bitdepth = str(args[0]['bitdepth'])
    a_samplerate = str(args[0]['samplerate'])
    a_bitrate = None
    if "bitrate" in args[0]:
        a_bitrate = args[0]['bitrate']
    if a_bitrate is None:
        a_bitrate = getBitrate()
    a_bitrate = a_bitrate.split(' ')[0]

    a_position = str(args[0]['position'])
    s_status = args[0]['status']
    s_debug = args[0]
    print(s_debug)


    if s_status.find("stop") != -1:
        unicornhatmini.set_all(0, 0, 0)
        _dots.stop()
        _text.stop()
        #dotext(a_position)
        display_stop()
    if s_status.find("pause") != -1:
        _dots.pause()
        _text.stop()
        #dotext(a_position)
        display_pause()
    if s_status.find("play") != -1:
        #unicornhatmini.set_all(0, 0, 0)
        _text.stop()
        _dots.start()
        if args[0]["service"] == "webradio":
            dotext(title)
        else:
            dotext(a_position)
            print(args[0])
            display_play(a_samplerate, a_bitdepth)
    unicornhatmini.show()
    return 'ok'


async def main():
    global _timer
    try:
        button_a.when_pressed = pressed
        button_b.when_pressed = pressed
        button_x.when_pressed = pressed
        button_y.when_pressed = pressed

        result = socketIO.on('pushState', on_push_state)
        socketIO.on('connect', on_connect)
        time.sleep(2)
        _deubg = False
        _text.start("Volumio " + getNetworkIp())

    except KeyboardInterrupt:
        button_a.close()
        button_b.close()
        button_x.close()
        button_y.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    print("socketio wait")
    socketIO.wait()
