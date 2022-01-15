#!/usr/bin/env python3
import requests
import asyncio
import threading

def set_pixels(u, row, r, g, b):
    for i in range(17):
        u.set_pixel(i, row, r, g, b)

def seek_get_seconds():
    jres = requests.get('http://localhost:3000/api/v1/getState').json()
    return int(jres["seek"] / 1000)

class Dots:
    def __init__(self, u):
        self._unicorn = u
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
            self._unicorn.set_pixel(3 + p, 5, 0, 0, 0)

    async def loop(self):
        print("dot")
        # seek()
        self.doDots = True
        while self.do():
            self.add()
            for p in range(self.dots()):
                self._unicorn.set_pixel(4 + p, 5, 255, 0, 0)
            self._unicorn.show()
            if self.dots() > 8:
                self.seek()
                for p in range(self.dots()):
                    self._unicorn.set_pixel(4 + p, 5, 0, 0, 0)
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
            set_pixels(self._unicorn, 6, 255, 0, 0)
            dd = d - 17
            if dd > 16:
                set_pixels(self._unicorn, 6, 102, 0, 153)
            else:
                for p in range(dd):
                    self._unicorn.set_pixel(p, 6, 102, 0, 153)
        else:
            for x in range(d):
                self._unicorn.set_pixel(x, 6, 255, 0, 0)