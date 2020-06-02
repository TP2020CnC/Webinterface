#
# Name: kartenUpdate.py.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Yannik Seitz
# Erstellt: 2020-05-23
# Letzte Änderung: 2020-05-29
#
# Der KartenUpdater wird von der Worker-Funktion aus dem AnfragenVerwalten.py aufgerufen
# Das Verzeichnis und die Roboter-URL wird im Konstruktor der Klasse mitgegeben.
#


try:
    from Webinterface.library.MessdatenSammeln import MessdatenSammler
    from Webinterface.library.KartenParser import Parser
    #from Webinterface.library.DatenbankVerwalten import DatenbankVerwalter  # DEBUG
except:
    from MessdatenSammeln import MessdatenSammler
    from KartenParser import Parser
    #from DatenbankVerwalten import DatenbankVerwalter  # DEBUG
import json
import random
import time
import requests

#from multiprocessing import Process  # DEBUG




class KartenUpdater:
    def __init__(self, file_path, url):
        self.mds = MessdatenSammler(file_path)
        self.par = Parser(file_path)
        self.FILE_PATH = file_path
        self.url = url

    def current_milli_time(self):
        """
        Aktuelle Zeit in Millisekunden

        :return:			int
        """
        return int(round(time.time() * 1000))

    def UpdateJSON(self):
        """
        karte.json aktualisieren

        """
        try:
            self.ApiRequest()
            self.par.BuildJSON(True)
        except Exception as e:
            print(e)

    def UpdateDreck(self):
        """
        dreck.json aktualisieren
        
        """
        try:
            self.ApiRequest()
            roboPos = self.par.GetRoboPos()
            self.mds.UpdateDreck(roboPos)
        except Exception as e:
            print(e)

    def ApiRequest(self):
        """
        karte.gz vom Roboter anfragen
        
        """
        r = requests.get(self.url + "/api/map/latest")
        open(self.FILE_PATH + "karte.gz", 'wb+').write(r.content)


    # def UpdateDebugger(self, repeatCounter):  # DEBUG  # DEBUG  # DEBUG  # DEBUG  # DEBUG
    #     try:
    #         self.ApiRequest()
    #         roboPos = self.par.GetRoboPos()
    #         self.mds.UpdateDreckDebug(roboPos)
    #         if repeatCounter % 10 == 0:
    #             self.par.BuildJsonDebug(True)
    #             print(repeatCounter) # DEBUG
    #             #self.png.ImageBuilderDebug(True, True)
    #     except Exception as e:
    #         print(e)
    

# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG# DEBUG
# class KartenDebugger:   # DEBUG
#     def __init__(self, file_path):
#         self.db = DatenbankVerwalter()
#         self.FILE_PATH = file_path
#         self.repeatCounter = 0

#     def InsertDebugDirt(self):
#         self.db.updateDatabase(self.FILE_PATH + "messdaten.db", {
#             "typ": "DRECK",
#             "sensornummer": 1,
#             "millisekunden": self.current_milli_time(),
#             "messwert": 0
#         })
#         self.repeatCounter += 1

#     def ResetSQL(self):
#         self.db.delTable(self.FILE_PATH + "messdaten.db")


# def worker2(num):
#     """thread worker function"""
#     kd = KartenDebugger("C:/test/")
#     kd.ResetSQL()
#     while 1:
#         kd.InsertDebugDirt()
#         time.sleep(0.2)
#     return


# def worker1(num):
#     """thread worker function"""
#     ku = KartenUpdater("C:/test/", "http://192.168.0.237")
#     ku.Update()
#     return


# def main():
#     jobs = []
#     t1 = Process(target=worker1, args=(1,))
#     t1.start()
#     jobs.append(t1)
#     t2 = Process(target=worker2, args=(1,))
#     t2.start()
#     jobs.append(t2)
#     while 1:
#         pass


# if __name__ == "__main__":
#     main()
