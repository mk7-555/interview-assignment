'''
This is a script to read a webserver log file and parse the IP addresses with successful HTTP GET request
Author: Madhu Kesavan
Email: madhukesavan555@gmail.com
'''
import re
import os
import argparse
import sys
from collections import OrderedDict
# 
# valid IPv4 address has 4 octets in format "A:B:C:D"
# 
ip4_ptrn = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
# 
# valid IPv6 address has 8 octets in format "A:B:C:D:E:F:G:H"
#
ip6_ptrn = re.compile(r'^\w{1,4}\:\w{1,4}\:\w{1,4}\:\w{1,4}\:\w{1,4}\:\w{1,4}\:\w{1,4}\:\w{1,4}')
#
# Regex pattern to get the HTTP status (common error codes listed )
#
http_resp = re.compile(r'"GET .* HTTP/1.1"\s(200|301|302|401|404|500|502)')
#
# Parse the log file for IPv4 and IPv6 addresses. 
# If IP address is followed by successful GET request (HTTP 200 OK)
# then add it to the hash (dictionary).
# Track the number of successful GET requests for each IP and update hash.
#
def parseSuccessIPs(log_file):
	#
	# Use an Ordered dictionary for the hash table. Normal dict does not guarantee element order. 
	#
	ip_table = OrderedDict()
	ip4_addr = None
	ip6_addr = None
	
	with open(log_file, 'r') as log_f:
		for line in log_f:
			match_ip4 = ip4_ptrn.search(line)
			match_ip6 = ip6_ptrn.search(line)
			http_stat = http_resp.findall(line)
			
			if match_ip4 is not None and '200' in http_stat:
				ip4_addr = match_ip4.group()
				if ip4_addr in ip_table.keys():	
					ip_table[ip4_addr] += 1
				else: 
					ip_table[ip4_addr] = 1

			if match_ip6 is not None and '200' in http_stat:
				ip6_addr = match_ip6.group()
				if ip6_addr in ip_table.keys():
					ip_table[ip6_addr] += 1
				else:
					ip_table[ip6_addr] = 1
	return ip_table

	
def writeOutputFile(ip_table, op_file):

	# Write to file only if ip_table is not empty
	if ip_table:
		with open(op_file, 'w') as of:
			for ip, count in ip_table.items():
				of.write("{0} {1}\n".format(ip, count))
	else:
		print("IP table is empty! Exiting program.")
		return False
	
	print("Output is available in file: {}".format(op_file))
	return True

##############################################################################
# Program entry
##############################################################################
if __name__ == "__main__":
	#
	# Get the webserver log file from command line. Note: Full path required.
	#
	parser = argparse.ArgumentParser(description="Path to webserver log file:")
	parser.add_argument('logfile', metavar='logfile', type=str, help='Full path to the webserver log file')
	args = parser.parse_args()
	input_file = args.logfile

	# check if file exists
	if not os.path.isfile(input_file):
		print("The given input file does not exist!")
		sys.exit()

	op_file = "success-ips.txt"
	# 
	# Parse the input file and collect IPs for successful GET requests
	# into the hash table: ip_table.
	#
	ip_table = parseSuccessIPs(input_file)
	writeOutputFile(ip_table=ip_table, op_file=op_file)
