#
# Name: KartenParser.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-20
# Letzte Änderung: 2020-06-02
#
# Der Parser ist dafür zuständig die karte.gz zu enpacken und die rr-Formatierten Binärdaten aufzugliedern.
# Das Ergebnis wird als JSON im selben Verzeichnis gespeichert.
# Das Verzeichnis wird im Konstruktor der Klasse mitgegeben. Im Fromat: "foo/bar/verzeichnis/"
#

import gzip
import json
import math
import os
import shutil
import struct
import sys
import time


####
class Parser:
    ####
    def __init__(self, file_path):
        #
        # Konfiguration des Pasers
        #
        self.DIMENSION_PIXELS = 1024
        self.DIMENSION_MM = 50 * 1024
        self.FILE_PATH = file_path

#
# Schmutztoleranz und Ausbreitungszerfall
#
        self.PRIM_DECAY = 0.87 
        self.SEC_DECAY = 0.8
        self.TOLERANCE = 6500
#
# Konfiguration der Karte
#
        self.SCALE_FACTOR = 4
        self.CROP = False
        self.DRAW_NO_GO_AREAS = True
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
# Bytes in Integers umwandeln
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

####
    def ParseBlock(self, fileBytes, offset, result, fileLength, fastMode):
        """
        Kartenblöcke errechnen (Rekursiv)

        :bytes fileBytes:	Kartendaten als bytes
        :int offset:		Forschritt des Lesens
        :dict result:		dict mit Daten des aktuellen Fortschrittes
        :int fileLength:	Laenge der Kartendaten
        :bool fastMode:     Nur Roboterpostion ausgeben
        :return:			result
        :return:			ParseBlock(bytes, offset, result, fileLength)
        """
        if fileLength <= offset:
            return result

        g3offset = 0
        switch = self.GetUInt16LE(fileBytes, 0x00 + offset)
        hlength = self.GetUInt16LE(fileBytes, 0x02 + offset)
        length = self.GetUInt32LE(fileBytes, 0x04 + offset)

        blockType = self.Switch(switch)

        # ROBOT_POSITION
        # CHARGER_LOCATION
        if blockType == "ROBOT_POSITION" or blockType == "CHARGER_LOCATION":
            if length >= 12:
                angle = self.GetInt32LE(fileBytes, 0x10 + offset)
            else:
                angle = 0
            result[blockType] = {
                "position": [self.GetUInt16LE(fileBytes, 0x08 + offset),
                             self.GetUInt16LE(fileBytes, 0x0c + offset)],
                "angle": angle
            }
            if fastMode and blockType == "ROBOT_POSITION":
                return result

        # IMAGE
        elif blockType == "IMAGE":
            if hlength > 24:
                g3offset = 4
            if g3offset:
                count = self.GetInt32LE(fileBytes, 0x08 + offset)
            else:
                count = 0
            parameters = {
                "segments": {
                    "count": count,
                    "if": []
                },
                "position": {
                    "top": self.GetInt32LE(fileBytes, 0x08 + g3offset + offset),
                    "left": self.GetInt32LE(fileBytes, 0x0c + g3offset + offset)
                },
                "dimensions": {
                    "height": self.GetInt32LE(fileBytes, 0x10 + g3offset + offset),
                    "width": self.GetInt32LE(fileBytes, 0x14 + g3offset + offset)
                },
                "pixels": {
                    "floor": [],
                    "obstacle_strong": [],
                    "segments": {}
                }
            }

            parameters["position"]["top"] = self.DIMENSION_PIXELS - \
                parameters["position"]["top"] - \
                parameters["dimensions"]["height"]
            if parameters["dimensions"]["height"] > 0 and parameters["dimensions"]["width"] > 0:
                i = 0
                s = 0
                while i < length:
                    val = self.GetUInt8(fileBytes, 0x18 + g3offset + offset + i)
                    if (val & 0x07) == 0:
                        i += 1
                        continue
                    coords = [i % parameters["dimensions"]["width"], parameters["dimensions"]
                              ["height"] - 1 - math.floor(i / parameters["dimensions"]["width"])]
                    i += 1
                    if (val & 0x07) == 1:
                        parameters["pixels"]["obstacle_strong"].append(coords)
                    else:
                        parameters["pixels"]["floor"].append(coords)
                        s = (val & 248) >> 3
                        if s != 0:
                            if s not in parameters["pixels"]["segments"]:
                                parameters["pixels"]["segments"][s] = []
                            parameters["pixels"]["segments"][s].append(coords)
            if blockType in result:
                result[blockType].append(parameters)
            else:
                result[blockType] = parameters

        # PATH
        # GOTO_PATH
        # GOTO_PREDICTED_PATH
        elif blockType == "PATH" or blockType == "GOTO_PATH" or blockType == "GOTO_PREDICTED_PATH":
            points = []
            i = 0
            while i < length:
                points.append([
                    self.GetUInt16LE(fileBytes, 0x14 + offset + i),
                    self.GetUInt16LE(fileBytes, 0x14 + offset + i + 2)
                ])
                i += 4
            current_angle = self.GetUInt32LE(fileBytes, 0x10 + offset)

            result[blockType] = {
                "points": points,
                "current_angle": current_angle
            }

        # GOTO_TARGET
        elif blockType == "GOTO_TARGET":
            result[blockType] = {
                "position": [
                    self.GetUInt32LE(fileBytes, 0x08 + g3offset + offset),
                    self.GetUInt32LE(fileBytes, 0x0a + g3offset + offset)
                ]
            }

        # CURRENTLY_CLEANED_ZONES
        elif blockType == "CURRENTLY_CLEANED_ZONES":
            zoneCount = self.GetUInt32LE(fileBytes, 0x08 + offset)
            zones = []
            if zoneCount > 0:
                i = 0
                while i < length:
                    zones.append([
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 2),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 4),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 6)])
                    i += 8
            if blockType in result:
                result[blockType].append(zones)
            else:
                result[blockType] = zones

        # FORBIDDEN_ZONES
        elif blockType == "FORBIDDEN_ZONES":
            forbiddenZoneCount = self.GetUInt32LE(fileBytes, 0x08 + offset)
            forbiddenZones = []
            if forbiddenZoneCount > 0:
                i = 0
                while i < length:
                    forbiddenZones.append([
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 2),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 4),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 6),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 8),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 10),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 12),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 14),
                    ])
                    i += 16
            if blockType in result:
                result[blockType].append(forbiddenZones)
            else:
                result[blockType] = forbiddenZones

        # VIRTUAL_WALLS
        elif blockType == "VIRTUAL_WALLS":
            wallCount = self.GetUInt32LE(fileBytes, 0x08 + offset)
            walls = []
            if wallCount > 0:
                while i < length:
                    walls.append([
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 2),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 4),
                        self.GetUInt16LE(fileBytes, 0x0c + offset + i + 6)
                    ])
                    i += 8
            if blockType in result:
                result[blockType].append(walls)
            else:
                result[blockType] = walls

        # CURRENTLY_CLEANED_BLOCKS
        elif blockType == "CURRENTLY_CLEANED_BLOCKS":
            blockCount = self.GetUInt32LE(fileBytes, 0x08 + offset)
            blocks = []
            if blockCount > 0:
                while i < length:
                    blocks.append(
                        [self.self.GetUInt8(fileBytes, 0x0c + offset + i)])
                    i += 1
            if blockType in result:
                result[blockType].append(blocks)
            else:
                result[blockType] = blocks

        # DIGEST
        elif blockType == "DIGEST":
            pass

        else:
            pass

        return self.ParseBlock(fileBytes, offset + length + hlength, result, fileLength, fastMode)
#####################################################

####
    def Parse(self, blocks, fileBytes):
        """
        Karte analysieren

        :dict blocks:		Blockdaten
        :bytes file:		Kartendaten als bytes
        :return:			parsedMapData
        """
        parsedMapData = {
            "header_length": self.GetUInt16LE(fileBytes, 0x02),
            "data_length": self.GetUInt16LE(fileBytes, 0x04),
            "version": {
                "major": self.GetUInt16LE(fileBytes, 0x08),
                "minor": self.GetUInt16LE(fileBytes, 0x0A)
            },
            "map_index": self.GetUInt16LE(fileBytes, 0x0C),
            "map_sequence": self.GetUInt16LE(fileBytes, 0x10)
        }

        # IMAGE
        if "IMAGE" in blocks:
            parsedMapData["image"] = blocks["IMAGE"]
            tempList = [
                {"type": "PATH",
                 "path": "path"
                 },
                {"type": "GOTO_PATH",
                 "path": "goto_path"
                 },
                {"type": "GOTO_PREDICTED_PATH",
                 "path": "goto_predicted_path"
                 }]
            for item in tempList:
                if item["type"] in blocks:
                    parsedMapData[item["path"]] = blocks[item["type"]]

                    def lamb(point):
                        point[1] = self.DIMENSION_MM - point[1]
                        return point
                    parsedMapData[item["path"]]["points"] = list(
                        map(lamb, parsedMapData[item["path"]]["points"]))
                    if len(parsedMapData[item["path"]]["points"]) >= 2:
                        parsedMapData[item["path"]]["current_angle"] = math.atan2(
                            parsedMapData[item["path"]]["points"][len(parsedMapData[item["path"]]["points"]) - 1][1] -
                            parsedMapData[item["path"]]["points"][len(
                                parsedMapData[item["path"]]["points"]) - 2][1],
                            parsedMapData[item["path"]]["points"][len(parsedMapData[item["path"]]["points"]) - 1][0] -
                            parsedMapData[item["path"]]["points"][len(
                                parsedMapData[item["path"]]["points"]) - 2][0]
                        ) * 180 / math.pi
            if "CHARGER_LOCATION" in blocks:
                parsedMapData["charger"] = blocks["CHARGER_LOCATION"]["position"]
                parsedMapData["charger"][1] = self.DIMENSION_MM - \
                    parsedMapData["charger"][1]
            if "ROBOT_POSITION" in blocks:
                parsedMapData["robot"] = blocks["ROBOT_POSITION"]["position"]
                parsedMapData["robot"][1] = self.DIMENSION_MM - \
                    parsedMapData["robot"][1]
            if "GOTO_TARGET" in blocks:
                parsedMapData["goto_target"] = blocks["GOTO_TARGET"]["position"]
                parsedMapData["goto_target"][1] = self.DIMENSION_MM - \
                    parsedMapData["goto_target"][1]
            if "CURRENTLY_CLEANED_ZONES" in blocks:
                parsedMapData["currently_cleaned_zones"] = blocks["CURRENTLY_CLEANED_ZONES"]

                def lamb(zone):
                    zone[1] = self.DIMENSION_MM - zone[1]
                    zone[3] = self.DIMENSION_MM - zone[3]
                    return zone
                parsedMapData["currently_cleaned_zones"] = list(
                    map(lamb, parsedMapData["currently_cleaned_zones"]))
            if "FORBIDDEN_ZONES" in blocks:
                parsedMapData["forbidden_zones"] = blocks["FORBIDDEN_ZONES"]

                def lamb(zone):
                    zone[1] = self.DIMENSION_MM - zone[1]
                    zone[3] = self.DIMENSION_MM - zone[3]
                    zone[5] = self.DIMENSION_MM - zone[5]
                    zone[7] = self.DIMENSION_MM - zone[7]
                    return zone
                parsedMapData["forbidden_zones"] = list(
                    map(lamb, parsedMapData["forbidden_zones"]))
            if "VIRTUAL_WALLS" in blocks:
                parsedMapData["virtual_walls"] = blocks["VIRTUAL_WALLS"]

                def lamb(wall):
                    wall[1] = self.DIMENSION_MM - wall[1]
                    wall[3] = self.DIMENSION_MM - wall[3]
                    return wall
                parsedMapData["virtual_walls"] = list(
                    map(lamb, parsedMapData["virtual_walls"]))
            if "CURRENTLY_CLEANED_BLOCKS" in blocks:
                parsedMapData["currently_cleaned_blocks"] = blocks["CURRENTLY_CLEANED_BLOCKS"]
            return parsedMapData
#####################################################

    def BuildDirt(self, parsedMapData):
        if os.path.isfile(self.FILE_PATH + "dreck.json"):
            with open(self.FILE_PATH + "dreck.json") as json_file:
                dreckDict = json.load(json_file)

            position = parsedMapData["image"]["position"]
            floor = parsedMapData["image"]["pixels"]["floor"]

            # Verschmutzungspunkte
            dirtSpots = []
            primSpots = []
            spotGrid = []

            # Gitter anlegen
            for coordinate in floor:
                if coordinate[0] % 2 == 1 and coordinate[1] % 2 == 1:
                    spot = [(coordinate[0], coordinate[1]), 0]
                    spotGrid.append(spot)

            # Dreck einlesen
            if "dirt" in dreckDict:
                for dreck in dreckDict["dirt"]:
                    pos = [(int)(self.TransformCoords(dreck[0][0], position["left"]) / self.SCALE_FACTOR),
                           (int)(self.TransformCoords(dreck[0][1], position["top"]) / self.SCALE_FACTOR)]
                    if pos[0] % 2 == 0:
                        pos[0] = pos[0] - 1
                    if pos[1] % 2 == 0:
                        pos[1] = pos[1] - 1
                    if pos in floor:
                        dirtSpots.append([(pos[0], pos[1]), dreck[1]])
                        

            # Primaere Schmutzpunkte verteilen
            for spot in spotGrid:
                for dirt in dirtSpots:
                    test = spot[0]
                    target = dirt[0]
                    if (test[0], test[1]) == target and dirt[1] > self.TOLERANCE and spot[1] < dirt[1]:
                        spot[1] = dirt[1]
                        primSpots.append(spot)

            # Schmutzausbreitung (deaktiviert für kleine Testbox)
                    # if (test[0] - 2, test[1]) == target or (test[0] + 2, test[1]) == target or (test[0], test[1] - 2) == target or (test[0], test[1] + 2) == target:
                    #     if ((int)(dirt[1]) * self.PRIM_DECAY) > self.TOLERANCE:
                    #         if spot[1] != 360:
                    #             if spot[1] > dirt[1]:
                    #                 spot[1] = dirt[1]
                    #         else:
                    #             spot[1] = ((int)(dirt[1]) * self.PRIM_DECAY)
                    #         primSpots.append(spot)
                    # if (test[0] - 2, test[1] - 2) == target or (test[0] + 2, test[1] + 2) == target or (test[0] + 2, test[1] - 2) == target or (test[0] - 2, test[1] + 2) == target:
                    #     if ((int)(dirt[1]) * self.SEC_DECAY) > self.TOLERANCE:
                    #         if spot[1] != 360:
                    #             if spot[1] > dirt[1]:
                    #                 spot[1] = dirt[1]
                    #         else:
                    #             spot[1] = ((int)(dirt[1]) * self.SEC_DECAY)
                    #         primSpots.append(spot)

            parsedMapData["dirt"] = primSpots
        return parsedMapData


####

    def Unpack(self):
        """
        Entpackt die Datei und gibt Datei und Dateilaenge zurueck

        :return:		[file, fileLength]
        """
        with gzip.open(self.FILE_PATH + "karte.gz", 'r') as f_in, open(self.FILE_PATH + "karte", 'wb+') as f_out:
            shutil.copyfileobj(f_in, f_out)
            #print(os.path.getmtime(self.FILE_PATH + "karte.gz"))

        fileBytes = open(self.FILE_PATH + "karte", 'rb+')
        fileLength = os.path.getsize(self.FILE_PATH + "karte")
        return [fileBytes, fileLength]
#####################################################

####
    def GetRoboPos(self):
        """
        Programmstart, gibt nur Position zurück

        :return:		Roboterkoordinaten
        """
        parsedMapData = {}
        unpacked = self.Unpack()
        fileBytes = unpacked[0]
        fileLength = unpacked[1]
        if self.GetBytes(fileBytes, 0, 1) == b'\x72' and self.GetBytes(fileBytes, 1, 1) == b'\x72':
            blocks = self.ParseBlock(fileBytes, 0x14, {}, fileLength, True)
            if "ROBOT_POSITION" in blocks:
                parsedMapData["robot"] = blocks["ROBOT_POSITION"]["position"]
                parsedMapData["robot"][1] = self.DIMENSION_MM - \
                    parsedMapData["robot"][1]
        fileBytes.close()
        return parsedMapData
#####################################################

####
    def BuildJSON(self, drawDirt):
        """
        Programmstart, erstellt JSON
        :bool drawDirt:     Ob Verschmutzungsdaten hinzugefügt werden soll
        :return:		    -
        """
        if os.path.exists(self.FILE_PATH + "karte.gz"):
            unpacked = self.Unpack()
            fileBytes = unpacked[0]
            fileLength = unpacked[1]
            if self.GetBytes(fileBytes, 0, 1) == b'\x72' and self.GetBytes(fileBytes, 1, 1) == b'\x72':
                blocks = self.ParseBlock(fileBytes, 0x14, {}, fileLength, False)
                mapData = self.Parse(blocks, fileBytes)
                if drawDirt:
                    mapData = self.BuildDirt(mapData)
                with open(self.FILE_PATH + "karte.json", "w") as write_file:
                    json.dump(mapData, write_file)
            fileBytes.close()
#####################################################

# #### # Debug
#     def BuildJsonDebug(self, drawDirt): # Debug
#         start_time = time.time()  # Debug: Zeit starten

#         self.BuildJSON(drawDirt)

#         print("--- %s seconds --- JSON ---" % (time.time() - start_time))  # Debug: Zeit stoppen
#         sys.stdout.flush()
# #####################################################


# #### # Debug
# if __name__ == "__main__": # Debug
#     karte = Parser("C:\\test\\")
#     karte.BuildJsonDebug()
