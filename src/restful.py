#!flask/bin/python
from flask import Flask, jsonify, request, abort
import os
import json
import subprocess

app = Flask(__name__)


@app.route('/api/v1', methods=['GET'])
def apis_list():
    return jsonify({'response': True, 'comment': 'I want you back free!'})


@app.route('/api/v1/monitor/<string:option>', methods=['PUT', 'DELETE'])
def monitor(option):

    options = ['mem', 'cpu', 'net'] # todo: from conffile
    sources = ['host', 'guest'] # todo: from conffile
    
    if not option in options:
        abort(404) # Raise an HTTPException with a 404 not found status code
    if request.method == 'PUT':
        payload = json.loads(request.data)
        if not payload['source'] in sources:
            abort(400) # Raise an HTTPException with a 400 not found status code
        command = 'python monitor/monitor_%s.py %s %s' % (payload['source'], payload['time'], option)
        #os.system(command)
        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        return jsonify({
            'response': True,
            'method': request.method,
            'option':option, 
            'time': payload['time'],
            'source': payload['source']})

    elif request.method == 'DELETE':
        payload = json.loads(request.data)
        if payload['source'] == 'host' or payload['source'] == 'guest':
            command = "ps -elf | grep python | grep %s | grep %s | grep -v grep | awk '{print $4}'" % (payload['source'], option)
            command_ps = "ps -elf"
            command_grep1 = "grep python"
            command_grep2 = "grep %s" % (payload['source'])
            command_grep3 = "grep %s" % (option)
            command_grep4 = "grep -v grep"
            command_awk = ["awk", "{print $4}"]
        else:
            abort(400)
        #pid =  os.popen(command).read().split("\n")[0]
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
            abort(400)
        #os.popen("kill -9 "+pid)
        p = subprocess.Popen(["kill", "-9", pid], stdout=subprocess.PIPE)
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
        #subprocess.Popen(command, stdout=subprocess.PIPE)
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