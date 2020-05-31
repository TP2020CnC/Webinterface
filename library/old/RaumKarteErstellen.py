#
# Name: RaumKarteErstellen.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-08
# Letzte Änderung: 2020-05-20
#
# LEGACY # LEGACY # LEGACY # LEGACY # LEGACY # LEGACY # LEGACY
# wird nicht mehr benutzt

import io
import json
import struct
import os
import math
import colorsys
import sys
import random
import time
import shutil
import gzip
from PIL import Image, ImageDraw


class KartenErsteller:
    ####
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

####
    def ParseBlock(self, bytes, offset, result, fileLength):
        """
        Kartenblöcke errechnen (Rekursiv)

        :bytes bytes:		Kartendaten als bytes
        :int offset:		Forschritt des byte lesens
        :dict result:		dict mit Daten des aktuellen Fortschrittes
        :int fileLength:	Laenge der Kartendaten
        :return:			result
        :return:			ParseBlock(bytes, offset, result, fileLength)
        """

        if fileLength <= offset:
            return result

        g3offset = 0
        switch = self.GetUInt16LE(bytes, 0x00 + offset)
        hlength = self.GetUInt16LE(bytes, 0x02 + offset)
        length = self.GetUInt32LE(bytes, 0x04 + offset)

        type = self.Switch(switch)

        # ROBOT_POSITION
        # CHARGER_LOCATION
        if type == "ROBOT_POSITION" or type == "CHARGER_LOCATION":
            if length >= 12:
                angle = self.GetInt32LE(bytes, 0x10 + offset)
            else:
                angle = 0
            result[type] = {
                "position": [self.GetUInt16LE(bytes, 0x08 + offset),
                             self.GetUInt16LE(bytes, 0x0c + offset)],
                "angle": angle
            }

        # IMAGE
        elif type == "IMAGE":
            if hlength > 24:
                g3offset = 4
            if g3offset:
                count = self.GetInt32LE(bytes, 0x08 + offset)
            else:
                count = 0
            parameters = {
                "segments": {
                    "count": count,
                    "if": []
                },
                "position": {
                    "top": self.GetInt32LE(bytes, 0x08 + g3offset + offset),
                    "left": self.GetInt32LE(bytes, 0x0c + g3offset + offset)
                },
                "dimensions": {
                    "height": self.GetInt32LE(bytes, 0x10 + g3offset + offset),
                    "width": self.GetInt32LE(bytes, 0x14 + g3offset + offset)
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
                    val = self.GetUInt8(bytes, 0x18 + g3offset + offset + i)
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
            if type in result:
                result[type].append(parameters)
            else:
                result[type] = parameters

        # PATH
        # GOTO_PATH
        # GOTO_PREDICTED_PATH
        elif type == "PATH" or type == "GOTO_PATH" or type == "GOTO_PREDICTED_PATH":
            points = []
            i = 0
            while i < length:
                points.append([
                    self.GetUInt16LE(bytes, 0x14 + offset + i),
                    self.GetUInt16LE(bytes, 0x14 + offset + i + 2)
                ])
                i += 4
            current_angle = self.GetUInt32LE(bytes, 0x10 + offset)

            result[type] = {
                "points": points,
                "current_angle": current_angle
            }

        # GOTO_TARGET
        elif type == "GOTO_TARGET":
            result[type] = {
                "position": [
                    self.GetUInt32LE(bytes, 0x08 + g3offset + offset),
                    self.GetUInt32LE(bytes, 0x0a + g3offset + offset)
                ]
            }

        # CURRENTLY_CLEANED_ZONES
        elif type == "CURRENTLY_CLEANED_ZONES":
            zoneCount = self.GetUInt32LE(bytes, 0x08 + offset)
            zones = []
            if zoneCount > 0:
                i = 0
                while i < length:
                    zones.append([
                        self.GetUInt16LE(bytes, 0x0c + offset + i),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 2),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 4),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 6)])
                    i += 8
            if type in result:
                result[type].append(zones)
            else:
                result[type] = zones

        # FORBIDDEN_ZONES
        elif type == "FORBIDDEN_ZONES":
            forbiddenZoneCount = self.GetUInt32LE(bytes, 0x08 + offset)
            forbiddenZones = []
            if forbiddenZoneCount > 0:
                i = 0
                while i < length:
                    forbiddenZones.append([
                        self.GetUInt16LE(bytes, 0x0c + offset + i),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 2),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 4),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 6),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 8),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 10),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 12),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 14),
                    ])
                    i += 16
            if type in result:
                result[type].append(forbiddenZones)
            else:
                result[type] = forbiddenZones

        # VIRTUAL_WALLS
        elif type == "VIRTUAL_WALLS":
            wallCount = self.GetUInt32LE(bytes, 0x08 + offset)
            walls = []
            if wallCount > 0:
                while i < length:
                    walls.append([
                        self.GetUInt16LE(bytes, 0x0c + offset + i),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 2),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 4),
                        self.GetUInt16LE(bytes, 0x0c + offset + i + 6)
                    ])
                    i += 8
            if type in result:
                result[type].append(walls)
            else:
                result[type] = walls

        # CURRENTLY_CLEANED_BLOCKS
        elif type == "CURRENTLY_CLEANED_BLOCKS":
            blockCount = self.GetUInt32LE(bytes, 0x08 + offset)
            blocks = []
            if blockCount > 0:
                i = 0
                while i < length:
                    blocks.append([self.GetUInt8(bytes, 0x0c + offset + i)])
                    i += 1
            if type in result:
                result[type].append(blocks)
            else:
                result[type] = blocks

        # DIGEST
        elif type == "DIGEST":
            pass

        else:
            pass

        return self.ParseBlock(bytes, offset + length + hlength, result, fileLength)
#####################################################

####
    def Parse(self, blocks, file):
        """
        Karte analysieren

        :bytes file:		Kartendaten als bytes
        :dict blocks:		Blockdaten
        :return:			parsedMapData
        """

        parsedMapData = {
            "header_length": self.GetUInt16LE(file, 0x02),
            "data_length": self.GetUInt16LE(file, 0x04),
            "version": {
                "major": self.GetUInt16LE(file, 0x08),
                "minor": self.GetUInt16LE(file, 0x0A)
            },
            "map_index": self.GetUInt16LE(file, 0x0C),
            "map_sequence": self.GetUInt16LE(file, 0x10)
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

####
    def ImageBuilder(self, mapDict, drawPath):
        """
        Karte als .png bauen

        :dict mapDict:		Kartendaten als dict
        :return:			-
        """

        # Kartendaten lesen
        dimensions = mapDict["image"]["dimensions"]
        floor = mapDict["image"]["pixels"]["floor"]
        obstacle_strong = mapDict["image"]["pixels"]["obstacle_strong"]
        no_go_areas = mapDict["forbidden_zones"]
        #obstacle_weak = json_file["image"]["pixels"]["segments"][31]

        # Roboterdaten lesen
        if "robot" in mapDict:
            robot = mapDict["robot"]
        if "charger" in mapDict:
            charger = mapDict["charger"]
        path = mapDict["path"]["points"]
        position = mapDict["image"]["position"]
        current_angle = mapDict["path"]["current_angle"]

        # Icons einlesen
        d_station = Image.open(self.FILE_PATH + "assets/charger.png")
        vacuum = Image.open(self.FILE_PATH + "assets/robot.png")
        # correct for inverse rotation
        vacuum = vacuum.rotate(360 - current_angle)

        # Karte zeichnen
        map = Image.new(
            'RGBA', (dimensions["width"], dimensions["height"]), color=self.COLOR_BACKGROUND)
        draw = ImageDraw.Draw(map)
        max_x = 0
        max_y = 0
        min_x = dimensions["width"]
        min_y = dimensions["height"]

        for coordinate in floor:
            # Wenn Karte zugeschnitten werden soll
            if self.CROP:
                max_x = coordinate[0] if max_x < coordinate[0] else max_x
                max_y = coordinate[1] if max_y < coordinate[1] else max_y
                min_x = coordinate[0] if min_x > coordinate[0] else min_x
                min_y = coordinate[1] if min_y > coordinate[1] else min_y

            draw.point((coordinate[0], coordinate[1]), fill=self.COLOR_FLOOR)
        # for coordinate in obstacle_weak:
        #	draw.point((coordinate[0],coordinate[1]), fill=self.COLOR_OBSTACLE_WEAK)
        for coordinate in obstacle_strong:
            draw.point((coordinate[0], coordinate[1]),
                       fill=self.COLOR_OBSTACLE_STRONG)

        # Karte vergroessern
        map = map.resize((dimensions["width"] * self.SCALE_FACTOR,
                          dimensions["height"] * self.SCALE_FACTOR), Image.NEAREST)
        draw = ImageDraw.Draw(map)

        # no go zones
        if self.DRAW_NO_GO_AREAS:
            for no_go_area in no_go_areas:
                def draw_line(i1, i2, i3, i4):
                    draw.line((self.TransformCoords(no_go_area[i1], position["left"]),
                               self.TransformCoords(
                                   no_go_area[i2], position["top"]),
                               self.TransformCoords(
                                   no_go_area[i3], position["left"]),
                               self.TransformCoords(no_go_area[i4], position["top"])),
                              fill=self.COLOR_NOGO_BORDER,
                              width=round(0.5 * self.SCALE_FACTOR))

                # draw box borders
                draw_line(0, 1, 2, 3)
                draw_line(2, 3, 4, 5)
                draw_line(4, 5, 6, 7)
                draw_line(6, 7, 0, 1)

                # create rectange on an overlay to preserve map data below; then
                # merge it
                overlay = Image.new('RGBA', map.size, self.COLOR_BACKGROUND)
                draw = ImageDraw.Draw(overlay)
                draw.rectangle(((self.TransformCoords(no_go_area[0], position["left"]),
                                 self.TransformCoords(no_go_area[1], position["top"])),
                                (self.TransformCoords(no_go_area[4], position["left"]),
                                 self.TransformCoords(no_go_area[5], position["top"]))),
                               fill=self.COLOR_NOGO_AREA)
                map = Image.alpha_composite(map, overlay)
                draw = ImageDraw.Draw(map)

        # Roboterpfad
        if self.DRAW_PATH and drawPath and len(path) > 1:
            old_x = self.TransformCoords(path[0][0], position["left"])
            old_y = self.TransformCoords(path[0][1], position["top"])
            for x in range(len(path)):
                if (x == len(path) - 1):
                    break
                if x % 2 == 1:
                    continue
                new_x = self.TransformCoords(path[x + 1][0], position["left"])
                new_y = self.TransformCoords(path[x + 1][1], position["top"])
                draw.line((old_x, old_y, new_x, new_y), fill=self.COLOR_PATH, width=round(
                    0.25 * self.SCALE_FACTOR))
                old_x = new_x
                old_y = new_y

        # Icons zeichnen
        if "charger" in mapDict:
            # Herunterskalieren
            d_station.thumbnail(
                (8 * self.SCALE_FACTOR, 8 * self.SCALE_FACTOR), Image.ANTIALIAS)
            map.paste(d_station,
                      (self.TransformCoords(charger[0], position["left"]) - round(d_station.width / 2),
                       self.TransformCoords(charger[1], position["top"]) - round(d_station.height / 2)),
                      d_station)
        if "robot" in mapDict:
            # Herunterskalieren
            vacuum.thumbnail((8 * self.SCALE_FACTOR, 8 *
                              self.SCALE_FACTOR), Image.ANTIALIAS)
            map.paste(vacuum,
                      (self.TransformCoords(robot[0], position["left"]) - round(vacuum.width / 2),
                       self.TransformCoords(robot[1], position["top"]) - round(vacuum.height / 2)),
                      vacuum)

        # Karte zuschneiden
        if self.CROP:
            map = map.crop((min_x * self.SCALE_FACTOR,
                            min_y * self.SCALE_FACTOR,
                            max_x * self.SCALE_FACTOR,
                            max_y * self.SCALE_FACTOR))

        # Karte speichern
        map.save(self.FILE_PATH + "karte_.png")
        map.close()
#####################################################

####
    def ImageEnhancer(self, mapDict):
        """
        Karte anhand der Schmutzverteilung umfaerben (Heatmap)

        :dict mapDict:		Kartendaten als dict
        :return:			-
        """

        # Schmutztoleranz und ausbreitungszerfall
        PRIM_DECAY = 1.8
        SEC_DECAY = 1.4
        TOLERANCE = 60

        # Kartendaten lesen
        dimensions = mapDict["image"]["dimensions"]
        floor = mapDict["image"]["pixels"]["floor"]
        robot = mapDict["robot"]
        position = mapDict["image"]["position"]
        vacuum = Image.open(self.FILE_PATH + "assets//robot.png")

        # Karte erstellen
        colorMap = Image.new(
            'RGBA', (dimensions["width"], dimensions["height"]), color=self.COLOR_BACKGROUND)
        draw = ImageDraw.Draw(colorMap)

        # Verschmutzungspunkte
        dirtSpots = []
        primSpots = []
        secSpots = []
        spotGrid = []

        # Gitter anlegen
        for coordinate in floor:
            if coordinate[0] % 2 == 1 and coordinate[1] % 2 == 1:
                spot = [(coordinate[0], coordinate[1]), 360]
                draw.point(spot[0], fill=self.COLOR_TEST_CLEAN)
                spotGrid.append(spot)

        # TEST TEST TEST TEST TEST TEST TEST
        build_i = 0
        while build_i < 80:
            dirtSpots.append(
                [(197, 181 + build_i), random.randrange(TOLERANCE)])
            build_i += 8
        build_i = 0
        while build_i < 16:
            dirtSpots.append(
                [(197 - build_i, 261), random.randrange(TOLERANCE)])
            build_i += 8
        build_i = 0
        while build_i < 20:
            dirtSpots.append(
                [(181, 261 - build_i), random.randrange(TOLERANCE)])
            build_i += 8
        build_i = 0
        while build_i < 32:
            dirtSpots.append(
                [(181 - build_i, 241), random.randrange(TOLERANCE)])
            build_i += 8

        rpos = ((int)(self.TransformCoords(robot[0], position["left"]) / self.SCALE_FACTOR), (int)(
            self.TransformCoords(robot[1], position["top"]) / self.SCALE_FACTOR))
        dirtSpots.append([(rpos[0] + 10, rpos[1]), 0])
        # TEST TEST TEST TEST TEST TEST TEST

        # Primaere Schmutzpunkte verteilen
        for spot in spotGrid:
            for dirt in dirtSpots:
                test = spot[0]
                target = dirt[0]
                if (test[0], test[1]) == target:
                    if dirt[1] < TOLERANCE:
                        spot[1] = dirt[1]
                        primSpots.append(spot)
                if (test[0] - 2, test[1]) == target or (test[0] + 2, test[1]) == target or (test[0], test[1] - 2) == target or (test[0], test[1] + 2) == target:
                    if ((int)(dirt[1] + 20) * PRIM_DECAY - 20) < TOLERANCE:
                        if spot[1] != 360:
                            spot[1] = (spot[1] + dirt[1]) / 2
                        else:
                            spot[1] = ((int)(dirt[1] + 20) * PRIM_DECAY - 20)
                        primSpots.append(spot)
                    else:
                        dirtSpots.remove(dirt)
                if (test[0] - 2, test[1] - 2) == target or (test[0] + 2, test[1] + 2) == target or (test[0] + 2, test[1] - 2) == target or (test[0] - 2, test[1] + 2) == target:
                    if ((int)(dirt[1] + 20) * PRIM_DECAY * 1.4 - 20) < TOLERANCE:
                        if spot[1] != 360:
                            spot[1] = (spot[1] + dirt[1]) / 2
                        else:
                            spot[1] = ((int)(dirt[1] + 20) *
                                       PRIM_DECAY * 1.4 - 20)
                        primSpots.append(spot)

        # Sekundaere Schmutzpunkte verteilen
        for spot in spotGrid:
            if spot not in primSpots:
                for dirt in primSpots:
                    test = spot[0]
                    target = dirt[0]
                    if (test[0] - 2, test[1]) == target or (test[0] + 2, test[1]) == target or (test[0], test[1] - 2) == target or (test[0], test[1] + 2) == target:
                        if (int)(dirt[1] * SEC_DECAY) < TOLERANCE:
                            if spot[1] != 360:
                                spot[1] = (spot[1] + dirt[1]) / 2
                            else:
                                spot[1] = ((int)(dirt[1] + 20)
                                           * SEC_DECAY - 20)
                            secSpots.append(spot)
        #			if (test[0] - 2, test[1] - 2) == target or (test[0] + 2, test[1] + 2) == target or (test[0] + 2, test[1] - 2) == target or (test[0] - 2, test[1] + 2) == target:
        #				if (int)(dirt[1] * SEC_DECAY) < TOLERANCE:
        #					if spot[1] != 360:
        #						spot[1] = (spot[1] + dirt[1]) / 2
        #					else:
        #						spot[1] = ((int)(dirt[1] + 20) * SEC_DECAY * 1.8 - 20)
        #					orangeSpots.append(spot)

        # Schmutzpunkte zeichen
        for dirt in primSpots:
            draw.point(dirt[0], fill=(self.HueToRGB(dirt[1])))
        for dirt in secSpots:
            draw.point(dirt[0], fill=(self.HueToRGB(dirt[1])))

        # Karte vergroessern
        colorMap = colorMap.resize(
            (dimensions["width"] * self.SCALE_FACTOR, dimensions["height"] * self.SCALE_FACTOR), Image.NEAREST)

        # Karte verbinden
        map = Image.open(self.FILE_PATH + "karte_.png", "r")
        colorMap.paste(map, (0, 0), map)
        colorMap.save(self.FILE_PATH + "karte.png")
        colorMap.close()
#####################################################

####
    def Unpack(self):
        """
        Entpackt die Datei und gibt Datei und Dateilänge zurueck

        :return:		[file, fileLength]
        """
        with gzip.open(self.FILE_PATH + "karte.gz", 'r') as f_in, open(self.FILE_PATH + "karte", 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        file = open(self.FILE_PATH + "karte", 'rb')
        fileLength = os.path.getsize(self.FILE_PATH + "karte")
        return [file, fileLength]
#####################################################

####
    def BuildMap(self, drawHeatmap, drawPath):
        """
        Programmstart zum erstellen der Karte

        :bool drawHeatmap:	ob eine Heatmap erstellt werden soll ()
        :bool drawPath:		ob der Pfad gezeichnet werden soll ()
        :return:		-
        """

        unpacked = self.Unpack()
        file = unpacked[0]
        fileLength = unpacked[1]

        if self.GetBytes(file, 0, 1) == b'\x72' and self.GetBytes(file, 1, 1) == b'\x72':
            blocks = self.ParseBlock(file, 0x14, {}, fileLength)
            mapData = self.Parse(blocks, file)
            self.ImageBuilder(mapData, drawPath)
            if drawHeatmap:
                self.ImageEnhancer(mapData)
            else:
                shutil.move(self.FILE_PATH + "karte_.png",
                            self.FILE_PATH + "karte.png")
        file.close()
#####################################################

####
    def BuildJSON(self):
        """
        Programmstart, nur JSON-Ausgabe

        :return:		-
        """

        unpacked = self.Unpack()
        file = unpacked[0]
        fileLength = unpacked[1]

        if self.GetBytes(file, 0, 1) == b'\x72' and self.GetBytes(file, 1, 1) == b'\x72':
            blocks = self.ParseBlock(file, 0x14, {}, fileLength)
            mapData = self.Parse(blocks, file)
            with open(self.FILE_PATH + "karte.json", "w") as write_file:
                json.dump(mapData, write_file)
        file.close()
#####################################################

####
    def Debug(self):
        start_time = time.time()  # Debug: Zeit starten

        self.BuildJSON()
        self.BuildMap(1, 1)

        print("--- %s seconds ---" %
              (time.time() - start_time))  # Debug: Zeit stoppen
#####################################################


####
if __name__ == "__main__":
    karte = KartenErsteller("C:/test/")
    karte.Debug()
