#!/usr/bin/python

import os, sys
import argparse
from opennms import Outage

CONFIG_FILE = "config.yaml"

parser = argparse.ArgumentParser(description="Schedule outage for the given node.")
parser.add_argument("-x", "--host", nargs=1, dest="HOSTNAME", help="Hostname to put in outage mode.")
parser.add_argument("-g", "--get-nodes", action="store_true", default=False, help="Get list of node ids and node labels.")
parser.add_argument("-s", "--set-outage", action="store_true", default=False, help="Set outage for the specified host with -x.")
parser.add_argument("-o", "--get-outage", action="store_true", default=False, help="Get list of outages.")

arguments = parser.parse_args()

try:
	HOSTNAME = arguments.HOSTNAME[0]
except:
	HOSTNAME = os.uname()[1]
	print "No hostname provided, defaulting to current (%s)..\n" %(HOSTNAME)

client = Outage(HOSTNAME, CONFIG_FILE)

if(arguments.get_nodes):
	client.get_nodes()
	sys.exit(0)
elif(arguments.set_outage):
	client.set_outage()
	sys.exit(0)
elif(arguments.get_outage):
	client.get_outage()
	sys.exit(0)
else:
	parser.print_help()

