#!/usr/bin/env python

"""
	Authors: Lorenzo Carnevale <lorenzocarnevale@gmail.com>
"""

import os, sys, time
from threading import Thread
import json
import redis


DEBUG = 1

class MonitorGuest():

	def __init__(self, interval, db):
		# class variables
		self.__interval = float(interval)
		self.__db = str(db)
		# function's dictionary for hw
		self.__funDictHw = dict()
		self.__funDictHw['mem'] = self.__mem
		self.__funDictHw['cpu'] = self.__cpu
		self.__funDictHw['net'] = self.__net
		# function's dictionary for db
		self.__funDictDb = dict()
		self.__funDictDb['null'] = self.__toNull
		self.__funDictDb['redis'] = self.__toRedis
		if db == 'redis':
			self.conn = redis.Redis('localhost')




	def __mem_poll(self):
		#command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$2\";\"$4\";\"$6\";\"$7}'" # 1-id; 2-name; 4-memusage; 6-memlimit; 7-memperc
		command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$3 $4\";\"$6 $7\";\"$8}'" # 1-id; 34-memusage; 67-memlimit; 8-memperc
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
				#'name': arg[1],
				'mem_usage': arg[1],
				'mem_limit': arg[2],
				'mem_perc': arg[3]
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
		#command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$2\";\"$3}'" # 1-id; 2-name; 3-cpu
		command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$2}'" # 1-id; 2-cpu
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
				#'name': arg[1],
				'cpu': arg[1]
			}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __cpu(self):
		args = self.__cpu_poll()
		json_data = self.__cpu_status(args)
		return json_data
	

	def __net_poll(self):
		#command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$2\";\"$8\";\"$8}'" # 1-id; 2-name; 8-netin; 9-netout
		command = "docker stats --no-stream | awk '{if (NR!=1) {print}}' | awk '{print $1\";\"$9 $10\";\"$12 $13}'" # 1-id; 910-netin; 1213-netout
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
				#'name': arg[1],
				'net_in': arg[1],
				'net_out': arg[2]
			}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __net(self):
		args = self.__net_poll()
		json_data = self.__net_status(args)
		return json_data


	def __toRedis(self, threadName, json_data):
		key = '%s_%s' % (threadName,str(int(time.time())))
		self.conn.set(key, json_data)

	def __toNull(self, threadName, json_data):
		old_stdout = sys.stdout
		sys.stdout = open(os.devnull, 'w')
		sys.stdout = old_stdout
		if DEBUG:
			print 'toNull'


	def run(self, mons):
		try:
			while True:
				for mon in mons:
					json_data = self.__funDictHw[mon]()
					try:
						thread = Thread(target = self.__funDictDb[self.__db], args = (mon, json_data, ))
						thread.start()
						thread.join()
					except:
					   print "Error: unable to start thread"
				time.sleep(self.__interval)
		except (KeyboardInterrupt, SystemExit):
			pass


if __name__ == '__main__':
	db = sys.argv[1]
	interval = sys.argv[2]
	monitors = sys.argv[3:]
	MonitorGuest(interval, db).run(monitors)