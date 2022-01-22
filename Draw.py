#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from unicornhatmini import UnicornHATMini
from colorsys import hsv_to_rgb
from Settings import Settings
from Status import Status


class RGB:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    @classmethod
    def getDefault(self):
        return RGB(0, 184, 230)


class Draw:
    def __init__(self, u: UnicornHATMini, settings: Settings):
        self._settings = settings
        self.unicron = u
        self._samplerates = ["44", "48", "88.2", "96", "192", "384"]
        self._bitdepth = ["16", "24", "32"]
        self.rgb = RGB(0, 0, 255)

    def set_pixel(self, x, y, rgb: RGB):
        self.unicron.set_pixel(x, y, rgb.r, rgb.g, rgb.b)

    def flash(self):
        self.unicron.set_all(255,255,255)
        self.unicron.show()

    def sun(self):
        u = self.unicron
        rgb = RGB(255, 255, 0)
        u.set_all(0, 0, 0)
        x = 5
        y = 1
        self.set_pixel(x + 2, y + 1, rgb)
        self.set_pixel(x + 3, y + 1, rgb)
        self.set_pixel(x + 4, y + 1, rgb)

        self.set_pixel(x , y + 2, rgb)
        self.set_pixel(x + 1, y + 2, rgb)
        self.set_pixel(x + 2, y + 2, rgb)
        self.set_pixel(x + 3, y + 2, rgb)
        self.set_pixel(x + 4, y + 2, rgb)
        self.set_pixel(x + 5, y + 2, rgb)
        self.set_pixel(x + 6, y + 2, rgb)

        self.set_pixel(x + 3, y -1 , rgb)
        self.set_pixel(x + 3, y ,  rgb)
        self.set_pixel(x + 3, y + 4, rgb)
        self.set_pixel(x + 3, y + 5, rgb)

        self.set_pixel(x + 2, y + 3, rgb)
        self.set_pixel(x + 3, y + 3, rgb)
        self.set_pixel(x + 4, y + 3, rgb)

        self.set_pixel(x, y - 1, rgb)
        self.set_pixel(x+1, y, rgb)

        self.set_pixel(x, y + 5, rgb)
        self.set_pixel(x+1, y + 4, rgb)

        self.set_pixel(x + 6, y - 1, rgb)
        self.set_pixel(x + 5, y, rgb)

        self.set_pixel(x + 5, y + 4, rgb)
        self.set_pixel(x + 6, y + 5, rgb)
        u.show()

    def airplayDrawing(self):
        u = self.unicron
        rgb = RGB(0, 184, 230)
        xo = 3
        xd = 10
        u.set_all(0, 0, 0)
        u.set_brightness(self._settings.get_brightness())
        for x in range(xd):
            u.set_pixel(xo + x, 1, rgb.r, rgb.g, rgb.b)
        for y in range(4):
            u.set_pixel(xo, y + 1, rgb.r, rgb.g, rgb.b)
        for y in range(4):
            u.set_pixel(xo + xd, y + 1, rgb.r, rgb.g, rgb.b)
        u.set_pixel(xo + 1, 4, rgb.r, rgb.g, rgb.b)
        u.set_pixel(xo + xd - 1, 4, rgb.r, rgb.g, rgb.b)
        for x in range(5):
            u.set_pixel(xo + 3 + x, 5, rgb.r, rgb.g, rgb.b)
        for x in range(3):
            u.set_pixel(xo + 4 + x, 4, rgb.r, rgb.g, rgb.b)
        u.set_pixel(xo + 5, 3, rgb.r, rgb.g, rgb.b)
        u.show()

    def samplerate(self, samplerate):
        y = 5
        for i in range(len(self._samplerates)):
            if samplerate.find(self._samplerates[i]) != -1:
                for dots in range(i):
                    self.set_pixel(dots, y, self.rgb)
        self.unicron.show()

    def bitdepth(self, bitdepth):
        y = 5
        xd = 16
        for i in range(len(self._bitdepth)):
            if bitdepth.find(self._bitdepth[i]) != -1:
                for dots in range(i):
                    self.set_pixel(xd + dots, y, self.rgb)
        self.unicron.show()

    def display_play(self, status):
        self.bitdepth(status.s_bitdepth)
        self.samplerate(status.s_samplerate)
        self.unicron.set_pixel(7, 5, 0, 0, 0)
        self.unicron.set_pixel(7, 6, 0, 0, 0)
        self.unicron.set_pixel(9, 5, 0, 0, 0)
        self.unicron.set_pixel(9, 6, 0, 0, 0)
        self.unicron.show()

    def display_pause(self):
        r = 255
        g = 0
        b = 0
        self.unicron.set_pixel(14, 1, r, g, b)
        self.unicron.set_pixel(14, 2, r, g, b)
        self.unicron.set_pixel(16, 1, r, g, b)
        self.unicron.set_pixel(16, 2, r, g, b)
        self.unicron.show()

    def display_stop(self):
        r = 255
        g = 0
        b = 0
        self.unicron.set_all(0, 0, 0)

        self.unicron.set_pixel(7, 2, r, g, b)
        self.unicron.set_pixel(8, 2, r, g, b)
        self.unicron.set_pixel(9, 2, r, g, b)
        self.unicron.set_pixel(7, 3, r, g, b)
        self.unicron.set_pixel(8, 3, r, g, b)
        self.unicron.set_pixel(9, 3, r, g, b)
        self.unicron.set_pixel(7, 4, r, g, b)
        self.unicron.set_pixel(8, 4, r, g, b)
        self.unicron.set_pixel(9, 4, r, g, b)
        self.unicron.show()
