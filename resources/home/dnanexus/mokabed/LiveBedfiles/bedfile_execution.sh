#!/bin/bash

#qsub -p -50 -q shortterm.q,longterm.q,test.q bedfile_execution.sh 
##Set the working directory to the current one
#$ -cwd

##Output STDERR and STDOUT to output file place in NGSpipeline_STDOUT_files in Home directory
#$ -j y
#$ -o /home/ryank/NGSpipeline_STDOUT_files


##Set the shell 
#$ -S /bin/bash

##Set the name of the Job
#$ -N bedfile_executiuon

##Set the Parallel Environment
#$ -pe threaded 2

##Email me when job starts and finishes
#$ -m be
#$ -M kevin.ryan@viapath.co.uk

module load python/2.7


python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/ryank/Databases/Test/OldCM_CNV_pre_processed_LogFile.txt --outputfile /home/ryank/Databases/Test/OldCM_CNV_pre_processedBedFile.bed --transcripts /home/ryank/Databases/Transcripts/CMpanelTranscriptsOld.txt --CNVoutput /home/ryank/Databases/Test/OldCMCNVdata.bed

python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --logfile /home/ryank/Databases/Test/OldCM_LogFile.txt --outputfile /home/ryank/Databases/Test/OldCMdata.bed --transcripts /home/ryank/Databases/Transcripts/CMpanelTranscriptsOld.txt

