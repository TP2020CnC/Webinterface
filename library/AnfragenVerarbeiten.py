#
# Name: AnfragenVerarbeiten.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Robin Schepp
# Co. Autor: Yannik Seitz
# Erstellt: 2020-05-20
# Letzte Änderung: 2020-06-2
#
# Der AnfrageVerarbeiter ist zentrales Element unserer Architektur und verarbeitet sowohl Anfragen von lokalen Programmen, wie
# auch vom ESP und vom Roboter selbst. 
# Von hier aus werden alle Programme bis auf die views.py aufgerufen und am laufen gehalten.
#

import json
import os
import sqlite3
import threading
import time
import urllib.parse
from builtins import print
from datetime import datetime
from multiprocessing.pool import ThreadPool
from urllib.request import Request, urlopen

import requests
from flask import (Flask, Response, jsonify, make_response, redirect,
                   render_template, request, url_for)

from Webinterface import app
from Webinterface.library.DatenbankVerwalten import \
    DatenbankVerwalter as database
from Webinterface.library.KartenUpdater import KartenDebugger, KartenUpdater

_KILL = True

# Hält Updatevorgang am laufen -> Karte für Weboberfläche
def Worker_KartenUpdater(path, url):
    """thread worker function"""
    ku = KartenUpdater(path, url)
    repeatCounter = -1
    running = False
    while 1:
        repeatCounter += 1
        if _KILL:
            break
        try:
            if running: 
                ku.UpdateDreck()
            if repeatCounter % 10 == 0:
                ku.UpdateJSON()

                response = urlopen(url + "/api/current_status")
                string = response.read().decode('utf-8')
                currState = json.loads(string) 
                if currState["human_state"] == "Cleaning":
                    running = True
                else:
                    running = False
        except Exception as e:
            print(e)
    return

# def Worker_KartenDebugger(path): # DEBUG # DEBUG # DEBUG 
#     """thread worker function"""
#     kd = KartenDebugger(path)
#     while 1:
#         if _KILL:
#             break
#         try:
#             kd.InsertDebugDirt()
#             time.sleep(0.2)
#         except Exception as e:
#             print(e)
#     return


class AnfrageVerarbeiter(object):
    """Diese Klasse generiert Aktionen, die auf Nutzereingaben zurückführen"""

    def __init__(self, currUrl):
        # Roboter URL wird übergeben
        self.url = currUrl
        # Die nächsten drei Zeilen wird die Aktuelle Statusmeldung angefragt und in ein Python Dictionary umgewandelt
        response = urlopen(self.url + "/api/current_status")
        string = response.read().decode('utf-8')
        self.currState = json.loads(string)
        # Klassenvariablen werden initialisiert
        self.jobs = []
        self.payload = {}
        # Der Header für die http PUT-Request zum senden des Fanmode (Robotermodus) wird initialisiert
        self.headers = {"content-type": "application/json",
               "Authorization": "<auth-key>"}
        # Ein Datenbankverwalter zum Eintragen und Löschen der Datenbank
        self.db = database()
    # Die Datei dreck.json wird geleert und so resettet
    def ResetDreckJson(self, path):
        data = {}
        data["dirt"] = []
        with open(path + "dreck.json", "w") as write_file:
            json.dump(data, write_file)
    
    # Startet Kartenupdatevorgang
    def StartKartenUpdater(self, mapLocation, url):   
        global _KILL
        if _KILL == True:
            self.jobs = []  
            _KILL = False
            t1 = ThreadPool(processes=1)
            t1.apply_async(Worker_KartenUpdater, args=(mapLocation,url))
            self.jobs.append(t1)
            #t2 = ThreadPool(target=Worker_KartenDebugger, args=(mapLocation,)) # DEBUG 
            #self.jobs.append(t2)

    # Stoppt Kartenupdatevorgang
    def StopKartenUpdater(self):
        global _KILL
        _KILL = True
        for job in self.jobs:
            job.terminate()
            job.join()

    # Statusinformationen werden abgerufen
    def getCurrentState(self):
        response = urlopen(self.url + "/api/current_status")
        string = response.read().decode('utf-8')
        self.currState = json.loads(string)

    #  Holt die gezippte Kartendatei in Bytecode zerlegt und speichert sie an angegebener Stelle
    def download_url(self, url, save_path):
        r = requests.get(url)
        open(save_path, 'wb').write(r.content)

    # Anfragen über die api/ Schnittstelle werden nach Methode und Befehl der Website (robot_mode) gefiltert und verarbeitet.
    # Die Daten werden über die HTTP Schnittstelle des Valetudo Webservers auf dem Roboter angefragt.
    # Verwendete lokale Dateien sind die karte.json und dreck.json 
    def verarbeiteAnfrage(self, method, robot_mode, myResponse="not_useable", mapBuilder="not_useable", mapFolder="not_useable", mapParser="not_usable", dbLocation="not_useable", request="not_useable"):
        # Wenn es sich um eine PUT-Request handelt
        if method == "PUT":
            # startet Roboter
            if robot_mode == "start":
                requests.put(self.url + "/api/start_cleaning")
                # startet das regelmäßige erneuern des Json Strings, welcher von Website verarbeitet und Dargestellt wird
                self.StartKartenUpdater(mapFolder, self.url)
            # stoppt Roboter
            elif robot_mode == "stop":
                requests.put(self.url + "/api/stop_cleaning")
            # pausiert Roboter
            elif robot_mode == "pause":
                requests.put(self.url + "/api/pause_cleaning")
            # Roboter macht auf sich aufmerksam
            elif robot_mode == "find":
                requests.put(self.url + "/api/find_robot")
            # Roboter fährt zum Dock zurück
            elif robot_mode == "home":
                requests.put(self.url + "/api/drive_home")
                # Tabelle mit Dreckdaten wird gelöscht
                self.db.delTable(dbLocation)
                # dreck.json wird geleert
                self.ResetDreckJson(mapFolder)
            # Die nächsten Zeilen tragen den Bodycontent für für PUT Anfrage zum setzen des Fanmode ein
            elif robot_mode == "whisper":
                self.payload = {'speed': '1'}
            elif robot_mode == "quiet":
                self.payload = {'speed': '38'}
            elif robot_mode == "balanced":
                self.payload = {'speed': '60'}
            elif robot_mode == "turbo":
                self.payload = {'speed': '75'}
            elif robot_mode == "max":
                self.payload = {'speed': '100'}
            elif robot_mode == "mop":
                self.payload = {'speed': '105'}
            # Testdreckdaten werden in Datenbank eingetragen
            elif robot_mode == "dustTest":
                self.db.insertTestData(dbLocation)
        # Wird ausgeführt, wenn es sich um eine GET-Request handelt
        elif method == "GET":
            # Aktueller Status des Roboters wird Angefragt
            if robot_mode == "state":
                self.getCurrentState()
                # Antwort geht als Json-String zurück (wird von JavaScript auf der Website verarbeitet)
                return jsonify({'battery': self.currState["battery"], 'clean_area': self.currState["clean_area"], 'fan_power': self.currState["fan_power"], 'human_state': self.currState["human_state"]})
            # Liefert die gezippte Kartendatei mit allen Positionskoordinaten in Bytecode zerlegt zurück            
            elif robot_mode == "latest":
                # Speichert die Datei vom Roboter als karte.gz
                self.download_url((self.url + "/api/map/latest"), mapFolder + "karte.gz")
            # Liefert die karte.json mit allen Koordinaten zurück -> Weboberfläche
            elif robot_mode == "map":
                f = open(mapFolder + "karte.json", "r")
                #return jsonify(json.loads(f.read()))
                return f.read()
        # Bei Postanfragen verwendet
        elif method == "POST":
            # Hiermit werden Verschmutzungsdaten einzeln hingeschickt und gespeichert
            if robot_mode == "setDirt":
                # Speichert Verschmutzungsdaten ab
                self.db.updateDatabase(dbLocation, request.get_json(force=True))
        # Wenn payload nicht leer ist (für den fanmode muss noch die request gesendet werden)
        if self.payload != "":
            # Request wird gestellt -> Fanmode wird gesetzt
            requests.put((self.url + "/api/fanspeed"),data=json.dumps(self.payload), headers=self.headers)
            # Wenn alles gut kommt ok gut zurück
            return jsonify({'message': "ok gut"})
