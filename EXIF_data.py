#!/usr/bin/env python3
import sys

TAGS={  0x100:  "ImageWidth",
        0x101:  "ImageLength",
        0x102:  "BitsPerSample",
        0x103:  "Compression",
        0x106:  "PhotometricInterpretation",
        0x10A:  "FillOrder",
        0x10D:  "DocumentName",
        0x10E:  "ImageDescription",
        0x10F:  "Make",
        0x110:  "Model",
        0x111:  "StripOffsets",
        0x112:  "Orientation",
        0x115:  "SamplesPerPixel",
        0x116:  "RowsPerStrip",
        0x117:  "StripByteCounts",
        0x11A:  "XResolution",
        0x11B:  "YResolution",
        0x11C:  "PlanarConfiguration",
        0x128:  "ResolutionUnit",
        0x12D:  "TransferFunction",
        0x131:  "Software",
        0x132:  "DateTime",
        0x13B:  "Artist",
        0x13E:  "WhitePoint",
        0x13F:  "PrimaryChromaticities",
        0x156:  "TransferRange",
        0x200:  "JPEGProc",
        0x201:  "JPEGInterchangeFormat",
        0x202:  "JPEGInterchangeFormatLength",
        0x211:  "YCbCrCoefficients",
        0x212:  "YCbCrSubSampling",
        0x213:  "YCbCrPositioning",
        0x214:  "ReferenceBlackWhite",
        0x828F: "BatteryLevel",
        0x8298: "Copyright",
        0x829A: "ExposureTime",
        0x829D: "FNumber",
        0x83BB: "IPTC/NAA",
        0x8769: "ExifIFDPointer",
        0x8773: "InterColorProfile",
        0x8822: "ExposureProgram",
        0x8824: "SpectralSensitivity",
        0x8825: "GPSInfoIFDPointer",
        0x8827: "ISOSpeedRatings",
        0x8828: "OECF",
        0x9000: "ExifVersion",
        0x9003: "DateTimeOriginal",
        0x9004: "DateTimeDigitized",
        0x9101: "ComponentsConfiguration",
        0x9102: "CompressedBitsPerPixel",
        0x9201: "ShutterSpeedValue",
        0x9202: "ApertureValue",
        0x9203: "BrightnessValue",
        0x9204: "ExposureBiasValue",
        0x9205: "MaxApertureValue",
        0x9206: "SubjectDistance",
        0x9207: "MeteringMode",
        0x9208: "LightSource",
        0x9209: "Flash",
        0x920A: "FocalLength",
        0x9214: "SubjectArea",
        0x927C: "MakerNote",
        0x9286: "UserComment",
        0x9290: "SubSecTime",
        0x9291: "SubSecTimeOriginal",
        0x9292: "SubSecTimeDigitized",
        0xA000: "FlashPixVersion",
        0xA001: "ColorSpace",
        0xA002: "PixelXDimension",
        0xA003: "PixelYDimension",
        0xA004: "RelatedSoundFile",
        0xA005: "InteroperabilityIFDPointer",
        0xA20B: "FlashEnergy",                  # 0x920B in TIFF/EP
        0xA20C: "SpatialFrequencyResponse",     # 0x920C    -  -
        0xA20E: "FocalPlaneXResolution",        # 0x920E    -  -
        0xA20F: "FocalPlaneYResolution",        # 0x920F    -  -
        0xA210: "FocalPlaneResolutionUnit",     # 0x9210    -  -
        0xA214: "SubjectLocation",              # 0x9214    -  -
        0xA215: "ExposureIndex",                # 0x9215    -  -
        0xA217: "SensingMethod",                # 0x9217    -  -
        0xA300: "FileSource",
        0xA301: "SceneType",
        0xA302: "CFAPattern",                   # 0x828E in TIFF/EP
        0xA401: "CustomRendered",
        0xA402: "ExposureMode",
        0xA403: "WhiteBalance",
        0xA404: "DigitalZoomRatio",
        0xA405: "FocalLengthIn35mmFilm",
        0xA406: "SceneCaptureType",
        0xA407: "GainControl",
        0xA408: "Contrast",
        0xA409: "Saturation",
        0xA40A: "Sharpness",
        0xA40B: "DeviceSettingDescription",
        0xA40C: "SubjectDistanceRange",
        0xA420: "ImageUniqueID",
        0xA432: "LensSpecification",
        0xA433: "LensMake",
        0xA434: "LensModel",
        0xA435: "LensSerialNumber"
}
bytes_per_component = (0,1,1,2,4,8,1,1,2,4,8,4,8)



def usage():
	"""
        Returns an error if run without being given a JPEG
	"""
	print("Error:")
	print("USAGE: hw3.py image.jpg")
	print("exiting...")
	sys.exit()

def read(fd):
	"""
	Reads in a JPEG
	Verifies that it is in fact a JPEG
	Finds all of the markers in the JPEG, and prints their location, number and size
	When it finds the EXIF marker, it calls exif_read() before continuing
	"""
	offset = 0
	bytes = fd.read(2)
	offset+= 2
	if(bytes != b'\xff\xd8'):
		usage()
	bytes = fd.read(4)
	offset+= 4
	found = 0
	while(1): #this loops through all of the markers and prints their info
		if(bytes[0] != 0xFF): #This should never happen
			print("uh oh...")
			break
		print("[0x%04x" % offset + "] Marker 0xFF%02X" % bytes[1] + " size=0x%02X" % bytes[2] + "%02X" % bytes[3])
		size = (bytes[2]<<8) + (bytes[3]<<0)
		if(bytes[1] == 0xE1 and found == 0):
			exif_read(fd,size,offset)
			fd.seek(offset)
			found = 1
		else:
			if(bytes[1] == 0xDA):
				break
			offset+= size-2
			fd.read(size - 2)
			bytes = fd.read(4)
			offset+= 4

def exif_read(fd,size,offset):
	'''
	Reads therough the EXIF metadata
	If the JPEG is little endian, the programming stops
	Finds the beginning of the IPD entires, and then prints the number of IPD entries
	For each IPD entry, it prints the tag name in hex, the tag name in English, and the data stored in the entry
	'''
	data = fd.read(10)
	offset+= 10
	start = offset - 3
	if(data[6] != 0x4d or data[7] != 0x4d):
		print()
		print('ERROR: this JPEG is little endian')
		print('big endian required')
		print('closing...')
		sys.exit()
	data = fd.read(4)
	offset+= data[3] - 4
	fd.read(data[3] - 8)
	data = fd.read(2)
	offset+= 2
	entries = (data[0]<<8) + (data[1])
	print('Number of IPD Entries = %x' % entries)
	i = 0
	while(i < entries): #all the IPD entries are read, parsed and printed in this loop
		data = fd.read(12)
		offset+= 12
		tag = (data[0]<<8) + (data[1])
		format = (data[2]<<8) + (data[3])
		if(format == 1 or format == 2 or format == 3 or format == 4 or format == 5 or format == 7): #only print the data if it is one of these formats
			components = (data[4]<<32) + (data[5]<<16) + (data[6]<<8) + (data[7])
			length = bytes_per_component[format] * components
			d = (data[8]<<32) + (data[9]<<16) + (data[10]<<8) + (data[11])
			if(d >= 4):
				fd.seek(start + d - 1)
				d = fd.read(length - 1)
				fd.seek(offset)
				temp = ''
				for b in d:
					if(b >= 32 and b <= 126):
						temp+=chr(b)
					else:
						temp+=str(b)       
			print('%04X' % tag + ' ' + TAGS[tag] + ' ', temp)
		else: #print this otherwise
			print('' + tag + ' ' + TAGS[tag])
		i+= 1



def main():
	"""
	Trys to open a JPEG to read.
	Calls usage() if there is an error, calls read() otherwise
	"""
	try:
		image = sys.argv[1]
		fd = open(image, "rb")
	except:
		usage()
	read(fd)



if __name__ == '__main__':
	main()
