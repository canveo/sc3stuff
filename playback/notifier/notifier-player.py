from __future__ import print_function

import sys, os, time, tempfile
from seiscomp3 import Core, Client, DataModel, Communication, IO, Logging, Utils

class NotifierPlayer(Client.Application):

    def __init__(self, argc, argv):
        Client.Application.__init__(self, argc, argv)
        self.setMessagingEnabled(False)
        self.setDatabaseEnabled(False, False)
        self._startTime = self._endTime = None
        self._xmlFileName = None
        self.speed = 1

    def createCommandLineDescription(self):
        Client.Application.createCommandLineDescription(self)
        self.commandline().addGroup("Play")
        self.commandline().addStringOption("Play", "begin", "specify start of time window")
        self.commandline().addStringOption("Play", "end", "specify end of time window")
        self.commandline().addStringOption("Play", "speed", "specify speed factor")
        self.commandline().addGroup("Input")
        self.commandline().addStringOption("Input", "xml-file", "specify xml file")

    def init(self):
        if not Client.Application.init(self):
            return False

        try:    start = self.commandline().optionString("begin")
        except: start = None

        try:    end = self.commandline().optionString("end")
        except: end = None

        try:    self._xmlFileName = self.commandline().optionString("xml-file")
        except: pass

        try:
            self.speed = self.commandline().optionString("speed")
            if self.speed == "0":
                self.speed = None
            else:
                self.speed = float(self.speed)
        except: self.speed = 1

        if start:
            self._startTime = Core.Time.GMT()
            if self._startTime.fromString(start, "%F %T") == False:
                Logging.error("Wrong 'begin' format")
                return False
        if end:
            self._endTime = Core.Time.GMT()
            if self._endTime.fromString(end, "%F %T") == False:
                Logging.error("Wrong 'end' format")
                return False

        return True

    def addObject(self, parent, obj):
        Logging.debug("addObject parent=%s" % parent)

    def updateObject(self, parent, obj):
        Logging.debug("updateObject parent=%s" % parent)

    def _readNotifierMessageFromXML(self, xml):
        b = Utils.stringToStreambuf(xml)
        ar = IO.XMLArchive(b)
        obj = ar.readObject()
        if obj is None:
            raise TypeError, "got invalid xml"
        nm  = DataModel.NotifierMessage.Cast(obj)
        if nm is None:
            raise TypeError, self._xmlFile + ": no NotifierMessage object found"
        return nm

    def handleMessage(self, msg):
        Logging.debug("handleMessage %s" % str(msg))
        Client.Application.handleMessage(self, msg)

    def run(self):
        if not self._xmlFileName:
            return False

        Logging.debug("input file is %s" % self._xmlFileName)
        self._xmlFile = file(self._xmlFileName)

        while True:
            while True:
                line = self._xmlFile.readline().strip()
                if not line:
                    return True
                if line[0] == "#":
                    break
            print (line)
            try:
                sharp, nbytes, timestamp = line.split()
                nbytes = int(nbytes)
                assert sharp[0] == "#"
                xml = self._xmlFile.read(nbytes)
                print(xml)
            except:
                Logging.error("ERROR")
                break

            msg = self._readNotifierMessageFromXML(xml)
            self.handleMessage(msg)

        return True

app = NotifierPlayer(len(sys.argv), sys.argv)
sys.exit(app())
