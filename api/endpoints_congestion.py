from flask import Flask,jsonify,render_template,request,Blueprint
import sqlite3
import json
import uuid
from flask import abort
from flask import Response
import time
from functools import wraps
import jwt
import csv
import pandas as pd
import redis


endpoints_congestion = Blueprint('endpoints_congestion', __name__)
def get_endpoints():
    return endpoints_congestion

def requires_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing.'}), 401
        try:
            data = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid.'}), 401
        return f(*args, **kwargs)
    return decorated

# Función para seleccionar los puntos intermedios de la lista de coordenadas
def select_intermediate_points(coords):
    num_points = len(coords)
    first_point = coords[0]
    last_point = coords[-1]
    intermediate_points = []
    if num_points > 2:
        for i in range(1, num_points - 1):
            if i % 5 == 0: # selección del 20% de los puntos intermedios
                intermediate_points.append(coords[i])
    
    lista = []
    lista.append(first_point)
    for i in intermediate_points:
        lista.append(i)
    lista.append(last_point)
    return lista


data_path="/home/ubuntu/uoct_super_lunes/data/congestiones"
r = redis.Redis(host='localhost', port=6379, db=0)


@endpoints_congestion.route("/api/uoct/map/<string:region>/congestion/<string:day>/", methods=["GET"])
def get_congestions(region, day):
    
    filter_time = request.args.get('time')
    #si la respuesta esta en cache, retornarla
    if r.get(f"{region}/{day}/{filter_time}"):
        print(f"{region}/{day}/{filter_time}")
        return jsonify(json.loads(r.get(f"{region}/{day}/{filter_time}")))
    else:
        congestions = {
            "time": "",
            "congestions": [],
            "region": region,
        }
        congestions["time"] = filter_time
        error_read=False
        # abrir carpeta en base a una ruta
        try:
            df = pd.read_csv(f"{data_path}/{region}/{day}/{filter_time}.csv", delimiter=';')
            
        except:
            error_read=True
            
        if error_read==True:
            None   
        else:
            df["coordinates"] = df.apply(lambda row: json.loads(row[19].replace("'", "\"").replace("x", "longitude").replace("y", "latitude")), axis=1)

            
            df.apply(lambda row: congestions["congestions"].append({
                "body": {
                    "commune": row[2],
                    "duration_hours": row[8],
                    "extension_km": row[10],
                    "origin_axes": row[18],
                    "jamLevel": 4,
                    "time_init": row[6],
                    "time_end": row[7],
                    "speed": row[11],
                    "axe": row[5]
                },
                "line_lite": select_intermediate_points(row["coordinates"]),
                "line": json.loads(row[19].replace("'", "\"").replace("x", "longitude").replace("y", "latitude"))
            }), axis=1)
        r.set(f"{region}/{day}/{filter_time}", json.dumps(congestions))
        return jsonify(congestions)

