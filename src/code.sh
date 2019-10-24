#!/bin/bash
#

# The following line causes bash to exit at any point if there is any error
# and to output each line as it is executed -- useful for debugging
set -e -x -o pipefail

dx-download-all-inputs --parallel

echo $down
echo $up
echo $coding_up
echo $coding_down
echo $genes_or_transcripts
echo $minuschr
echo $mergeboundaries


opts=""
if [ "$coding_up" != 0 ]; then
  opts="$opts --codingup $coding_up"
else
opts="$opts --codingup 0"
fi

if [ "$coding_down" != 0 ]; then
  opts="$opts --codingdown $coding_down"
else
opts="$opts --codingdown 0"
fi

if [ "$up" != "" ]; then
  opts="$opts --up $up"
fi

if [ "$down" != "" ]; then
  opts="$opts --down $down"
fi

if [ "$genes_or_transcripts" == "GENES" ]; then
  opts="$opts --genes $transcript_file_path"
elif [ "$genes_or_transcripts" == "TRANSCRIPTS" ]; then
opts="$opts --useaccessions --transcripts $transcript_file_path"
fi

if [ "$minuschr" == "true" ]; then
  opts="$opts --minuschr"
fi

if [ "$mergeboundaries" == "true" ]; then
  opts="$opts --mergeboundaries"
fi

# capture pan number from input file
pannumber=$transcript_file_prefix
echo $pannumber
echo $transcript_file_prefix
bedfile_name="data.bed"
logfile_name="_LogFile.txt"

#set logfile
mkdir -p /home/dnanexus/out/Output_files/
outputfile=" --outputfile /home/dnanexus/out/Output_files/$pannumber$bedfile_name"
#set output file
logfile=" --logfile /home/dnanexus/out/Output_files/$pannumber$logfile_name"

#add app version to logfile
version=$(cd /home/dnanexus/mokabed; git describe --tag) 
echo "app version as defined by git tag = ${version}" > /home/dnanexus/out/Output_files/$pannumber$logfile_name

#mkdir -p /home/dnanexus/out/Output_files/

echo $opts
echo $logfile
echo $outputfile

#
# Run mokabed
#
/home/dnanexus/anaconda2/bin/python2.7 /home/dnanexus/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/OOBed7_uses_mirrored_database_.py $opts $outputfile $logfile

#
# Upload results
#
#mark-section "uploading results"

dx-upload-all-outputs

#mark-success
