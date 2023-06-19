from flask import Flask,jsonify,render_template,request,Blueprint
import sqlite3
import json
import uuid
from flask import abort
from flask import Response
import time
from functools import wraps
import jwt

endpoints_map = Blueprint('endpoints_map', __name__)
def get_endpoints():
    return endpoints_map

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



@endpoints_map.route('/<string:project_name>/map/', methods=["GET"])
def map_route(project_name):
    routes={
        "project_name":project_name,
        "regiones":[{ "region":"Gran Concepción",
                "congestion":[{"date":"06_03_2023","url":"/api/uoct/map/Concepcion/congestion/06_03_2023/?time=", "max_value":1.0},
                    {"date":"07_03_2022","url":"/api/uoct/map/Concepcion/congestion/07_03_2022/?time=", "max_value":1.0},
                              ],
                "fotografia":[{"date":"06_03_2023","url":"/api/uoct/map/fotografia/BioBio/"}],
                "modal":[],
                "movements":[{"date":"06_03_2023","url":"/api/uoct/map/Concepcion/movement/2023?time=","max_value": 0.77},
                    {"date":"07_03_2022","url":"/api/uoct/map/Concepcion/movement/2022?time=","max_value":1.0},
                             ],
                "obras":[{ "date":"06_03_2023","url":"/api/uoct/map/Concepcion/services/obras"}],
                "time_displacement":[],
                "time_axes":[],
                "geoposition":{
                    "latitude":-36.820135,
                    "longitude":-73.044390,
                }
            },
            { "region":"Gran Valparaíso",
                "congestion":[{"date":"07_03_2022","url":"/api/uoct/map/Valparaiso/congestion/07_03_2022/?time=", "max_value":1.0}],
                "fotografia":[{"date":"06_03_2023","url":"/api/uoct/map/fotografia/Valparaiso/",}],
                "modal":[],
                "movements":[{"date":"06_03_2023","url":"/api/uoct/map/Valparaiso/movement/2022?time=","max_value": 0.77},
                             {"date":"07_03_2022","url":"/api/uoct/map/Valparaiso/movement/2022?time=","max_value":1.0}
                             ],
                "obras":[],
                "time_displacement":[],
                "time_axes":[],
                "geoposition":{
                    "latitude":-33.047238,
                    "longitude":-71.612688,
                }
                
            },
            { 
             "region":"Gran Santiago",
                "congestion":[{"date":"06_03_2023","url":"/api/uoct/map/Metropolitana/congestion/06_03_2023/?time=", "max_value":1.0},
                              {"date":"07_03_2022","url":"/api/uoct/map/Metropolitana/congestion/07_03_2022/?time=", "max_value":1.0},
                             
                              ],
                "fotografia":[{"date":"06_03_2023","url":"/api/uoct/map/fotografia/Metropolitana/","max_value": 0.77 }],
                "modal":[{"date":"06_03_2023","url":"/api/uoct/map/Metropolitana/modal/"}],
                "movements":[{"date":"06_03_2023","url":"/api/uoct/map/Metropolitana/movement/2023?time=", "max_value": 0.77},
                    {"date":"09_11_2022","url":"/api/uoct/map/Metropolitana/movement/2022?time=", "max_value":1.0},
                             ],
                "obras":[{"date":"06_03_2023","url":"/api/uoct/map/Metropolitana/services/obras"}],
                "time_displacement":[{"date":"06_03_2023","url":"/api/uoct/map/Metropolitana/times/displacement","max_value": 0.77}],
                "time_axes":[{"date":"06_03_2023","url":"/api/uoct/map/Metropolitana/times/axes","max_value": 0.77}],
                "geoposition":{
                    "latitude":-33.437796,
                    "longitude":-70.650445,
                }
                
            },
            { "region":"Rancagua-Machalí",
                "congestion":[{"date":"07_03_2022","url":"/api/uoct/map/Rancagua/congestion/07_03_2022/?time=", "max_value":1.0}],
                "fotografia":[{"date":"06_03_2023","url":"/api/uoct/map/fotografia/BernardoOHiggins/"}],
                "modal":[],
                "movements":[{"date":"06_03_2023","url":"/api/uoct/map/Rancagua/movement/2023?time=", "max_value": 0.77},
                    {"date":"07_03_2022","url":"/api/uoct/map/Rancagua/movement/2022?time=", "max_value":1.0},
                             ],
                "obras":[],
                "time_displacement":[],
                "time_axes":[],
                "geoposition":{
                    "latitude":-34.170555,
                    "longitude":-70.740555,
                }
                
                
            },
            { "region":"Temuco-Padre Las Casas",
                "congestion":[{"date":"07_03_2022","url":"/api/uoct/map/Temuco/congestion/07_03_2022/?time=", "max_value":1.0},
                              ],
                "fotografia":[{"date":"06_03_2023","url":"/api/uoct/map/fotografia/Araucania/"}],
                "modal":[],
                "movements":[{"date":"06_03_2023","url":"/api/uoct/map/Temuco/movement/2023?time=", "max_value": 0.77},
                    {"date":"07_03_2022","url":"/api/uoct/map/Temuco/movement/2022?time=","max_value":1.0},
                             ],
                "obras":[],
                "time_displacement":[],
                "time_axes":[],
                "geoposition":{
                    "latitude":-38.739167,
                    "longitude":-72.598889,
                }
                
            },               
            { "region":"La Serena-Coquimbo",
                "congestion":[],
                "fotografia":[{"date":"06_03_2023","url":"/api/uoct/map/fotografia/Coquimbo/"}],
                "modal":[],
                "movements":[],
                "obras":[],
                "time_displacement":[],
                "time_axes":[],
                "geoposition":{
                    "latitude":-29.953333,
                    "longitude":-71.343333,
                }
            }
        ]
        
    }
    
    return jsonify(routes)
