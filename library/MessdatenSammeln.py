#
# Name: MessdatenSammeln.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-15
# Letzte Änderung: 2020-05-29
#
# Der MessdatenSammler ist dafür zuständig die Messdaten aus der SQLite-Datenbank zu sammeln und ab eine gewissen Messgroesse abzuspeichern.
# Der Wert wird zusammen mit der aktuellen Staubsaugerposition in die dreck.json geschrieben. 
# Das Verzeichnis wird im Konstruktor der Klasse mitgegeben. Im Fromat: "foo/bar/verzeichnis/"
#

import json
import os
import sqlite3
import sys
import time

try:
    from Webinterface.library.DatenbankVerwalten import DatenbankVerwalter
except:
    from DatenbankVerwalten import DatenbankVerwalter



class MessdatenSammler:
#####################################################
    def __init__(self, file_path):
        self.db = DatenbankVerwalter()
        self.lastTime = 0
        self.FILE_PATH = file_path
        
        self.TOLERANCE = 6500
#####################################################

####
    def current_milli_time(self):
        """
        Aktuelle Zeit in Millisekunden

        :return:			int
        """
        return int(round(time.time() * 1000))
#####################################################

####
    def InsertDreck(self, dreck, roboPos):
        """
        Einfügen der Verschmutzungsdaten in die dreck.json

        :float dreck:		Messwert
        :list roboPos:      Roboterposition
        """
        if not os.path.isfile(self.FILE_PATH + "dreck.json"):
            data = {}
            data["dirt"] = []
            with open(self.FILE_PATH + "dreck.json", "w+") as write_file:
                json.dump(data, write_file)
        with open(self.FILE_PATH + "dreck.json", "r") as json_file:
            data = json.load(json_file)
        
        spot = [[roboPos["robot"][0], roboPos["robot"][1]], dreck]
        data["dirt"].append(spot)
        with open(self.FILE_PATH + "dreck.json", "w+") as write_file:
            json.dump(data, write_file)
#####################################################

####
    def UpdateDreck(self, roboPos):
        """
        Verschmutzungsdaten auslesen und schreiben

        :list roboPos:      Roboterposition
        """     
        dreckConn = sqlite3.connect(self.FILE_PATH + "messdaten.db")
        dreck = self.db.GetDreck(dreckConn, self.lastTime)
        self.lastTime = self.current_milli_time()
        if dreck is not None and dreck > self.TOLERANCE:
            #print("Einfügen:")  # Debug # Debug # Debug
            #print(dreck)  # Debug # Debug # Debug
            self.InsertDreck(dreck, roboPos)        
#####################################################

# ####
#     def UpdateDreckDebug(self, roboPos):
#         """
#     Debug
#     """
#         start_time = time.time()  # Debug: Zeit starten

#         self.UpdateDreck(roboPos)

#         print("--- %s seconds --- UpdateDreck ---" %
#               (time.time() - start_time))  # Debug: Zeit stoppen
#         sys.stdout.flush()

#####################################################


# #### # Debug
# if __name__ == "__main__": # Debug
#     mess = MessdatenSammler("C:/test/")
#     mess.Debug()
