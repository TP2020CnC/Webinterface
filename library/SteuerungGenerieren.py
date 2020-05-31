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
        self.url = currUrl
        response = urlopen(self.url + "/api/current_status")
        string = response.read().decode('utf-8')
        self.currState = json.loads(string)
        self.jobs = []
        self.payload = {}
        self.headers = {"content-type": "application/json",
               "Authorization": "<auth-key>"}
        self.db = database()

    def ResetDreckJson(self, path):
        data = {}
        data["dirt"] = []
        with open(path + "dreck.json", "w") as write_file:
            json.dump(data, write_file)
    
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
 
    def download_url(self, url, save_path):
        r = requests.get(url)
        open(save_path, 'wb').write(r.content)

    # Anfragen über die api/ Schnittstelle werden nach Methode und Befehl der Website (robot_mode) gefiltert und verarbeitet.
    # Die Daten werden über die HTTP Schnittstelle des Valetudo Webservers auf dem Roboter angefragt.
    # Verwendete lokale Dateien sind die karte.json und dreck.json 
    def verarbeiteAnfrage(self, method, robot_mode, myResponse="not_useable", mapBuilder="not_useable", mapFolder="not_useable", mapParser="not_usable", dbLocation="not_useable", request="not_useable"):
        if method == "PUT":
            # startet Roboter
            if robot_mode == "start":
                requests.put(self.url + "/api/start_cleaning")
                # startet das regelmäßige erneuern des Json Strings, welcher von Website verarbeitet und Dargestellt wird
                self.StartKartenUpdater(mapFolder, self.url)
            # stoppt Roboter
            elif robot_mode == "stop":
                requests.put(self.url + "/api/stop_cleaning")
            elif robot_mode == "pause":
                requests.put(self.url + "/api/pause_cleaning")
            elif robot_mode == "find":
                requests.put(self.url + "/api/find_robot")
            elif robot_mode == "home":
                requests.put(self.url + "/api/drive_home")
                self.db.delTable(dbLocation)
                self.ResetDreckJson(mapFolder)
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
            elif robot_mode == "dustTest":
                self.db.insertTestData(dbLocation)
        elif method == "GET":
            if robot_mode == "state":
                self.getCurrentState()
                return jsonify({'battery': self.currState["battery"], 'clean_area': self.currState["clean_area"], 'fan_power': self.currState["fan_power"], 'human_state': self.currState["human_state"]})
            elif robot_mode == "karte":
                pass
            elif robot_mode == "latest":
                self.download_url((self.url + "/api/map/latest"), mapFolder + "karte.gz")
            elif robot_mode == "map":
                f = open(mapFolder + "karte.json", "r")
                #return jsonify(json.loads(f.read()))
                return f.read()
        elif method == "POST":
            if robot_mode == "setDirt":
                self.db.updateDatabase(dbLocation, request.get_json(force=True))
        if self.payload != "":
            requests.put((self.url + "/api/fanspeed"),data=json.dumps(self.payload), headers=self.headers)
            return jsonify({'message': "ok gut"})
        else:
            return jsonify({'message': "ok"})
