#!/usr/bin/env python3

import pickle
import os
import json
from json import JSONEncoder
from Color import RGB


class SettingsEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class SettingsData:
    def __init__(self, brightness: float = 0.1,
                 textColor: RGB = RGB(),
                 stopColor: RGB = RGB(),
                 airplayColor: RGB = RGB(),
                 dlnaColor: RGB = RGB(),
                 resolutionColor: RGB = RGB(),
                 dotColor: RGB = RGB() ):
        self.brightness = brightness
        self.textColor = textColor
        self.stopColor = stopColor
        self.airPlayColor = airplayColor
        self.dlnaColor = dlnaColor
        self.resolutionColor = resolutionColor
        self.dotColor = dotColor


class Settings:
    def __init__(self):
        self._data = SettingsData()
        self.file = "settings.json"
        self.readFile()

    def decodeRGB(self, obj, key):
        return  RGB(obj[key]['r'], obj[key]['g'], obj[key]['b'])

    def decode(self, obj):
        return SettingsData( obj['brightness'],
                            self.decodeRGB(obj, 'textColor'),
                            self.decodeRGB(obj, 'stopColor'),
                            self.decodeRGB(obj, 'airPlayColor'),
                            self.decodeRGB(obj, 'dlnaColor'),
                            self.decodeRGB(obj, 'resolutionColor'),
                            self.decodeRGB(obj, 'dotColor'))

    def increaes(self):
        self._data.brightness = self._data.brightness + 0.01
        self.writeFile()

    def decrease(self):
        self._data.brightness = self._data.brightness - 0.01
        self.writeFile()

    def get_brightness(self):
        return self._data.brightness

    def set_brightness(self, b):
        self._data.brightness = b
        self.writeFile()

    def get_textColor(self):
        return self._data.textColor

    def get_stopColor(self):
        return self._data.stopColor

    def get_airplayColor(self):
        return self._data.airPlayColor

    def get_dlnaColor(self):
        return self._data.dlnaColor

    def get_resolutionColor(self):
        return self._data.resolutionColor

    def get_dotColor(self):
        return self._data.dotColor

    def readFile(self):
        if os.path.isfile(self.file):
            with open(self.file, 'r') as file:
                data = json.loads(file.read())
                print(data)
                self._data = self.decode(data)
        else:
            self.writeFile()

    def writeFile(self):
        with open(self.file, 'w') as file:
            js = json.dumps(self._data, indent=4, cls=SettingsEncoder)
            file.write(js)
