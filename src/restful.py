#!flask/bin/python
from flask import Flask, jsonify, request, abort
import os
import json
import subprocess
import docker

app = Flask(__name__)


@app.route('/api/v1', methods=['GET'])
def apis_list():
    return jsonify({'response': True, 'status':200, 'comment': 'Hi, I am agento!'})


@app.route('/api/v1/monitor', methods=['PUT', 'DELETE'])
def monitor():

    options = ['mem', 'cpu', 'net'] # todo: from conffile
    sources = ['host', 'guest'] # todo: from conffile
    
    if request.method == 'PUT':
        payload = json.loads(request.data)
        if not payload['option'] in options:
            abort(404) # Raise an HTTPException with a 404 status code
        if not payload['source'] in sources:
            abort(400) # Raise an HTTPException with a 400 status code
        command = 'python monitor/monitor.py redis %s %s %s' % (payload['source'], payload['time'], payload['option'])
        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        return jsonify({
            'response': True,
            'method': request.method,
            'option':payload['option'], 
            'time': payload['time'],
            'source': payload['source']})

    elif request.method == 'DELETE':
        payload = json.loads(request.data)
        if payload['source'] == 'host' or payload['source'] == 'guest':
            command = "ps -elf | grep python | grep %s | grep %s | grep -v grep | awk '{print $4}'" % (payload['source'], payload['option'])
            command_ps = "ps -elf"
            command_grep1 = "grep python"
            command_grep2 = "grep %s" % (payload['source'])
            command_grep3 = "grep %s" % (payload['option'])
            command_grep4 = "grep -v grep"
            command_awk = ["awk", "{print $4}"]
        else:
            abort(400) # Raise an HTTPException with a 400 status code
        p_ps = subprocess.Popen(command_ps.split(), stdout=subprocess.PIPE)
        p_grep1 = subprocess.Popen(command_grep1.split(), stdin=p_ps.stdout, stdout=subprocess.PIPE)
        p_grep2 = subprocess.Popen(command_grep2.split(), stdin=p_grep1.stdout, stdout=subprocess.PIPE)
        p_grep3 = subprocess.Popen(command_grep3.split(), stdin=p_grep2.stdout, stdout=subprocess.PIPE)
        p_grep4 = subprocess.Popen(command_grep4.split(), stdin=p_grep3.stdout, stdout=subprocess.PIPE)
        p_awk = subprocess.Popen(command_awk, stdin=p_grep4.stdout, stdout=subprocess.PIPE)
        p_ps.stdout.close()
        pid = p_awk.communicate()[0].split("\n")[0]
        p_ps.wait()

        if not pid:
            abort(400) # Raise an HTTPException with a 400 status code
        p = subprocess.Popen(["kill", "-9", pid], stdout=subprocess.PIPE)
        
        return jsonify({
            'response': True,
            'status': 200})


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