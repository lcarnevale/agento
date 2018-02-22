from threading import Thread
from kafka import KafkaProducer
import sys, time, redis, json


def main(channel, redis_host='localhost', kafka_host='localhost', kafka_port='9092'):

	kafka_url = '%s:%s' % (kafka_host, kafka_port)
 	r = redis.Redis(redis_host)
	p = r.pubsub()
	p.subscribe([channel])

	PAUSE = True

	while PAUSE:
		message = p.get_message()
		if message:
			try:
				producer = KafkaProducer(
					bootstrap_servers=kafka_url,
					value_serializer=lambda v: json.dumps(v).encode('utf-8')
					)
				producer.send(message['channel'], message['data'])
			except TypeError:
				print 'jump'
		time.sleep(1)

if __name__ == '__main__':
	# get json as argv
	channel=sys.argv[1]
	main(channel)
	#thread = Thread(target = main, args = (channel, ))
	#thread.start()
	#thread.join()