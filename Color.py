#!/usr/bin/env python3
class RGB:
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self.r = r
        self.g = g
        self.b = b

    @classmethod
    def getDefault(self):
        return RGB(0, 184, 230)
