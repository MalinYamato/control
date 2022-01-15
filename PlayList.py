#!/usr/bin/env python3

import pickle
import os

class Station:
    def __init__(self, title, uri):
        self.title = title
        self.service = "webradio"
        self.type = "webradio"
        self.uri = uri


class Playlist:
    def __init__(self):
        self.pos = 0
        self.stations = []
        self.readFile()

    def readFile(self):
        if os.path.isfile("playlist.txt"):
            with open('playlist.txt', 'rb') as file:
                self.stations = pickle.load(file)
        else:
            self.writeFile()

    def writeFile(self):
        with open('playlist.txt', 'wb') as file:
            pickle.dump(self.stations, file)

    def add(self, station):
        self.stations.append(station)

    def addStatus(self, stat):
        for i in range(len(self.stations)):
            if stat.s_title == self.stations[i].title:
                print("Playlist.add -- station alreaad added")
                return
        self.add(Station(stat.s_title, stat.s_uri))
        self.writeFile()

    def delStatus(self, stat):
        for i in range(len(self.stations)):
            if stat.s_title == self.stations[i].title:
                self.stations.pop(i)
                self.writeFile()
                return

        print("Playlist.del -- station did not exist ")

    def current(self):
        return self.stations[self.pos ]

    def next(self):
        self.pos = self.pos + 1
        if self.pos >= len(self.stations):
            self.pos = 0
        return self.stations[self.pos ]

    def prev(self):
        self.pos = self.pos - 1
        if self.pos < 0:
            self.pos = 0
        return self.stations[self.pos]
