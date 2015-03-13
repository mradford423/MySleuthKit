#!/usr/bin/env python3
import sys
import struct

#Written by Michael Radford

def usage():
	'''
	Returns an error if run without being given an offset and a FAT16 image
	'''
	print("Error:")
	print("USAGE: hw3.py offset(in sectors) image")
	print("exiting...")
	sys.exit()

def parse(offset, fd):
	'''
	parses the image and prints the results
	'''

	'''
	Check signature for FAT16
	'''
	fd.seek(510+(offset*512))
	bytes = fd.read(2)
	if(bytes != b'\x55\xAA'):
		usage()
	print("FILE SYSTEM INFORMATION")
	print("--------------------------------------------")
	print("File System Type: FAT16")
	
	'''
	Find OEM Name
	'''
	fd.seek(3+(offset*512))
	bytes = fd.read(8)
	print("")
	print("OEM Name: ", end="")
	for b in bytes:
		print(chr(b), end="")
	print("")

	'''
	Find Volume ID and Label
	'''
	fd.seek(39+(offset*512))
	bytes = fd.read(4)
	print('Volume ID: 0x', end="")
	for b in reversed(bytes):
		print("%02x" % b, end="")
	print("")
	bytes = fd.read(11)
	print('Volume Label (Boot Sector): ', end="")
	for b in bytes:
		print (chr(b), end="")
	print("")
	print("")
	
	'''
	Already found File System Type Label
	'''
	print("File System Type Label: FAT16")
	print("")

	'''
	Prints the layout on the File System in sectors
	'''
	print("File System Layout (in sectors)")
	
	#Total range
	fd.seek(19+(offset*512))
	bytes = fd.read(2)
	sectors = (bytes[1]<<8) + (bytes[0]) - 1
	if(sectors == 0):
		fd.seek(32+(offset*512))
		bytes = fd.read(4)
		sectors = (bytes[3]<<24) + (bytes[2]<<16) + (bytes[1]<<8) + (bytes[0]) - 1
	print("Total Range: 0 -", sectors)
	print("Total Range in Image: 0 -", sectors - 1)
	
	#Reserved Space
	fd.seek(14+(offset*512))
	bytes = fd.read(2)
	reserved = (bytes[1]<<8) + (bytes[0]) - 1
	print("* Reserved: 0 -", reserved)
	
	#Boot Sector (Assuming always 0)
	print("** Boot Sector: 0")
	
	#Location of FAT(s)
	fd.seek(22+(offset*512))
	bytes = fd.read(2)
	fatsize = (bytes[1]<<8) + (bytes[0])
	print("* FAT 0: ", reserved + 1, "-", fatsize + reserved )
	fd.seek(16+(offset*512))
	if(fd.read()[0] == 2):
		print("* FAT 1: ", fatsize + reserved + 1, "-", fatsize + fatsize + reserved)
	
	#Data Area
	datastart = fatsize + fatsize + reserved + 1
	print("* Data Area: ", datastart, "-", sectors)
	
	#Size of each Sector (used now, not printed until later)
	fd.seek(11+(offset*512))
	bytes = fd.read(2)
	secsize = (bytes[1]<<8) + (bytes[0])
	
	# number of sectors per cluster (used for calculations, not printed)
	fd.seek(13+(offset*512))
	sec_per_clus = fd.read(1)[0]
	
	#Root Directory
	fd.seek(17+(offset*512))
	bytes = fd.read(2)
	rootsize = (bytes[1]<<8) + (bytes[0])
	print("** Root Directory: ", datastart, "-", datastart + int((rootsize*32)/512) - 1)
	
	#Cluster Area
	clus_end = sectors - ((sectors-1)%2)
	print("** Cluster Area: ", datastart + int((rootsize*32)/512), "-", clus_end)
	
	#Non-Clustered Area
	print("** Non-clustered: ", clus_end + 1, "-", sectors)
	print("")
	
	'''
	Final content info 
	'''
	print("CONTENT INFORMATION")
	print("--------------------------------------------")
	print("Sector Size: ", secsize, "bytes")
	print("Cluster Size: ", sec_per_clus * secsize, "bytes")
	#Total Cluster range uses an equation found on page 164 of carrier
	print("Total Cluster Range:  2 -", int(((clus_end - (datastart + (rootsize*32)/512))/sec_per_clus) + 2))
	print("")



def main():
	'''
	Tries to parse the given FAT16 image
	Calls usage() if there is an error, calls parse() otherwise
	'''
	try:
		offset = int(sys.argv[1])
		image = sys.argv[2]
		fd = open(image, "rb")
	except:
		usage()
	parse(offset,fd)


if __name__ == '__main__':
	main()
