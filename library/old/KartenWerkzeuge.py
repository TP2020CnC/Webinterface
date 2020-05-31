#
# Name: KartenWerkzeuge.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-20
# Letzte Änderung: 2020-05-20
#
# Die Werkzeuge enthalten verschiedene Konfigarationen und Hilfsfunktionen.
# Das Verzeichnis wird im Konstruktor der Klasse mitgegeben. Im Fromat: "foo/bar/verzeichnis/"
#

import struct
import colorsys


class Werkzeuge:
    def __init__(self, file_path):
        #
        # Farben
        #
        self.COLOR_FLOOR = (255, 255, 255, 32)
        self.COLOR_OBSTACLE_WEAK = (0, 0, 0, 255)
        self.COLOR_OBSTACLE_STRONG = (0, 255, 64, 255)
        self.COLOR_PATH = (255, 255, 255, 255)
        self.COLOR_NOGO_BORDER = (255, 0, 0)
        self.COLOR_NOGO_AREA = (255, 0, 0, 128)
        self.COLOR_BACKGROUND = (255, 0, 0, 0)
        self.COLOR_TEST_CLEAN = (153, 255, 255, 16)

        #
        # Konfiguration der Karte
        #
        self.FILE_PATH = file_path
        self.SCALE_FACTOR = 4
        self.CROP = False
        self.DRAW_PATH = True
        self.DRAW_NO_GO_AREAS = True

        #
        # Konfiguration des Pasers
        #
        self.DIMENSION_PIXELS = 1024
        self.DIMENSION_MM = 50 * 1024

        #
        # Schmutztoleranz und ausbreitungszerfall
        #
        self.PRIM_DECAY = 1.8
        self.SEC_DECAY = 1.4
        self.TOLERANCE = 60
#####################################################

####
    #
    # Farben von Hue zu RGB konvertieren
    #
    def HueToRGB(self, hue):
        buf = colorsys.hsv_to_rgb(hue / 360, 1, 1)
        return ((int)(buf[0] * 255), (int)(buf[1] * 255), (int)(buf[2] * 255), 255)
#####################################################

####
    #
    # Konvertieren der Kartenkoordinaten
    #
    def TransformCoords(self, coord, offset_from):
        coord /= 50
        coord -= offset_from
        coord *= self.SCALE_FACTOR
        return round(coord)
#####################################################

####
    #
    # Switch fuer Paser
    #
    def Switch(self, argument):
        switcher = {
            1: "CHARGER_LOCATION",
            2: "IMAGE",
            3: "PATH",
            4: "GOTO_PATH",
            5: "GOTO_PREDICTED_PATH",
            6: "CURRENTLY_CLEANED_ZONES",
            7: "GOTO_TARGET",
            8: "ROBOT_POSITION",
            9: "FORBIDDEN_ZONES",
            10: "VIRTUAL_WALLS",
            11: "CURRENTLY_CLEANED_BLOCKS",
            1024: "DIGEST"
        }
        return switcher.get(argument, "Invalid")
#####################################################

####
    #
    # Bytes auslesen
    #
    def GetBytes(self, bytes, offset, length):
        bytes.seek(offset, 0)
        b = bytes.read(length)
        return b
#####################################################

####
    #
    # Bytes in Inegers umwandeln
    #
    def GetUInt8(self, bytes, offset):
        return struct.unpack('B', self.GetBytes(bytes, offset, 1))[0]

    def GetUInt16LE(self, bytes, offset):
        return struct.unpack('<H', self.GetBytes(bytes, offset, 2))[0]

    def GetUInt32LE(self, bytes, offset):
        return struct.unpack('<I', self.GetBytes(bytes, offset, 4))[0]

    def GetInt32LE(self, bytes, offset):
        return struct.unpack('<i', self.GetBytes(bytes, offset, 4))[0]
#####################################################
