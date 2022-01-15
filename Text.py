#!/usr/bin/env python3

import asyncio
import time
import sys
import threading
from PIL import Image, ImageDraw, ImageFont
from colorsys import hsv_to_rgb

class Text:
    def __init__(self, u):
        self.unicorn = u
        self.loops = -1
        self._text = ""
        self._timer = threading.Timer(1, self.looptext)
        self._stop = True
        self.rainbow = False

    async def textFlow(self):
        rotation = 180
        if len(sys.argv) > 1:
            try:
                rotation = int(sys.argv[1])
            except ValueError:
                print("Usage: {} <rotation>".format(sys.argv[0]))
                sys.exit(1)

        self.unicorn.set_rotation(rotation)
        display_width, display_height = self.unicorn.get_shape()
        self.unicorn.set_brightness(0.1)
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
                            self.unicorn.set_pixel(x, y, r, g, b)
                        else:
                            self.unicorn.set_pixel(x, y, 0, 100, 255)

                    else:
                        self.unicorn.set_pixel(x, y, 0, 0, 0)

            offset_x += 1
            if offset_x + display_width > image.size[0]:
                offset_x = 0

            self.unicorn.show()
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

    def dotext(self, text):
        self.stop()
        rotation = 180
        if len(sys.argv) > 1:
            try:
                rotation = int(sys.argv[1])
            except ValueError:
                print("Usage: {} <rotation>".format(sys.argv[0]))
                sys.exit(1)

        if text is None:
            print("a None value, returning")
            return False
        self.unicorn.set_rotation(rotation)
        display_width, display_height = self.unicorn.get_shape()
        self.unicorn.set_brightness(0.1)
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
                    self.unicorn.set_pixel(x, y, 255, g, b)
                else:
                    self.unicorn.set_pixel(x, y, 0, 0, 0)

        offset_x += 0
        if offset_x + display_width > image.size[0]:
            offset_x = 0
        self.unicorn.show()