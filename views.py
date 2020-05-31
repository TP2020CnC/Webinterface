"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, url_for, request, redirect, jsonify, make_response, render_template
from Webinterface import app
from Webinterface.library.SteuerungGenerieren import AnfrageVerarbeiter
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
def urlOk(url):
    siteAvailable = True
    try:
        requests.get(url)
    except requests.exceptions.ConnectionError:
        return False
########################################################################################################
# Properties
########################################################################################################
#URL-Roboter
url = "http://178.202.120.28:8090"
#url = "http://192.168.0.95"
#url = "http://192.168.0.237"
siteAvailable = True
#Exceptionhandling Roboter nicht erreichbar
dirname = os.path.dirname(__file__)
mapFolder = os.path.join(dirname, "static/maps/")
dbLocation = os.path.join(dirname, "static/maps/messdaten.db")
curReg = AnfrageVerarbeiter(url)
png = pngZeichner(mapFolder)
parser = Parser(mapFolder)

########################################################################################################
# Routes
########################################################################################################
#Standardroute
@app.route('/')
@app.route('/Steuerung', methods=['POST', 'GET'])
def Steuerung2():
    """Renders the home page."""
    #Wenn Standardroute nicht erreichbar redirect zur Fehlerseite
    siteAvailable = urlOk(url)
    if siteAvailable == False:
        return redirect(url_for('Fehler'))
    return render_template(
        'Steuerung.html',
        title='Steuerung'
    )


@app.route('/Karte', methods=['GET'])
def Karte():
    """Renders the contact page."""
    #Wenn Standardroute nicht erreichbar redirect zur Fehlerseite
    siteAvailable = urlOk(url)
    if siteAvailable == False:
        return redirect(url_for('Fehler'))
    parser.BuildJSON(True)
    return render_template(
        'Karte.html',
        title='Karte',
    )

@app.route('/Verbindungsfehler')
def Fehler():
    """Renders the contact page."""
    return render_template(
        'Fehler.html',
        title='Verbindungsfehler'
    )

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
