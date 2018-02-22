from __future__ import print_function
import os, sys, signal, psutil

def pid(cmdline, programname):
	for p in psutil.process_iter(attrs=[]):
		if set(cmdline).issubset(p.info['cmdline']) and not set([programname]).issubset(p.info['cmdline']):
			return p.info['pid']

def kill(pid):
	try:
		os.kill(pid, signal.SIGTERM)
		return True
	except TypeError:
		return False

def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == '__main__':
	programname = sys.argv[0]
	cmdline = sys.argv[1:]
	if not kill(pid(cmdline, programname)):
		errprint(1)