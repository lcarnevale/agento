#!/usr/bin/env python

"""
	Authors: Lorenzo Carnevale <lorenzocarnevale@gmail.com>
"""

from threading import Thread
import os, sys, time
import psutil, json, redis, docker
import pprint

DEBUG = 1

class Monitor():

	def __init__(self, interval, db):
		# class variables
		self.__interval = float(interval)
		self.__db = str(db)
		#
		self.__docker_client = docker.from_env()
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



	def __mem_host(self):
		"""."""
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
		data['swap'] = {
			'total': int(swap.total / 1024),
			'used': int(swap.used / 1024),
			'free': int(swap.free / 1024)
		}

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __mem_guest(self):
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

	def __mem(self, source):
		if source == 'host':
			json_data = self.__mem_host()
		elif source == 'guest':
			json_data = self.__mem_guest()
		else:
			# run exception
			pass
		return json_data


	def __cpu_host(self):
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
		data = {'guest': {'cpu': {}}}
		all_containers = self.__docker_client.containers.list()
		for one_container in all_containers:
			container = self.__docker_client.containers.get(one_container.id)
			stats_container = container.stats(decode=True,stream=False)
			data['guest']['cpu'][stats_container['id']] = stats_container['cpu_stats']
			data['guest']['cpu'][stats_container['id']]['name'] = stats_container['name']
			data['guest']['cpu'][stats_container['id']]['precpu_stats'] = stats_container['precpu_stats']
			data['guest']['cpu'][stats_container['id']]['read'] = stats_container['read']

		json_data = json.dumps(data)

		if DEBUG:
			print json_data

		return json_data

	def __cpu(self, source):
		if source == 'host':
			json_data = self.__cpu_host()
		elif source == 'guest':
			json_data = self.__cpu_guest()
		else:
			# run exception
			pass
		return json_data


	def __net_host(self):
		"""."""
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

	def __net_guest(self):
		pass

	def __net(self, source):
		if source == 'host':
			json_data = self.__net_host()
		elif source == 'guest':
			json_data = self.__net_guest()
		else:
			# run exception
			pass
		return json_data


	def __toRedis(self, mon, json_data):
		self.conn.publish(mon,json_data)

	def __toNull(self, mon, json_data):
		old_stdout = sys.stdout
		sys.stdout = open(os.devnull, 'w')
		sys.stdout = old_stdout
		if DEBUG:
			print 'toNull'


	def __sample(self, source, mon):
		json_data = self.__funDictHw[mon](source)
		self.__funDictDb[self.__db](mon, json_data)

	def run(self, source, mons):
		try:
			while True:
				for mon in mons:
					thread = Thread(target = self.__sample, args = (source, mon, ))
					thread.start()
					thread.join()
				time.sleep(self.__interval)
		except (KeyboardInterrupt, SystemExit):
			pass



if __name__ == '__main__':
	db = sys.argv[1]
	source = sys.argv[2]
	interval = sys.argv[3]
	monitors = sys.argv[4:]
	Monitor(interval, db).run(source, monitors)