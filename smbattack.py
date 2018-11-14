import argparse as ag
import os 
from subprocess import call

def performAttack(location, serverIP, username, password=None):
	if (password is None):
		password = bruteForcePassword()
		print ("Null Password, brute forced to: " + password)
	else:
		print ("password is " + password)
	os.mkdir(location)
	mountpoint = ""
	mountArgs = ["mount", "-t", "cifs", "-o", "username=" + username + ",password=" + password, "//" + serverIP + "/" + mountpoint, location]
	call(mountArgs)

def bruteForcePassword():
	return "bruteForcePassword"
parser = ag.ArgumentParser()
parser.add_argument('--mountloc', type=str, help="Enter the location to mount the system")
parser.add_argument('--serverIP', type=str, help="Enter the name of the targer windows server")
parser.add_argument('--username', type=str, help="Enter the username of the target windows server")
parser.add_argument('--password', type=str, help="Optional. Enter the password of the target windows server. If not included, password will be brute forced.")


args = parser.parse_args()
if args.password:
	performAttack(args.mountloc, args.serverIP, args.username, args.password)
else:
	performAttack(args.mountloc, args.serverIP, args.username)

