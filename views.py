"""
Routes and views for the flask application.
"""
#
# Name: views.py
# Projekt: FS4V Abschlussprojekt Staubsaugerroboter
# Schule: Heinrich-Emanuel-Merck-Schule
# Betrieb: COUNT+CARE
# Autor: Robin Schepp
# Erstellt: 2020-05-20
# Letzte Änderung: 2020-06-2
#
# In Views befinden sich alle Routen, die Über den Webserver erreichbar sind.
# Auch die APIs sind hier erreichbar und werden über den Übergabeparameter robot_mode angesprochen.
#

from datetime import datetime
from flask import Flask, url_for, request, redirect, jsonify, make_response, render_template
from Webinterface import app
from Webinterface.library.AnfragenVerarbeiten import AnfrageVerarbeiter
from Webinterface.library.pngZeichner import pngZeichner
from Webinterface.library.KartenParser import Parser
import json
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import requests
import urllib.parse
import os

########################################################################################################
# Functions
########################################################################################################
# Testet, ob Roboter erreichbar ist
def urlOk(url):
    siteAvailable = True
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
########################################################################################################
# Properties
########################################################################################################
# URL-Roboter
#url = "http://178.202.120.28:8090"
url = "http://192.168.0.95"
#url = "http://192.168.0.237"
# Hilfvariable Roboter erreichbar
siteAvailable = True
# Findet aktuelles Verzeichnis heraus
dirname = os.path.dirname(__file__)
# Verzeichnis der benötigten Karten-Dateien
mapFolder = os.path.join(dirname, "static/maps/")
# Pfad zur Datenbank-Datei
dbLocation = os.path.join(dirname, "static/maps/messdaten.db")
# Current Request, Verarbeitet die aktuelle Anfrage, ein Objekt der Klasse AnfragenVerarbeiten
curReg = AnfrageVerarbeiter(url)
# Erstellt aus dem Klabumbatsch vom Roboter, einen Lesbaren Json-String
parser = Parser(mapFolder)
png = pngZeichner(mapFolder)
########################################################################################################
# Routes
########################################################################################################
# Standardroute
@app.route('/')
@app.route('/Steuerung', methods=['POST', 'GET'])
def Steuerung2():
    """Renders the home page."""
    # Wenn Standardroute nicht erreichbar redirect zur Fehlerseite
    siteAvailable = urlOk(url)
    if siteAvailable == False:
        return redirect(url_for('Fehler'))
    return render_template(
    'Steuerung.html',
    title='Steuerung'
    )

# Route zur Karte
@app.route('/Karte', methods=['GET'])
def Karte():
    """Renders the contact page."""
    # Wenn Standardroute nicht erreichbar redirect zur Fehlerseite
    siteAvailable = urlOk(url)
    if siteAvailable == False:
        return redirect(url_for('Fehler'))
    parser.BuildJSON(True)
    return render_template(
        'Karte.html',
        title='Karte',
    )

# Route zur Fehlerseite 
@app.route('/Verbindungsfehler')
def Fehler():
    """Renders the contact page."""
    return render_template(
        'Fehler.html',
        title='Verbindungsfehler'
    )

# Route zur API mit Übergabeparameter, der als robot_mode in das Objekt verarbeiteAnfrage übergeben wird
# Vorselektiert durch Methode und bestimmt so die Übergabeparameter
@app.route('/api/<string:robot_mode>', methods=['PUT', 'GET', 'POST'])
def sendInstruction(robot_mode):
    #Wenn Standardroute nicht erreichbar redirect zur Fehlerseite
    siteAvailable = urlOk(url)
    if siteAvailable == False:
        return redirect(url_for('Fehler'))
    if request.method == "PUT":
        return curReg.verarbeiteAnfrage("PUT", robot_mode, "nothing", png, mapFolder, parser, dbLocation, request)
    elif request.method == "GET":
        return curReg.verarbeiteAnfrage("GET", robot_mode, request.args.get("mapMode"), png, mapFolder, parser, dbLocation, request)
    elif request.method == "POST":
        return curReg.verarbeiteAnfrage("POST", robot_mode, request.args.get("mapMode"), png, mapFolder, parser, dbLocation, request)
    return jsonify({'message': "nicht_ganz_so_ok"})
