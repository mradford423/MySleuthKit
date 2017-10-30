#!/usr/bin/env python3
import sys

def usage():
	"""
	Returns an error if run without being given:
	- a minimum length - int
	- a file name - string
	"""
	print("Error:")
	print("USAGE: strings.py minimum_length filename")
	print("exiting...")
	sys.exit()

def read(minlength, fd):
	"""
	reads from the given file descriptor 1 byte at a time
	if the byte is a printable ASCII character, it gets added to the output string
	if the byte is a printable ASCII character, and the following byte is 00,
		then it is treated as a little endian unicode character, and 
		is added to the output string
	if there are two 00s in a row, or an unprintable character is encountered,
		and the output string is at least the length of the minimum length, 
		the output string is printed and the program moves to the next line
	"""
	output = ""
	prev = 0
	while(1):
		byte = fd.read(1)
		if not byte:
			print(output)
			break
		if((byte[0] >= 32 and byte[0] <= 126) or (byte[0] == ord("\n"))):
			output+=chr(byte[0])
		else:
			if(byte[0] == 00 and prev != 00):
				pass
			else:
				if(len(output) >= minlength):
					print(output)
				output = ""	
		prev = byte[0]


def main():
	"""
	Trys to open a file to read.
	Calls usage() if there is an error, calls read() otherwise
	"""
	try:
		minlength = int(sys.argv[1])
		filename = sys.argv[2]
		fd = open(filename, "rb")
	except:
		usage()
	read(minlength, fd)



if __name__ == '__main__':
	main()
