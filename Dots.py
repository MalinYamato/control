#!/usr/bin/env python3
import requests
import asyncio
import threading
from Settings import Settings
from Util import *
from Color import RGB

def set_pixels(u, row, rgb):
    for i in range(17):
        u.set_pixel(i, row, rgb.r, rgb.g, rgb.b)

class Dots:
    def __init__(self, u, s: Settings):
        self.brightness = s.get_brightness()
        self._unicorn = u
        self.doDots = False
        self.i = 0
        self._settings = s
        self.timer = threading.Timer(1, self.run)

    def set_pixel(self,x, y, rgb: RGB):
        self._unicorn.set_pixel(x, y, rgb.r, rgb.g, rgb.b)

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
            self.set_pixel(3 + p, 5, RGB())

    async def loop(self):
        print("dot")
        # seek()
        self.doDots = True
        while self.do():
            self.add()
            for p in range(self.dots()):
                self.set_pixel(5 + p, 5, self._settings.get_dotColor())
            self._unicorn.show()
            if self.dots() > 6:
                self.seek()
                for p in range(self.dots()):
                    self.set_pixel(5 + p, 5, RGB())
                self.reset()
            await asyncio.sleep(1)

    def run(self):
        asyncio.run(self.loop())

    def start(self):
        self.seek()
        if self.do():
            print("Already running, issue stop to to run it again!")
            return
        if self.timer.is_alive():
            self.timer.cancel()
        self.timer = threading.Timer(0.1, self.run)
        self.timer.start()

    def seek(self):
        d = int(seek_get_seconds() / 15)
        if d > 16:
            set_pixels(self._unicorn, 6, self._settings.get_dotColor())
            dd = d - 17
            if dd > 16:
                set_pixels(self._unicorn, 6, RGB(102, 0, 153))
            else:
                for p in range(dd):
                    self.set_pixel(p, 6, RGB(102, 0, 153))
        else:
            for x in range(d):
                rgb = self._settings.get_dotColor()
                self.set_pixel(x, 6, rgb )