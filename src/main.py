#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Agento RESTful App

    This application implements a RESTful server to manage 
    the following operations:
        - monitor;
        - deploy.

    TODO

    The scope of the application is academic research.
    It is part of the Osmotic Computing activities carried 
    out at both University of Messina and TU Wien.
"""

__author__ = "Lorenzo Carnevale"
__copyright__ = None
__credits__ = ["Lorenzo Carnevale"]
__license__ = None
__version__ = "1.1"
__maintainer__ = "Lorenzo Carnevale"
__email__ = "lcarnevale@unime.it"
__status__ = "Prototype"


import json
import docker
from flask import Flask
from flask import jsonify
from flask import request
from flask import abort
from apis.welcome.route import route_rules
from apis.monitor.monitor_manager import MonitorManager


app = Flask(__name__)


@app.route('/api/v1', methods=['GET'])
def apis_list():
    data = route_rules(app)
    # return route_table(data)
    return jsonify({'response': True, 
        'content': data, 
        'status':200, 
        'comment': 'Hi, I am agento!'
    })


@app.route('/api/v1/monitor/<resource>/<target>', methods=['PUT', 'DELETE'])
def monitor(resource, target):

    monitorManager = MonitorManager(resource, target, request.data)
    return monitorManager.run(request.method)


@app.route('/api/v1/deploy', methods=['PUT', 'DELETE'])
def deploy():

    payload = json.loads(request.data)
    client = docker.from_env()
    
    if request.method == 'PUT':
        client.containers.run(
            payload['image'],
            command=payload['command'],
            name=payload['name'],
            privileged=payload['privileged'],
            ports=payload['ports'],
            volumes=payload['volumes'],
            detach=True)

    if request.method == 'DELETE':
        try:
            client.containers.get(payload['name']).stop()
            client.containers.get(payload['name']).remove()
            client.images.remove(payload['image'])
        except docker.errors.NotFound as e:
            abort(400) # Raise an HTTPException with a 400 status code
        except docker.errors.APIError as e:
            abort(409) # Raise an HTTPException with a 409 status code

    return  jsonify({
        'response': True,
        'status': 200})