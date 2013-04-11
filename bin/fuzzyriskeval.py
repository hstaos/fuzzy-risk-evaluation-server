#!/usr/bin/env python

__author__ = 'apprentice1989@gmail.com (Huang Shitao)'

import getopt, sys, logging, daemon
import configure, server

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hp:v", ["help", "port=","version"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for op, value in opts:
		if op == "-p":
			port = int(value)
			init()
			logging.info("Server is starting...")
			with daemon.DaemonContext():
				server.start(port)
			#logging.info("Finished! Time cost : " + str(time_after - time_before))
		elif op == "-v":
			print("Version: 2.0.0")
		elif op == "-h":
			usage()

def usage():
	print("Use like this : ./riskeval [-p port].")

def init():
	logging.basicConfig(filename= configure.getConf()["log_file_path"],\
			format='%(levelname)s %(asctime)s:%(message)s', \
			level=logging.DEBUG)

if __name__ == "__main__":
	main()
