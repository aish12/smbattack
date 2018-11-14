
from subprocess import call
import argparse

class HydraCracker:
	def __init__(self):
		a_parser = argparse.ArgumentParser(description = "Used to parse command line arguments")
		a_parser.add_argument("-u", "-user", help = "The name of the user", required = False, default = "")
		a_parser.add_argument("-p", "-password", help = "The password file", required = False, default = "/usr/share/john/password.lst")
		a_parser.add_argument("-i", "-ip", help = "IP address of SMB server", required = True)

		parameters = a_parser.parse_args()
		
		arguments = ["hydra"]
		if a_parser.u != "":
			arguments.append("-l " + a_parser.u)
		
		arguments.append("-P " + a_parser.p)		
		arguments.append(a_parser.i)
		arguments.append("smb")
		call(arguments)

if __name__ == '__main__':
	a = HydraCracker()
