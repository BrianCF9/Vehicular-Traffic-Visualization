from flask import Flask,jsonify,render_template,request
import sqlite3
import json
import uuid
from flask import abort
from flask import Response
import time
import logging
import jwt
import datetime
import redis





from endpoints_map import get_endpoints as map_endpoints
from endpoints_services import get_endpoints as services_endpoints
from endpoints_congestion import get_endpoints as congestion_endpoints
from endpoints_movement import get_endpoints as movement_endpoints
from endpoints_modal import get_endpoints as modal_endpoints
from endpoints_times import get_endpoints as times_endpoints
from endpoints_fotografia import get_endpoints as fotografia_endpoints

app = Flask(__name__)
app.register_blueprint(map_endpoints())
app.register_blueprint(services_endpoints())
app.register_blueprint(congestion_endpoints())
app.register_blueprint(movement_endpoints())
app.register_blueprint(modal_endpoints())
app.register_blueprint(times_endpoints())
app.register_blueprint(fotografia_endpoints())

if __name__== "__main__":
    # Agregar un manejador de archivo para los logs
    #logging.basicConfig(filename='/home/ubuntu/uoct_super_lunes/logs/app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    app.run(host='0.0.0.0', port=8000, debug = False, threaded = True)