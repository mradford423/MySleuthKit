<h1> Overview </h1>
<p>This is my sleuth kit used for Digital Forensics, CS 365. Some of the materials in the testing directory are borrowed from testing material used for the course.</p>
<p>MySleuthKit consists of various tools that could be used in a real world forensics situation to examine things such as JPEG images, disk images, or various other types of files. Some of my tools are based on existing functions of The Sleuth Kit (http://www.sleuthkit.org/sleuthkit/), which is a collection of tools written in C used in digital investigations. Other tools are based on existing Linux commands that are useful when looking for evidence. Please note that these commands were written in Python 3.2, and some syntax will not work on any version of Python earlier than 3.</p>

<h1> The Tools </h1>
<h2>EXIF_data</h2>
<pre><code>python3 EXIF_data.py file.jpg</code></pre>
<p>This tool is used to parse the EXIF metadata of a JPEG file. It does this by finding all of the metadata markers in the JPEG, and calling an additional function when it finds the EXIF tag. This function prints out all of the IPD entries and their data, which can be useful in an investigation to find information such as when a photo was taken, or where it was taken if taken on a GPS enabled device. Please note that this tool only works for images with Big-Endian format. In addition, somes images may not have any EXIF metadata, or may be missing certain key IPD entries. I have included two JPEGs, in the testing directory, 'test1.jpg' and 'test2.jpg', that do have Big-Endian formatting and EXIF metadata for testing purposes.</p>
<br>
<h2>FAT16</h2>
<pre><code>python3 FAT16.py fat16image.dd</code></pre>
<p>This tool parses the boot sector of a FAT16 formatted drive to give information about the whole drive. It does this by checking for certain key values at various byte locations in the boot sector to find information such as the OEM name, before moving on to the file system layout. It prints the entire layout in sectors, which can help an investigator know where in the file system to look for evidence.  I have included a FAT16 formatted drive image in the testing directory called '6-fat-undel.dd' for testing purposes</p>
<br>
<h2>NTFS</h2>
<pre><code>python3 NTFS.py entry_number NTFSimage.dd</code></pre>
<p>This tool gives information about a given entry in the NTFS file table of an NTFS formatted drive. It does this by first parsing the 0 entry of the file table, as that gives us information about the location of all of the other tables in the file system. Then, it jumps to the location of the the entry that we're looking for and begins printing information about that entry, including all of its attributes. In addition, it prints the leftover slack data of the entry, which is often garbage, but could be used as a place to hide evidence. I have included a NTFS formatted drive image in the testing directory called 'ntfs-img-kw-1.dd' for testing purposes.</p>
<br>
<h2>Hexdump</h2>
<pre><code>python3 hexdump.py file</code></pre>
Alternatively for larger files: <pre><code>python3 hexdump.py file | more</code></pre>
<p>This tool prints out the hex values of the contents of a file, similar to the 'hexdump' command in Linux. It first prints out the line number in hex, then a line of 16 bytes form the file in hex, the the ASCII representation of those 16 bytes if one exists. This tool can be useful for investigators to look through the raw data of a file to find evidence.</p>
<br>
<h2>Strings</h2>
<pre><code>python3 strings.py minimum_line_length file</pre></code>
<p>This tool prints out an ASCII representation of the contents of a file, similar to the 'strings' command in Linux. It does this by parsing the file, byte-by-byte, and if it gets a line longer than the user given minimum length, it prints the line. This will often result in unreadable data, but is still useful to an investigator, as the things that are readable could be useful evidence.</p>

