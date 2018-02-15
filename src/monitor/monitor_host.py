#!/usr/bin/env python

"""
	Authors: Lorenzo Carnevale <lorenzocarnevale@gmail.com>
"""

import os, sys, time
from threading import Thread
import psutil
import json
import redis


DEBUG = 1

class Monitor():

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
		if db is 'redis':
			print 'here'
			self.conn = redis.Redis('localhost')



	def __mem_poll(self):
		virt = psutil.virtual_memory()
		swap = psutil.swap_memory()
		return (virt, swap)

	def __mem_status(self, virt, swap):
		"""."""
		data = {'host': {}}
		data['host']['mem'] = {
			'total': int(virt.total / 1024),
			'used': int(virt.used / 1024),
			'free': int(virt.free / 1024),
			'shared': int(getattr(virt, 'shared', 0) / 1024),
			'buffers': int(getattr(virt, 'buffers', 0) / 1024),
			'cache': int(getattr(virt, 'cached', 0) / 1024)
		}
		data['swap'] = {
			'total': int(swap.total / 1024),
			'used': int(swap.used / 1024),
			'free': int(swap.free / 1024)
		}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __mem(self):
		args = self.__mem_poll()
		json_data = self.__mem_status(*args)
		return json_data


	def __cpu_poll(self):
		procs = []
		procs_status = {}
		for p in psutil.process_iter():
			try:
				p.dict = p.as_dict(['username', 'nice', 'memory_info',
									'memory_percent', 'cpu_percent',
									'cpu_times', 'name', 'status'])
				try:
					procs_status[p.dict['status']] += 1
				except KeyError:
					procs_status[p.dict['status']] = 1
			except psutil.NoSuchProcess:
				pass
			else:
				procs.append(p)

		return (procs_status, len(procs))

	def __cpu_status(self, procs_status, num_procs):
		"""."""
	    
		# cpu usage
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

	def __cpu(self):
		args = self.__cpu_poll()
		json_data = self.__cpu_status(*args)
		return json_data


	def __net_poll(self):
		tot = psutil.net_io_counters()
		pnic = psutil.net_io_counters(pernic=True)
		return (tot, pnic)

	def __net_status(self, tot, pnic):
		"""."""
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

	def __net(self):
		args = self.__net_poll()
		json_data = self.__net_status(*args)
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
	Monitor(interval, db).run(monitors)