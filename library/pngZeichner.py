#
# Name: pngZeichner.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-20
# Letzte Änderung: 2020-05-29
#
# Der pngZeichner ist dafür zuständig aus dem JSON ein PNG zu erstellen.
# Das PNG wird mit einer fortlaufenden Nummer im Dateinamen gespeichert.
# Das Verzeichnis wird im Konstruktor der Klasse mitgegeben. Im Fromat: "foo/bar/verzeichnis/"
#

import colorsys
import json
import random
import sys
import time
from builtins import print

from PIL import Image, ImageDraw


####
class pngZeichner:
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
        self.DRAW_NO_GO_AREAS = True

        #
        # Konfiguration des Pasers
        #
        self.DIMENSION_PIXELS = 1024
        self.DIMENSION_MM = 50 * 1024

        self.isDebugging = False
        self.debugCounter = 0

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
    def ImageBuilder(self, drawPath, drawHeat):
        """
        Karte als .png bauen

        :dict mapDict:		Kartendaten als dict
        :bool drawHeat:		Soll heat map zeichnen
        :bool drawPath:		Soll Pfad zeichnen
        :return:			-
        """
        with open(self.FILE_PATH + "karte.json") as json_file:
            mapDict = json.load(json_file)

        # Kartendaten lesen
        dimensions = mapDict["image"]["dimensions"]
        floor = mapDict["image"]["pixels"]["floor"]
        if "dirt" in mapDict:
            dirt = mapDict["dirt"]
        obstacle_strong = mapDict["image"]["pixels"]["obstacle_strong"]
        no_go_areas = mapDict["forbidden_zones"]
        # obstacle_weak = json_file["image"]["pixels"]["segments"][31]

        # Roboterdaten lesen
        if "robot" in mapDict:
            robot = mapDict["robot"]
        if "charger" in mapDict:
            charger = mapDict["charger"]
        path = mapDict["path"]["points"]
        position = mapDict["image"]["position"]
        current_angle = mapDict["path"]["current_angle"]

        # Icons einlesen
        d_station = Image.open(self.FILE_PATH + "assets//charger.png")
        vacuum = Image.open(self.FILE_PATH + "assets//robot.png")
        # correct for inverse rotation
        vacuum = vacuum.rotate(270 - current_angle)

        # Karte zeichnen
        PngImage = Image.new(
            'RGBA', (dimensions["width"], dimensions["height"]), color=self.COLOR_BACKGROUND)
        draw = ImageDraw.Draw(PngImage)
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

            draw.point((coordinate[0], coordinate[1]),
                       fill=self.COLOR_FLOOR)
        # for coordinate in obstacle_weak:
        #	draw.point((coordinate[0],coordinate[1]), fill=self.COLOR_OBSTACLE_WEAK)
        for coordinate in obstacle_strong:
            draw.point((coordinate[0], coordinate[1]),
                       fill=self.COLOR_OBSTACLE_STRONG)

        # Karte vergroessern
        PngImage = PngImage.resize((dimensions["width"] * self.SCALE_FACTOR,
                          dimensions["height"] * self.SCALE_FACTOR), Image.NEAREST)
        draw = ImageDraw.Draw(PngImage)

        # No-Go-Zonen
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

                # Rahmen
                draw_line(0, 1, 2, 3)
                draw_line(2, 3, 4, 5)
                draw_line(4, 5, 6, 7)
                draw_line(6, 7, 0, 1)

                # Overlay
                # overlay = Image.new('RGBA', map.size, self.COLOR_BACKGROUND)
                # draw = ImageDraw.Draw(overlay)
                # draw.rectangle(((	self.TransformCoords(no_go_area[0], position["left"]),
                #					self.TransformCoords(no_go_area[1], position["top"])),
                #				(	self.TransformCoords(no_go_area[4], position["left"]),
                #					self.TransformCoords(no_go_area[5], position["top"]))),
                #	fill=self.COLOR_NOGO_AREA)
                # map = Image.alpha_composite(map, overlay)
                # draw = ImageDraw.Draw(map)

        # Roboterpfad
        if drawPath and len(path) > 1:
            old_x = self.TransformCoords(path[0][0], position["left"])
            old_y = self.TransformCoords(path[0][1], position["top"])
            for i in range(len(path)):
                if (i == len(path) - 1):
                    break
                if i % 2 == 1:
                    continue
                new_x = self.TransformCoords(
                    path[i + 1][0], position["left"])
                new_y = self.TransformCoords(
                    path[i + 1][1], position["top"])
                draw.line((old_x, old_y, new_x, new_y), fill=self.COLOR_PATH, width=round(
                    0.25 * self.SCALE_FACTOR))
                old_x = new_x
                old_y = new_y

        # Icons zeichnen
        if "charger" in mapDict:
            # Herunterskalieren
            d_station.thumbnail(
                (8 * self.SCALE_FACTOR, 8 * self.SCALE_FACTOR), Image.ANTIALIAS)
            PngImage.paste(d_station,
                      (	self.TransformCoords(charger[0], position["left"]) - round(d_station.width / 2),
                        self.TransformCoords(charger[1], position["top"]) - round(d_station.height / 2)),
                      d_station)
        if "robot" in mapDict:
            # Herunterskalieren
            vacuum.thumbnail((8 * self.SCALE_FACTOR, 8 *
                              self.SCALE_FACTOR), Image.ANTIALIAS)
            PngImage.paste(vacuum,
                      (	self.TransformCoords(robot[0], position["left"]) - round(vacuum.width / 2),
                        self.TransformCoords(robot[1], position["top"]) - round(vacuum.height / 2)),
                      vacuum)

        # Karte zuschneiden
        if self.CROP:
            PngImage = PngImage.crop((min_x * self.SCALE_FACTOR,
                            min_y * self.SCALE_FACTOR,
                            max_x * self.SCALE_FACTOR,
                            max_y * self.SCALE_FACTOR))

        # Karte erstellen
        heatMap = Image.new(
            'RGBA', (dimensions["width"], dimensions["height"]), color=self.COLOR_BACKGROUND)
        draw = ImageDraw.Draw(heatMap)

        # Schmutzpunkte zeichen
        if "dirt" in mapDict:
            for spot in dirt:
                draw.point(spot[0], fill=(self.HueToRGB(spot[1])))

        # Karte vergroessern
        heatMap = heatMap.resize(
            (dimensions["width"] * self.SCALE_FACTOR, dimensions["height"] * self.SCALE_FACTOR), Image.NEAREST)

        # Karte speichern
        PngImage.save(self.FILE_PATH + "karte_.png")
        PngImage.close()

        # Karte verbinden
        if self.isDebugging:
            PngImage = Image.open(self.FILE_PATH + "karte_.png", "r")
            heatMap.paste(PngImage, (0, 0), PngImage)
            heatMap.save('{0}{1}{2}{3}'.format(
                self.FILE_PATH, "karte", self.debugCounter, ".png"))
            self.debugCounter += 1
        else:
            PngImage = Image.open(self.FILE_PATH + "karte_.png", "r")
            heatMap.paste(PngImage, (0, 0), PngImage)
            heatMap.save(self.FILE_PATH + "karte.png")
        heatMap.close()
#####################################################

####
    def ImageBuilderDebug(self, drawPath, drawHeat):
        start_time = time.time()  # Debug: Zeit starten

        self.isDebugging = True

        self.ImageBuilder(drawPath, drawHeat)

        print("--- %s seconds --- --- PNG ---" %  (time.time() - start_time))  # Debug: Zeit stoppen
        sys.stdout.flush()
#####################################################


####
if __name__ == "__main__":
    png = pngZeichner("C:\\test\\")
    png.ImageBuilderDebug(True, True)
