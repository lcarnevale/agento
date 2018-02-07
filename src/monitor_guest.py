#!/usr/bin/env python

"""
	Authors: Lorenzo Carnevale <lorenzocarnevale@gmail.com>
"""

import sys
import os
import time
import json


DEBUG = 1

class MonitorGuest():

	def __init__(self, interval):
		self.__interval = float(interval)
		self.__fundict = dict()
		self.__fundict['mem'] = self.__mem
		self.__fundict['cpu'] = self.__cpu
		self.__fundict['net'] = self.__net



	def __mem_poll(self):
		command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$2\";\"$4\";\"$6\";\"$7}'" # 1-id; 2-name; 4-memusage; 6-memlimit; 7-memperc
		res = os.popen(command).read().split("\n")
		data = []
		for r in res:
			data.append(r.split(";"))
		return data[:-1]

	def __mem_status(self, args):
		"""."""
		data = {'guests': {}}
		for arg in args:
			data['guests'][arg[0]] = {
				'name': arg[1],
				'mem_usage': arg[2],
				'mem_limit': arg[3],
				'mem_perc': arg[4]
			}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __mem(self):
		args = self.__mem_poll()
		json_data = self.__mem_status(args)
		return json_data


	def __cpu_poll(self):
		command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$2\";\"$3}'" # 1-id; 2-name; 3-cpu
		res = os.popen(command).read().split("\n")
		data = []
		for r in res:
			data.append(r.split(";"))
		return data[:-1]

	def __cpu_status(self, args):
		"""."""
		data = {'guests': {}}
		for arg in args:
			data['guests'][arg[0]] = {
				'name': arg[1],
				'cpu': arg[2]
			}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __cpu(self):
		args = self.__mem_poll()
		json_data = self.__mem_status(args)
		return json_data
	

	def __net_poll(self):
		command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$2\";\"$8\";\"$8}'" # 1-id; 2-name; 8-netin; 9-netout
		res = os.popen(command).read().split("\n")
		data = []
		for r in res:
			data.append(r.split(";"))
		return data[:-1]

	def __net_status(self, args):
		"""."""
		data = {'guests': {}}
		for arg in args:
			data['guests'][arg[0]] = {
				'name': arg[1],
				'net_in': arg[2],
				'net_out': arg[3]
			}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __net(self):
		args = self.__net_poll()
		json_data = self.__net_status(args)
		return json_data


	def run(self, mons):
		try:
			while True:
				for mon in mons:
					self.__fundict[mon]()
				time.sleep(self.__interval)
		except (KeyboardInterrupt, SystemExit):
			pass


if __name__ == '__main__':
	interval = sys.argv[1]
	monitors = sys.argv[2:]
	MonitorGuest(interval).run(monitors)