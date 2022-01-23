#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button
from unicornhatmini import UnicornHATMini
from colorsys import hsv_to_rgb
from Settings import Settings
from Status import Status
from Color import RGB


class Draw:
    def __init__(self, u: UnicornHATMini, settings: Settings):
        self._settings = settings
        self.unicron = u
        self._samplerates = ["44.1", "48", "88.2", "96", "192", "384"]
        self._bitdepth = ["16", "24", "32"]

    def set_pixel(self, x, y, rgb: RGB):
        self.unicron.set_pixel(x, y, rgb.r, rgb.g, rgb.b)

    def flash(self):
        self.unicron.set_all(255,255,255)
        self.unicron.show()

    def radio(self):
        x = 5
        y = 1
        rgb = self._settings.get_airplayColor()

        self.unicron.set_all(0, 0, 0)

        self.set_pixel(x + 3, y + 2, rgb)
        self.set_pixel(x + 3, y + 3, rgb)

        self.set_pixel(x + 3, y + 1, rgb)
        self.set_pixel(x + 2, y + 2, rgb)
        self.set_pixel(x + 4, y + 2, rgb)

        self.set_pixel(x + 3, y + 4, rgb)
        self.set_pixel(x + 3, y + 5, rgb)

        self.set_pixel(x +1 , y   , rgb)
        self.set_pixel(x  , y + 1, rgb)
        self.set_pixel(x  , y + 2, rgb)
        self.set_pixel(x  , y + 3, rgb)
        self.set_pixel(x +1 , y + 4, rgb)

        self.set_pixel(x - 1, y -1, rgb)
        self.set_pixel(x - 2 , y + 0, rgb)
        self.set_pixel(x - 2 , y + 1, rgb)
        self.set_pixel(x - 2,  y + 2, rgb)
        self.set_pixel(x - 2,  y + 3, rgb)
        self.set_pixel(x - 2,  y + 4, rgb)
        self.set_pixel(x - 1, y  + 5, rgb)

        self.set_pixel(x + 5,  y , rgb)
        self.set_pixel(x + 6 , y + 1, rgb)
        self.set_pixel(x + 6 , y + 2, rgb)
        self.set_pixel(x + 6 , y + 3, rgb)
        self.set_pixel(x + 5, y +4 , rgb)

        self.set_pixel(x + 7 , y -1 , rgb)
        self.set_pixel(x + 8 , y + 0, rgb)
        self.set_pixel(x + 8 , y + 1, rgb)
        self.set_pixel(x + 8,  y + 2, rgb)
        self.set_pixel(x + 8,  y + 3, rgb)
        self.set_pixel(x + 8,  y + 4, rgb)
        self.set_pixel(x + 7,  y + 5, rgb)


        self.unicron.show()

    def sun(self):

        x = 5
        y = 1
        rgb = RGB(255, 255, 0)

        self.unicron.set_all(0, 0, 0)

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
        self.unicron.show()

    def airplayDrawing(self):
        rgb = self._settings.get_airplayColor()
        xo = 3
        xd = 10
        self.unicron.set_all(0, 0, 0)
        self.unicron.set_brightness(self._settings.get_brightness())
        for x in range(xd):
            self.set_pixel(xo + x, 1, rgb)
        for y in range(4):
            self.set_pixel(xo, y + 1, rgb)
        for y in range(4):
            self.set_pixel(xo + xd, y + 1, rgb)
        self.set_pixel(xo + 1, 4, rgb)
        self.set_pixel(xo + xd - 1, 4, rgb)
        for x in range(5):
            self.set_pixel(xo + 3 + x, 5, rgb)
        for x in range(3):
            self.set_pixel(xo + 4 + x, 4, rgb)
        self.set_pixel(xo + 5, 3, rgb)
        self.unicron.show()

    def samplerate(self, samplerate):
        y = 5

        for i in range(len(self._samplerates)):
            if samplerate.find(self._samplerates[i]) != -1:
                for dots in range(i+1):
                    self.set_pixel(dots, y, self._settings.get_resolutionColor())


    def bitdepth(self, bitdepth):
        y = 5
        xd = 16
        for i in range(len(self._bitdepth)):
            if bitdepth.find(self._bitdepth[i]) != -1:
                for dots in range(i+1):
                    self.set_pixel(xd - dots, y, self._settings.get_resolutionColor())


    def display_play(self, status):
        self.bitdepth(status.s_bitdepth)
        self.samplerate(status.s_samplerate)
        self.set_pixel(7, 5, RGB())
        self.set_pixel(7, 6, RGB())
        self.set_pixel(9, 5, RGB())
        self.set_pixel(9, 6, RGB())
        print("play")
        self.unicron.show()

    def display_pause(self):
        rgb = self._settings.get_stopColor()
        self.set_pixel(14, 1, rgb)
        self.set_pixel(14, 2, rgb)
        self.set_pixel(16, 1, rgb)
        self.set_pixel(16, 2, rgb)
        self.unicron.show()

    def display_stop(self):
        rgb = self._settings.get_stopColor()
        self.unicron.set_all(0, 0, 0)

        self.set_pixel(7, 2, rgb)
        self.set_pixel(8, 2, rgb)
        self.set_pixel(9, 2, rgb)
        self.set_pixel(7, 3, rgb)
        self.set_pixel(8, 3, rgb)
        self.set_pixel(9, 3, rgb)
        self.set_pixel(7, 4, rgb)
        self.set_pixel(8, 4, rgb)
        self.set_pixel(9, 4, rgb)
        self.unicron.show()
