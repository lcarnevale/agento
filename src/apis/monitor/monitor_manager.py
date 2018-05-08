#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Functionalities for the monitor routes.

    The scope of the application is academic research.
    It is part of the Osmotic Computing activities carried 
    out at both University of Messina and TU Wien.
"""

__author__ = "Lorenzo Carnevale"
__copyright__ = None
__credits__ = ["Lorenzo Carnevale"]
__license__ = None
__version__ = "1"
__maintainer__ = "Lorenzo Carnevale"
__email__ = "lcarnevale@unime.it"
__status__ = "Prototype"


import subprocess
import os
import json
from flask import jsonify
from flask import request
from flask import abort


class MonitorManager():
    """

    """

    def __init__(self, resource, target, payload):
        self.resource = resource
        self.target = target
        try:
            self.payload = json.loads(payload)
        except ValueError:
            self.payload = None

        # read from conffile
        self.resource_list = ['mem', 'cpu', 'net', 'rtime'] 
        self.target_list = ['host', 'guest'] 

        self.__run_for_method = dict()
        self.__run_for_method['PUT'] = self.__put
        self.__run_for_method['DELETE'] = self.__delete


    def _check_assertion(self):
        """
        """
        try:
            assert self.resource in self.resource_list
            assert self.target in self.target_list
        except AssertionError:
            abort(400)

    def __put(self):
        """
        """
        if not self.payload:
            abort(400)
        command = 'python apis/monitor/monitor_start.py start null %s %s %s' % (self.target, self.payload['time'], self.resource)
        #p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        os.system(command)
        return jsonify({
            'response': True,
            })

    def __delete(self):
        """
        """
        command = 'python apis/monitor/monitor_end.py %s %s' % (self.target, self.resource)
        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if err:
            abort(400)
        return jsonify({
            'response': True,
            'status': 200})


    def run(self, method):
        self._check_assertion()
        r = self.__run_for_method[method]()
        return r



