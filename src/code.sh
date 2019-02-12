#!/bin/bash
#

# The following line causes bash to exit at any point if there is any error
# and to output each line as it is executed -- useful for debugging
set -e -x -o pipefail

dx-download-all-inputs

mv /home/dnanexus/in/transcript_file/$transcript_file_prefix.txt /home/dnanexus/$transcript_file_prefix.txt

#eval "$(ssh-agent -s)"
#ssh-add ~/.ssh/id_rsa
#git clone git@github.com:woook/mokabed.git
 
#cat /home/dnanexus/.ssh/id_rsa.pub | sudo tee -a /home/dnanexus/.ssh/authorized_keys
#sudo cp ~/.ssh/* /root/.ssh/
#chmod 600 /home/dnanexus/.ssh/id_rsa 
#ssh-keyscan -t rsa github.com 2>&1 >> /home/dnanexus/.ssh/known_hosts

#ssh -vT git@github.com


#git clone git@github.com:woook/mokabed.git

# capture github API key
GITHUB_KEY=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:mokabed_github_key)

git clone https://$GITHUB_KEY@github.com/woook/mokabed.git

cd mokabed

git checkout production 
ls

#bash ~/Anaconda2-4.2.0-Linux-x86_64.sh -b -p $HOME/Anaconda
#export PATH="$HOME/Anaconda/bin:$PATH"

#cp /usr/local/lib/python2.7/dist-packages/*  /home/dnanexus/Anaconda/lib/python2.7/site-packages/
#conda list

#--up 5 --down 5 --codingup 5 --codingdown 5 --outputfile /home/ryank/mokabed/LiveBedfiles/Pan492data.bed --logfile /home/ryank/mokabed/LiveBedfiles/Pan492_LogFile.txt --minuschr --mergeboundaries --genes /home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan492.txt 

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
  opts="$opts --genes /home/dnanexus/$transcript_file_prefix.txt"
elif [ "$genes_or_transcripts" == "TRANSCRIPTS" ]; then
opts="$opts --useaccessions --transcripts /home/dnanexus/$transcript_file_prefix.txt"
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
outputfile=" --outputfile /home/dnanexus/out/Output_files/$pannumber$bedfile_name"
#set output file
logfile=" --logfile /home/dnanexus/out/Output_files/$pannumber$logfile_name"

mkdir -p /home/dnanexus/out/Output_files/

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
