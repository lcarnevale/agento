#!flask/bin/python
from flask import Flask, jsonify, request, abort
import os, json

app = Flask(__name__)


@app.route('/api/v1', methods=['GET'])
def apis_list():
    return jsonify({'response': True, 'comment': 'I want you back free!'})


@app.route('/api/v1/monitor/<string:option>', methods=['PUT', 'DELETE'])
def monitor(option):

    options = ['mem', 'cpu', 'net'] # from conffile
    
    if not option in options:
        # Raise an HTTPException with a 404 not found status code
        abort(404)

    if request.method == 'PUT':
        payload = json.loads(request.data)
        if payload['source'] == 'host':
            command = 'python monitor_host.py %s %s &' % (payload['time'], option)
        elif payload['source'] == 'guest':
            command = 'python monitor_guest.py %s %s &' % (payload['time'], option)
        else:
            abort(400)
        #os.popen(command)
        os.system(command)
        return jsonify({
            'response': True,
            'method': request.method,
            'option':option, 
            'time': payload['time'],
            'source': payload['source']})

    elif request.method == 'DELETE':
        payload = json.loads(request.data)
        if payload['source'] == 'host' or payload['source'] == 'guest':
            command = "ps -elf | grep python | grep %s |grep %s | grep -v grep | awk '{print $4}'" % (payload['source'], option)
        else:
            abort(400)
        pid =  os.popen(command).read().split("\n")[0]
        if not pid:
            abort(400)
        os.popen("kill -9 "+pid)
        return jsonify({
            'response': True,
            'method': request.method,
            'option':option, 
            'pid': pid,
            'source': payload['source']})


@app.route('/api/v1/deploy', methods=['PUT', 'DELETE'])
def deploy():
    """
        Payload is
            {
                'image': 'claudiocinc/mongodb',
                'port': '-p 27001:27001',
                'name': 'mongodb',
                'host': '--net=host'
                'volume': '',
                'privileges': ''
            }
    """

    payload = json.loads(request.data)

    if request.method == 'PUT':
        # docker run -d conf['privileges'] conf['host'] conf['port'] conf['name'] conf['volume'] conf['image']
        command = 'docker run -d %s %s %s %s --name %s %s' % (payload['privileges'], payload['host'], payload['port'], payload['volume'], payload['name'], payload['image'])
        os.popen(command)
        command = 'docker start %s' % (payload['name'])
        os.popen(command)

    if request.method == 'DELETE':
        command = 'docker stop %s' % (payload['name'])
        os.popen(command)
        command = 'docker rm %s' % (payload['name'])
        os.popen(command)
        command = 'docker rmi %s' % (payload['image'])
        os.popen(command)

    return  jsonify({
        'response': True,
        'method': request.method})