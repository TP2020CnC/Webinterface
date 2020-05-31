#
# Name: svgZeichner.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-29
# Letzte Änderung: 2020-05-29
#
# Der svgZeichner ist dafür zuständig aus dem JSON ein PNG zu erstellen.
# Das PNG wird mit einer fortlaufenden Nummer im Dateinamen gespeichert.
# Das Verzeichnis wird im Konstruktor der Klasse mitgegeben. Im Fromat: "foo/bar/verzeichnis/"
#

#from PIL import Image, ImageDraw
import colorsys
import json
import random
import sys
import time
from builtins import print

import drawSvg as draw


####
class svgZeichner:
    ####
    def __init__(self, file_path):
        #
        # Farben
        #
        self.COLOR_FLOOR = '#9c9c9c'
        self.COLOR_OBSTACLE_WEAK = '#94ff96'
        self.COLOR_OBSTACLE_STRONG = '#0fff13'
        self.COLOR_PATH = '#f2f2f2'
        self.COLOR_NOGO_BORDER = '#ff338f'
        self.COLOR_NOGO_AREA = '#ffb8d8'
        self.COLOR_BACKGROUND = '#5c5c5c'
        self.COLOR_TEST_CLEAN = '#35e1ed'

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
        return '#%02x%02x%02x' % ((int)(buf[0] * 255), (int)(buf[1] * 255), (int)(buf[2] * 255))
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
        #d_station = self.FILE_PATH + "assets//charger.png"
        #SvgImage.add(d_station, {'x': 10, 'y': 20, 'width': 80, 'height': 55, 'fill': 'blue'})
        #vacuum = Image.open(self.FILE_PATH + "assets//robot.png")
        # correct for inverse rotation
        #vacuum = vacuum.rotate(270 - current_angle)

        # Karte zeichnen
        svgImage = draw.Drawing(dimensions["width"] * self.SCALE_FACTOR, dimensions["height"] * self.SCALE_FACTOR, origin=(0, -dimensions["height"] * self.SCALE_FACTOR), displayInline=False)

        for coordinate in floor:
            svgImage.append(draw.Rectangle(coordinate[0] * self.SCALE_FACTOR, -coordinate[1] * self.SCALE_FACTOR, 1 * self.SCALE_FACTOR, 1 * self.SCALE_FACTOR, fill=self.COLOR_FLOOR))


        for coordinate in obstacle_strong:
            svgImage.append(draw.Rectangle(coordinate[0] * self.SCALE_FACTOR, -coordinate[1] * self.SCALE_FACTOR, 1 * self.SCALE_FACTOR, 1 * self.SCALE_FACTOR, fill=self.COLOR_OBSTACLE_STRONG))
    

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
                svgImage.append(draw.Line(old_x, -old_y, new_x, -new_y, stroke=self.COLOR_PATH, stroke_width=0.25 * self.SCALE_FACTOR, fill='none'))
                old_x = new_x
                old_y = new_y

        # Icons zeichnen
        # if "charger" in mapDict:
        #     # Herunterskalieren
        #     d_station.thumbnail(
        #         (8 * self.SCALE_FACTOR, 8 * self.SCALE_FACTOR), Image.ANTIALIAS)
        #     SvgImage.paste(d_station,
        #               (	self.TransformCoords(charger[0], position["left"]) - round(d_station.width / 2),
        #                 self.TransformCoords(charger[1], position["top"]) - round(d_station.height / 2)),
        #               d_station)
        # if "robot" in mapDict:
        #     # Herunterskalieren
        #     vacuum.thumbnail((8 * self.SCALE_FACTOR, 8 *
        #                       self.SCALE_FACTOR), Image.ANTIALIAS)
        #     SvgImage.paste(vacuum,
        #               (	self.TransformCoords(robot[0], position["left"]) - round(vacuum.width / 2),
        #                 self.TransformCoords(robot[1], position["top"]) - round(vacuum.height / 2)),
        #               vacuum)

        # Schmutzpunkte zeichen
        if "dirt" in mapDict:
            for spot in dirt:
                svgImage.append(draw.Rectangle(self.TransformCoords(spot[0][0], position["left"]), self.TransformCoords(spot[0][0], position["top"]), 1 * self.SCALE_FACTOR, 1 * self.SCALE_FACTOR, fill=self.HueToRGB(spot[1])))

        svgImage.setRenderSize(dimensions["width"] * self.SCALE_FACTOR, dimensions["height"] * self.SCALE_FACTOR)

        # Karte speichern
        svgImage.saveSvg(self.FILE_PATH + "karte.svg")
# #####################################################

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
    png = svgZeichner("C:\\test\\")
    png.ImageBuilderDebug(True, True)
