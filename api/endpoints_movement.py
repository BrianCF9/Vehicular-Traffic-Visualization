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


endpoints_movements = Blueprint('endpoints_movements', __name__)
def get_endpoints():
    return endpoints_movements

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



data_path="/home/ubuntu/uoct_super_lunes/data/movements"
r = redis.Redis(host='localhost', port=6379, db=0)


@endpoints_movements.route("/api/uoct/map/<string:region>/movement/<string:year>", methods=["GET"])
def get_congestions(region,year):
    filter_time = request.args.get('time')
    #si la respuesta esta en cache, retornarla
    if r.get(f"{region}/{filter_time}/{year}"):
        print(f"{region}/{filter_time}/{year}")
        return jsonify(json.loads(r.get(f"{region}/{filter_time}/{year}")))
    else:
        movements = {
            "time": "",
            "movements": [],
            "region": region,
        }
        movements["time"] = filter_time
        error_read=False
        # abrir carpeta en base a una ruta
        try:
            # leer archivo json
            with open(f"{data_path}/{year}/{region}/{filter_time}.json", "r") as f:
                data = json.load(f)
        except:
            error_read=True
            
        if error_read==True:
            None,     
        else:
            for i in data:
                

                body = {
                    "duration_hours": i["time"],
                    "extension_km": i["length"],
                    "origin_axes": i["fromName"],
                    "jamLevel": i["jamLevel"],
                    "axe":i["toName"],
                }
                line_lite=process_coordinates(i["line"])
                line= json.loads(str(i["line"]).replace("'", "\"").replace("x", "longitude").replace("y", "latitude"))
                
                movements["movements"].append({"body":body,"line":line,"line_lite":line_lite})

        r.set(f"{region}/{filter_time}/{year}",json.dumps(movements))
        return jsonify(movements)



