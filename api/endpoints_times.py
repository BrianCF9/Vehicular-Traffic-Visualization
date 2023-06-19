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
import datetime

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


endpoints_times = Blueprint('endpoints_times', __name__)
def get_endpoints():
    return endpoints_times

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



data_path="/home/ubuntu/uoct_super_lunes/data/tiempos_de_viaje"
r = redis.Redis(host='localhost', port=6379, db=0)


@endpoints_times.route("/api/uoct/map/Metropolitana/times/displacement", methods=["GET"])
def get_times_pairs():
    path=os.path.join(data_path,"tiempo_viajes_pares_origen_destino.csv")
    arcs={
    "arcs":[],
    "region":"Metropolitana",}
    with open(path, 'r') as f:
        runner=0
        reader = csv.reader(f)
        for row in reader:
            try:
                row=row[0].split(";")
            except:
                row=[]
            
            if runner==0:
                runner=1
            else:
                if row.__len__()>0:

                    congestion={"body":{
                        "extension_km":row[8],
                        "origin_axes":row[1],
                        "destination_axes":row[2],
                        "sentido":row[3],
                        "distance":row[8],
                        "time_init":row[9],
                        "retard":row[10],
                        },
                        "from":{
                            "latitude":row[5],
                            "longitude":row[4]
                            },
                        "to":{
                            "latitude":row[7],
                            "longitude":row[6]
                        }
                    }
                    arcs["arcs"].append(congestion)
                    
                    
            
    
        

    return jsonify(arcs)









    
@endpoints_times.route("/api/uoct/map/Metropolitana/times/axes", methods=["GET"])
def get_times_axes():
    path=os.path.join(data_path,"tiempos_de_viajes_por_eje.csv")
    axes={
    "time":"",
    "axes":[],
    "region":"Metropolitana",}
    with open(path, 'r') as f:
        runner=0
        reader = csv.reader(f)
        for row in reader:
            if runner==0:
                
                runner=1
            else:
                if row.__len__()>0:
                    
                    axes["time"]=row[6]+" - "+row[7] +" AM"
                    
                    congestion={"body":{
                        "extension_km":row[5],
                        "origin_axes":row[3],
                        "jamLevel":4,
                        "time_init":row[6],
                        "time_end":row[7],
                        "time1":row[11],
                        "time2":row[10],
                        "time3":row[9],
                        "time4":row[8],
                        "axe":row[4]
                        },
                        "line_lite": select_intermediate_points(json.loads(str(row[12]).replace("'", "\"").replace("x", "longitude").replace("y", "latitude"))),
                        "line": json.loads(str(row[12]).replace("'", "\"").replace("x", "longitude").replace("y", "latitude")),
                    }
                    axes["axes"].append(congestion)
                    
                    
            
    
        return jsonify(axes)
    



