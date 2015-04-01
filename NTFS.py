#!/usr/bin/env python3
import sys
import struct
import datetime

#Written by Michael Radford

def usage():
	'''
	Returns an error if run without being given an entry# and an NTFS image
	'''
	print("Error:")
	print("USAGE: hw5.py entry_number NTFS_image")
	print("exiting...")
	sys.exit()

def getSigned(bytes):
	'''
	The function we created in lab. This gives us the value of a 2s compliment number
	'''
	length = len(bytes)
	most_sig = bytes[length-1]
	if(most_sig >> 7 == 0):
		return (struct.unpack("<q", bytes + b'\x00' * (8-length))[0])
	else:
		return (struct.unpack("<q", bytes + b'\xFF' * (8-length))[0])

def printFlags(flags):
	'''
	This function prints out the value of the flags for FILE_NAME and STANDARD_INFORMATION
	'''
	read_only = 0x0001
	hidden = 0x0002
	system = 0x0004
	archive = 0x0020
	device = 0x0040
	normal = 0x0080
	temporary = 0x0100
	sparse_file = 0x0200
	reparse_point = 0x0400
	compressed = 0x0800
	offline = 0x1000
	not_indexed = 0x2000
	encrypted = 0x4000

	if(flags&read_only):
		print("Read Only", end=" ")
	if(flags&hidden):
		print("Hidden", end=" ")
	if(flags&system):
		print("System", end=" ")
	if(flags&archive):
		print("Archive", end=" ")
	if(flags&device):
		print("Device", end=" ")
	if(flags&normal):
		print("Normal", end=" ")
	if(flags&temporary):
		print("Temporary", end=" ")
	if(flags&sparse_file):
		print("Sparse File", end=" ")
	if(flags&reparse_point):
		print("Reparse Point", end=" ")
	if(flags&compressed):
		print("Compressed", end=" ")
	if(flags&offline):
		print("Offline", end=" ")
	if(flags&not_indexed):
		print("Not Indexed for faster searches", end=" ")
	if(flags&encrypted):
		print("Encrypted", end=" ")
	print("")
def parse(entry, fd):
	'''
	parses the boot sector of the image
	first, we find MFT_entry 0, then parse it to get the runlist 
	we use the runlist to find the entry that the user gives us, then parse that

	Args:
	entry is the given entry number that the user wants to find
	fd is the file descriptor
	'''
	fd.seek(11)
	bytes = fd.read(2)
	bytes_per_sec = (bytes[1]<<8) + (bytes[0])
	sec_per_clus = fd.read(1)[0]
	fd.seek(8)
	bytes = fd.read(8)
	logFile = struct.unpack("<Q", bytes)[0]
	bytes = fd.read(2)
	sequence = (bytes[1]<<8) + (bytes[0])
	fd.seek(40)
	bytes = fd.read(8)
	total_sec = struct.unpack("<Q", bytes)[0]
	fd.seek(64)
	MFT_size = fd.read(1)[0]
	fd.seek(48)
	bytes = fd.read(8)
	MFT_start = struct.unpack("<Q", bytes)[0]
	fd.seek(MFT_start * sec_per_clus * bytes_per_sec)
	#we store the MFT_entry in a byte array to make it easier to read, and easier to handle the fixup array
	MFT_entry = bytearray(fd.read(1024))
	if(entry == 0):
		#if we are looking for entry 0, this ensures that we print out info while we're here, and we don't need to worry about the runlist
		parse_entry(entry, MFT_entry, 1)
	else:
		#otherwise, we just want the runlist from entry 0
		runlist = parse_entry(entry, MFT_entry, 0)
		count = 0
		while(count < len(runlist)):
			runlist[count] = runlist[count] * bytes_per_sec * sec_per_clus
			count+=1
		temp_entry = entry *1024
		count = 0
		location = 0
		while (count < len(runlist)):
			#this loop finds the location of the entry we are looking for
			if(runlist[count] + temp_entry < runlist[count+1]):
				location = runlist[count]+temp_entry
				break
			else:
				temp_entry -= (runlist[count+1] - runlist[count])
				count+=2
		fd.seek(location)
		#now we take this entry and parse it, this time with isEntry = 1
		MFT_entry = bytearray(fd.read(1024))
		parse_entry(entry, MFT_entry, 1)

def parse_entry(entry, MFT_entry, isEntry):
	'''
	We are given an MFT entry, and we parse it here
	This function parses all of the information in the header of the MFT entry
	We first do this to find the $DATA attribute of entry 0
	Then, we do it a second time to find the entry that the user is looking for, and print info about that entry

	Args:
	entry is the given entry number that the user wants to find
	MFT_entry is an entry in the MFT that we are currently parsing, and is always 1024 bytes in NTFS
	isEntry is 0 if this is not the entry that the user is looking for (so we are looking for the runlist)
		it is 1 otherwise
	'''
	bytes = [MFT_entry[i] for i in range(4)]
	sig = ''
	for b in bytes:
		sig+= chr(b)
	if(sig != "FILE"):
		print("Error: entry_number out of bounds")
		print("exiting...")
		sys.exit()
	
	bytes = [MFT_entry[i+4] for i in range(2)]
	fixup_offset = (bytes[1]<<8) + (bytes[0])
	bytes = [MFT_entry[i+6] for i in range(2)]
	fixup_entries = (bytes[1]<<8) + (bytes[0])
	bytes = bytearray([MFT_entry[i+8] for i in range(8)])
	LSN = struct.unpack("<Q", bytes)[0]
	bytes = [MFT_entry[i+16] for i in range(2)]
	sequence_value = (bytes[1]<<8) + (bytes[0])
	bytes = [MFT_entry[i+20] for i in range(2)]
	attribute_offset = (bytes[1]<<8) + (bytes[0])
	bytes = [MFT_entry[i+22] for i in range(2)]
	flags = (bytes[1]<<8) + (bytes[0])
	bytes = bytearray([MFT_entry[i+24] for i in range(4)])
	used = struct.unpack("<L", bytes)[0]
	bytes = bytearray([MFT_entry[i+28] for i in range(4)])
	allocated = struct.unpack("<L", bytes)[0]
	#now we handle the fixup array
	fixup_sig = bytearray([MFT_entry[i+fixup_offset] for i in range(2)])
	sec_end1 = bytearray([MFT_entry[i+510] for i in range(2)])
	sec_end2 = bytearray([MFT_entry[i+1022] for i in range(2)])
	if (sec_end1 != fixup_sig or sec_end2 != fixup_sig):
		#if the sector ends don't match the fixup signature, the data is corrupted
		print("Error: MFT entry corrupted")
		print("exiting...")
		sys.exit()
	fixup1 = fixup_sig = bytearray([MFT_entry[i+fixup_offset+2] for i in range(2)])
	fixup2 = fixup_sig = bytearray([MFT_entry[i+fixup_offset+4] for i in range(2)])
	MFT_entry[510] = fixup1[0]
	MFT_entry[511] = fixup1[1]
	MFT_entry[1022] = fixup2[0]
	MFT_entry[1023] = fixup2[1]
	#correctly handled the fixup array
	if(isEntry):
		#if this is the entry we are looking for, we print out the info we found
		print("MFT Entry Header Values:")
		print("Sequence:", sequence_value)
		print("$LogFile Sequence Number", LSN)
		if(flags&0x01):
			print("In use")
		if(flags&0x02):
			print("Directory")
		print("")
		print("Used size:", used, "bytes")
		print("Allocated size:", allocated, "bytes")
		print("")
	#now we begin to parse the attributes
	bytes = bytearray([MFT_entry[i+attribute_offset+ 4] for i in range(4)])
	att_length = struct.unpack("<L", bytes)[0]
	att = bytearray([MFT_entry[i+attribute_offset] for i in range(att_length)])
	count = 0
	runlist = []
	while 1:
		#this loop ensures that we parse every attribute in the entry
		data = parse_att(att, att_length, isEntry)
		if(data):
			#if we parsed the $DATA attribute, we have the runlist
			runlist = data
		count+= att_length
		bytes = bytearray([MFT_entry[i+attribute_offset+ count + 4] for i in range(4)])
		att_length = struct.unpack("<L", bytes)[0]
		if(att_length == 0):
			break
		try: 
			#if we reach the end of the list, we may end up with a massive number here, so we quit if that is the case
			att = bytearray([MFT_entry[i+attribute_offset+count] for i in range(att_length)])
		except:
			break
	if(isEntry):
		#now we print the slack data
		print("Slack data:")
		space_left = 1024 - attribute_offset - count
		bytes = bytearray([MFT_entry[i+attribute_offset+count] for i in range(space_left-1)])
		for b in bytes:
			if(b >= 32 and b <= 126):
				print(chr(b), end="")
			else:
				print(".", end="")
		print("")
	if(runlist):
		return runlist

def parse_att(att, att_length, isEntry):
	'''
	Here, we parse the current attribute in the MFT entry
	If we are on entry 0 looking for the runlist, we mainly want the $DATA attribute to get that runlist
	Otherwise, all of this information is important, and we print it out

	Args:
	att is the current attribute we are parsing
	att_length is the length of att (bytes 4-7 of att) 
	isEntry is 0 if this is not the entry that the user is looking for (so we are looking for the runlist)
		it is 1 otherwise
	'''
	try:
		#for some very small entries, this part crashed because the entry was too small, this try statement fixes that
		bytes = bytearray([att[i] for i in range(4)])
	except:
		print("Entry has no attributes")
		print("")
		sys.exit()
	att_type_id = struct.unpack("<L", bytes)[0]
	non_res = att[8]
	name_len = att[9]
	bytes = bytearray([att[i+10] for i in range(2)])
	name_offset = (bytes[1]<<8) + (bytes[0])
	bytes = bytearray([att[i+12] for i in range(2)])
	att_flags = (bytes[1]<<8) + (bytes[0])
	bytes = bytearray([att[i+14] for i in range(2)])
	att_id = (bytes[1]<<8) + (bytes[0])
	content_len = 0
	content_offset = 0
	if(non_res == 0):
		bytes = bytearray([att[i+16] for i in range(4)])
		content_len = struct.unpack("<L", bytes)[0]
		bytes = bytearray([att[i+20] for i in range(2)])
		content_offset = (bytes[1]<<8) + (bytes[0])
	#we parse if it was one of these first three attribute types
	if (att_type_id == 16):
		if(isEntry):
			#print information if this is the entry we are looking for
			print("Type: $STANDARD_INFORMATION (16) NameLen: (",name_len,")", end="")
			if(non_res):
				print(" Non-Resident  ", end="")
			else:
				print(" Resident  ", end="")
			print(" size:" , att_length)
		#we need to convert all of these times into Windows time
		D = 116444736000000000
		bytes = bytearray([att[i+content_offset] for i in range(8)])
		create_time = struct.unpack("<Q", bytes)[0]
		epoch = (create_time-D)/10000000
		create_time = str(datetime.datetime.fromtimestamp(epoch))
		bytes = bytearray([att[i+content_offset+8] for i in range(8)])
		file_altered_time = struct.unpack("<Q", bytes)[0]
		epoch = (file_altered_time-D)/10000000
		file_altered_time = str(datetime.datetime.fromtimestamp(epoch))
		bytes = bytearray([att[i+content_offset+16] for i in range(8)])
		MFT_altered_time = struct.unpack("<Q", bytes)[0]
		epoch = (MFT_altered_time-D)/10000000
		MFT_altered_time = str(datetime.datetime.fromtimestamp(epoch))
		bytes = bytearray([att[i+content_offset+24] for i in range(8)])
		accessed_time = struct.unpack("<Q", bytes)[0]
		epoch = (accessed_time-D)/10000000
		accessed_time = str(datetime.datetime.fromtimestamp(epoch))

		bytes = bytearray([att[i+content_offset+32] for i in range(4)])
		flags_SI = struct.unpack("<L", bytes)[0]
		bytes = bytearray([att[i+content_offset+36] for i in range(4)])
		max_versions = struct.unpack("<L", bytes)[0]
		bytes = bytearray([att[i+content_offset+40] for i in range(4)])
		version = struct.unpack("<L", bytes)[0]
		bytes = bytearray([att[i+content_offset+44] for i in range(4)])
		classID = struct.unpack("<L", bytes)[0]
		try:
			#some entries crash here. The book says these values require version 3.0+, so I assume some entries are out of date
			bytes = bytearray([att[i+content_offset+48] for i in range(4)])
			ownerID = struct.unpack("<L", bytes)[0]
			bytes = bytearray([att[i+content_offset+52] for i in range(4)])
			securityID = struct.unpack("<L", bytes)[0]
			bytes = bytearray([att[i+content_offset+56] for i in range(8)])
			quota_charged = struct.unpack("<Q", bytes)[0]
			bytes = bytearray([att[i+content_offset+64] for i in range(8)])
			USN = struct.unpack("<Q", bytes)[0]
		except:
			#fill those attributes with "missing", just to print
			print("This attribute is an older version, some values may be missing")
			ownerID = "missing"
			securityID = "missing"
			quota_charged = "missing"
			USN = "missing"
		if(isEntry):
			print("file_accessed  ", accessed_time)
			print("Owner ID  " , ownerID)
			print("version number", version)
			print("creation  ", create_time)
			print("Security ID" , securityID)
			print("mft altered:  ", MFT_altered_time)
			print("Update seq#  " , USN)
			
			print("flags  ", end=" ")
			printFlags(flags_SI)
		
			print("max # versions" , max_versions)
			print("Class ID" , classID)
			print("Quota Charged  " , quota_charged)
			print("file altered  ", file_altered_time)
			print("")

	elif (att_type_id == 48):
		if(isEntry):
			print("Type: $FILE_NAME (48) NameLen: (",name_len,")", end="")
			if(non_res):
				print(" Non-Resident  ", end="")
			else:
				print(" Resident  ", end="")
			print(" size:" , att_length)
		#we need to convert all of these times into Windows time		
		D = 116444736000000000
		bytes = bytearray([att[i+content_offset] for i in range(6)])
		parent_dir = getSigned(bytes)
		bytes = bytearray([att[i+content_offset+6] for i in range(2)])
		parent_dir_sequence = (bytes[1]<<8) + (bytes[0])
		bytes = bytearray([att[i+content_offset+8] for i in range(8)])
		create_time = struct.unpack("<Q", bytes)[0]
		epoch = (create_time-D)/10000000
		create_time = str(datetime.datetime.fromtimestamp(epoch))
		bytes = bytearray([att[i+content_offset+16] for i in range(8)])
		file_altered_time = struct.unpack("<Q", bytes)[0]
		epoch = (file_altered_time-D)/10000000
		file_altered_time = str(datetime.datetime.fromtimestamp(epoch))
		bytes = bytearray([att[i+content_offset+24] for i in range(8)])
		MFT_altered_time = struct.unpack("<Q", bytes)[0]
		epoch = (MFT_altered_time-D)/10000000
		MFT_altered_time = str(datetime.datetime.fromtimestamp(epoch))
		bytes = bytearray([att[i+content_offset+32] for i in range(8)])
		accessed_time = struct.unpack("<Q", bytes)[0]
		epoch = (accessed_time-D)/10000000
		accessed_time = str(datetime.datetime.fromtimestamp(epoch))

		bytes = bytearray([att[i+content_offset+40] for i in range(8)])
		len_allocated = struct.unpack("<Q", bytes)[0]
		bytes = bytearray([att[i+content_offset+48] for i in range(8)])
		len_actual = struct.unpack("<Q", bytes)[0]
		bytes = bytearray([att[i+content_offset+56] for i in range(4)])
		flags_FN = struct.unpack("<L", bytes)[0]
		bytes = bytearray([att[i+content_offset+60] for i in range(4)])
		reparse = struct.unpack("<L", bytes)[0]
		len_of_name = att[content_offset+64]
		namespace = att[content_offset+65]
		bytes = bytearray([att[i+content_offset+66] for i in range(2*len_of_name)])
		file_name = ""
		for b in bytes:
			if(b >= 32 and b <= 126):
				file_name +=chr(b)
		if(isEntry):
			print("Alloc. size of file", len_allocated)
			print("Length of name", len_of_name)
			print("MFT mod time", MFT_altered_time)
			print("Namespace", namespace)
			print("Parent dir ( MFT# , seq# )  (", parent_dir,",",parent_dir_sequence,")")
			print("Name", file_name)
			print("Real filesize", len_actual)
			print("Reparse value", reparse)
			print("file access time", accessed_time)
			print("file creation time", create_time)
			print("file mod time", file_altered_time)
			print("flags", end=" ")
			printFlags(flags_FN)
			print("")


	elif (att_type_id == 128):
		if(isEntry):
			print("Type: $DATA (128) NameLen: (",name_len,")", end="")
			if(non_res):
				print("Non-Resident  ", end="")
			else:
				print("Resident  ", end="")
			print("size:" , att_length)
		else:
			#this is where we get the runlist if this is entry 0
			count = 0
			RL_offsets = []
			RL_fields = []
			runlist = []
			while(1):
				#need to split byte 64 into two nibbles
				bytes = att[64 + count]
				offset_length = bytes >> 4
				RL_field_length = bytes & 0x0F
				if(offset_length == 0 and RL_field_length == 0):
					#if both of these values are 0, there must be nothing left
					break
				bytes = bytearray([att[i+65+count] for i in range(RL_field_length)])
				RL_field = getSigned(bytes)
				bytes = bytearray([att[i+65+RL_field_length+count] for i in range(offset_length)])
				RL_offset = getSigned(bytes)
				if count == 0:
					RL_offsets.append(RL_offset)
				else:
					RL_offset += RL_offsets[len(RL_offsets) - 1]
					RL_offsets.append(RL_offset)
				RL_fields.append(RL_field)
				count+= RL_field_length + offset_length + 1
			#after this loop, we have two arrays, one of offsets and one of sizes
			count = 0
			while (count < len(RL_fields)):
				#here we combine those arrays into one array of ranges	
				runlist.append(RL_offsets[count])
				runlist.append(RL_fields[count]+RL_offsets[count] - 1)
				count+=1
			return(runlist)
	#we don't parse these ones, but we still need to print their information if isEntry = 1
	elif(isEntry):
		if (att_type_id == 32):
			print("Type: $ATTRIBUTE_LIST (32)", end="")
		if (att_type_id == 64):
			print("Type: $OBJECT_ID (64)", end="")
		if (att_type_id == 192):
			print("Type: $REPARSE_POINT (192)", end="")
		if (att_type_id == 144):
			print("Type: $INDEX_ROOT (144)", end="")
		if (att_type_id == 160):
			print("Type: $INDEX_ALLOCATION (160)", end="")
		if (att_type_id == 176):
			print("Type: $BITMAP (176)", end="")
		print("NameLen: (",name_len,")", end="")
		if(non_res == 1):
			print(" Non-Resident  ", end="")
		else:
			print(" Resident  ", end="")
		print(" size:" , att_length)
		print("		(unparsed attribute) ")


def main():
	'''
	Tries to parse the given NTFS image
	Calls usage() if there is an error, calls parse() otherwise
	'''
	try:
		entry = int(sys.argv[1])
		image = sys.argv[2]
		fd = open(image, "rb")
	except:
		usage()
	parse(entry,fd)


if __name__ == '__main__':
	main()
