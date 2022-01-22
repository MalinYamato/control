#!/usr/bin/env python3

import pickle
import os

class SettingsData:
    def __init__(self):
        self.brightness = 0.1

class Settings:
    def __init__(self):
        self._data = SettingsData()
        self.file = "settings.txt"
        self.readFile()
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

    def readFile(self):
        if os.path.isfile(self.file):
            with open(self.file, 'rb') as file:
                self._data = pickle.load(file)
        else:
            self.writeFile()

    def writeFile(self):
        with open(self.file, 'wb') as file:
            pickle.dump(self._data, file)