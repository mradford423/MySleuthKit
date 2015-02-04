import sys

def usage():
	"""
	Returns an error if run without being given a file name
	"""
	print("Error:")
	print("USAGE: hw1.py filename")
	print("exiting...")
	sys.exit()


def read(fd):
	"""
	Reads in from the file 16 bytes at a time. 
	Prints the line number in hex at the beginning of each line.
	For each 16 byte line, prints each character's hex value.
	Then prints the ASCII value of each character if possible.
	Prints a period otherwise.

	Takes a file descriptor fd as an argument.
	This file name is taken from argv[1], and is created in main().
	"""
	line = 0;
	while (1):
		bytes = fd.read(16)
		print("%08x" % line + "  ", end="")
		line = line + len(bytes)
		for b in bytes:
			print("%02x" % b + " ", end="")
		
		if (len(bytes) < 16): #fill last line
			count = 16 - len(bytes)
			while (count != 0):
				print("   ", end="")
				count = count - 1

		print(" |", end ="")

		for b in bytes:
			if(b >= 32 and b <= 126):
				print(chr(b), end="")
			else:
				print(".", end="")
		print("|")

		if (len(bytes) < 16):
			print("%08x" % line + "  ")
			break

def main():
	"""
	Trys to open a file to read.
	Calls usage() if there is an error, calls read() otherwise
	"""
	try:
		filename = sys.argv[1]
		fd = open(filename, "rb")
	except:
		usage()
	read(fd)



if __name__ == '__main__':
	main()
