#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This is a standalone application ables to monitor hardware
    and software resources both of host and guests (docker
    containers).

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

import os
import sys 
import time
import psutil
import json
import redis
import docker
from daemon import runner

DEBUG = 1

class App():
	"""
		It is a daemon application running in background.
	"""

	def __init__(self, interval, target, resource):
		"""
			It initializes the class variables and fills the
			methods running dictionaries.
		"""

		# deamon variables
		self.stdin_path = '/dev/null'
		self.stdout_path = '/dev/tty'
		self.stderr_path = '/dev/tty'
		self.pidfile_path =  '/tmp/foo.pid'
		self.pidfile_timeout = 5
		# class variables
		self.__interval = float(interval)
		self.__target = target
		self.__resources = resource
		# docker environment
		self.__docker_client = docker.from_env()
		# database variables
		self.conn = None
		#self.conn = redis.Redis('localhost')
		# python methods dictionary for the resources/targets
		self.__run_by_resource = {'mem': {}, 'cpu': {}, 'net': {}}
		self.__run_by_resource['mem']['host'] = self.__mem_host
		self.__run_by_resource['mem']['guest'] = self.__mem_guest
		self.__run_by_resource['cpu']['host'] = self.__cpu_host
		self.__run_by_resource['cpu']['guest'] = self.__cpu_guest
		self.__run_by_resource['net']['host'] = self.__net_host
	

	# resources methods
	def __mem_host(self):
		"""
			This method performs a monitoring of the host
			memory (RAM) resource. 

			Returns:
				a JSON format dataset with the monitored
				information.
		"""

		virt = psutil.virtual_memory()
		swap = psutil.swap_memory()

		data = {'host': {}}
		data['host']['mem'] = {
			'total': int(virt.total / 1024),
			'used': int(virt.used / 1024),
			'free': int(virt.free / 1024),
			'shared': int(getattr(virt, 'shared', 0) / 1024),
			'buffers': int(getattr(virt, 'buffers', 0) / 1024),
			'cache': int(getattr(virt, 'cached', 0) / 1024)
		}
		data['host']['swap'] = {
			'total': int(swap.total / 1024),
			'used': int(swap.used / 1024),
			'free': int(swap.free / 1024)
		}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __mem_guest(self):
		"""
			This method performs a monitoring of the guest
			(docker containers) memory (RAM) resources. 

			Returns:
				a JSON format dataset with the monitored
				information.
		"""

		data = {'guest': {'mem': {}}}
		all_containers = self.__docker_client.containers.list()
		for one_container in all_containers:
			container = self.__docker_client.containers.get(one_container.id)
			stats_container = container.stats(decode=True,stream=False)
			data['guest']['mem'][stats_container['id']] = stats_container['memory_stats']
			data['guest']['mem'][stats_container['id']]['name'] = stats_container['name']

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __cpu_host(self):
		"""
			This method performs a monitoring of the host
			CPU resource. 

			Returns:
				a JSON format dataset with the monitored
				information.
		"""

		percs = psutil.cpu_percent(interval=0, percpu=True)
		data = {'host':{'cpu':{}}}
		for cpu_num, perc in enumerate(percs):
			key = "CPU%-2s" % (cpu_num)
			value = "%5s%%" % (perc)
			data['host']['cpu'][key] = value

		json_data = json.dumps(data)

		if DEBUG:
			print json_data    

		return json_data

	def __cpu_guest(self):
		"""
			This method performs a monitoring of the guest
			(docker containers) CPU resources. 

			Returns:
				a JSON format dataset with the monitored
				information.
		"""
		data = {'guest': {'cpu': {}}}
		all_containers = self.__docker_client.containers.list()
		for one_container in all_containers:
			container = self.__docker_client.containers.get(one_container.id)
			stats_container = container.stats(decode=True,stream=False)
			data['guest']['cpu'][stats_container['id']] = {}
			data['guest']['cpu'][stats_container['id']]['cpu_stats'] = stats_container['cpu_stats']
			data['guest']['cpu'][stats_container['id']]['name'] = stats_container['name']
			data['guest']['cpu'][stats_container['id']]['precpu_stats'] = stats_container['precpu_stats']
			data['guest']['cpu'][stats_container['id']]['read'] = stats_container['read']

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __net_host(self):
		"""
			This method performs a monitoring of the host
			network resource. 

			Returns:
				a JSON format dataset with the monitored
				information.
		"""
		tot = psutil.net_io_counters()
		pnic = psutil.net_io_counters(pernic=True)

		data = {'host':{'net': {}}}
		data['host']['net']['tot'] = {
			'bytes_sent': tot.bytes_sent,
			'bytes_recv': tot.bytes_recv,
			'packets_sent': tot.packets_sent,
			'packets_recv': tot.packets_recv
		}

		nic_names = list(pnic.keys())
		for name in nic_names:
			stats = pnic[name]
			data['host']['net'][name] = {
				'bytes_sent': stats.bytes_sent,
				'bytes_recv': stats.bytes_recv,
				'packets_sent': stats.packets_sent,
				'packets_recv': stats.packets_recv
			}
	    
		json_data = json.dumps(data)
	
		if DEBUG:
			print json_data

		return json_data


	# dbs methods
	def __toRedis(self, resource, json_data):
		"""
			It stores monitored data in redis database.

			Args:
				resource: the data's resource used as key;
				json_data: monitored data in JSON format.
		"""

		if self.conn:
			self.conn.publish(resource, json_data)


	def run(self):
		"""
			It is the starting point of the daemon. For each
			parameterized resource, it starts the monitor and
			stores results on database.
		"""

		while True:
			for resource in self.__resources:
				try:
					json_data = self.__run_by_resource[resource][self.__target]()
				except KeyError:
					# todo: raise exception
					print 'no json data'
				#self.__toRedis(resource, json_data)
			time.sleep(self.__interval)


interval = sys.argv[2]
target = sys.argv[3]
resources = sys.argv[4:]

app = App(interval, target, resources)
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()