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
import os

'''
congestions={
    "time":"",
    "congestions":[],
    "region":"",}

congestion={
    "commune":"",
    "duration_hours":"",
    "extension_km":"",
    "origin_axes":"",
    "jamLevel":"",
    "time_init":"",
    "time_end":"",
    "duration_hours":"",
    "speed_kmh":"",
    "axe":"",
    "line":[],
    "subroutes":[],
}
line={
    "geoposition":{
        "latitude":"",
        "longitude":""}
}
subroutes={
    "toName": "",
    "line": [],
    "fromName": "",
    "length": "",
    "jamLevel": "",
    "time": ""}

line_subroutes={
    "geoposition": {
        "latitude": "",
        "longitude": ""
                    }
}
'''


endpoints_fotografias = Blueprint('endpoints_fotografias', __name__)
def get_endpoints():
    return endpoints_fotografias

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
def process_coordinates(points):

    # Renombrar x por longitud y y por latitud
    for point in points:
        point['longitude'] = point.pop('x')
        point['latitude'] = point.pop('y')
    
    # Seleccionar el primer y último punto y un 30% de puntos intermedios
    num_points = len(points)
    indices = [0] + [i for i in range(1, num_points-1, 7) if i < num_points]+ [num_points-1]
    selected_points = [points[i] for i in indices]
    
    return selected_points

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



data_path="/home/ubuntu/uoct_super_lunes/data/congestiones_fotografia"
r = redis.Redis(host='localhost', port=6379, db=0)

@endpoints_fotografias.route("/api/uoct/map/fotografia/<string:region>/", methods=["GET"])
def get_fotografias(region):
    path=os.path.join(data_path,region,"hora_mas_congestionada.csv")
    if r.get(f"{region}/fotografia"):
        print(f"{region}/fotografia")
        return jsonify(json.loads(r.get(f"{region}/fotografia")))
    else:
        congestions = {
                
                "congestions": [],
                "region": region,
            }
        error_read=False
        # abrir carpeta en base a una ruta
        try:
            df = pd.read_csv(path, delimiter=';')
            
        except:
            error_read=True
            
        if error_read==True:
            congestions["congestions"]= [],     
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
                    "axe": row[5],
                    "buses_hora": row[20],
                },
                "line_lite": select_intermediate_points(row["coordinates"]),
                "line": json.loads(row[19].replace("'", "\"").replace("x", "longitude").replace("y", "latitude"))
            }), axis=1)
        r.set(f"{region}/fotografia", json.dumps(congestions))
        return jsonify(congestions)
                    
                    
            
    
    
