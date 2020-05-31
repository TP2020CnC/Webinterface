"""
The flask application package.
"""

from flask import Flask
app = Flask(__name__)

import Webinterface.views
import Webinterface.library.SteuerungGenerieren
import Webinterface.library.KartenParser
