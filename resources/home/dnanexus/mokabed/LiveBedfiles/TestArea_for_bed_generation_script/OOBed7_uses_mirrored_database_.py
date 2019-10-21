#!/usr/bin/python
import sys, getopt, os
import pandas as pd
import cruzdb
from sqlalchemy import or_
from versionnumber_newtest import Liveaccversion, LiveRefLink
import time, datetime, subprocess
from copy import deepcopy
import subprocess
import re
import numpy as np
from sambambaconvert import Sambamba

#Need to module load python/2.7
#Need to provide arguments 'up' to include the 5'UTR and 'down' to include the 3'UTR and the associated list of accession numbers of the associated transcripts
#Examples of how to use the script

#Version1 FH panel bed file 
#Set 5'UTR -30, 5'coding exon -30, 3'UTR +20, 3'coding exon +20
#Set Chromosomal coordinate list +-0
#Note that convention states that chromosomal coordinate data set out as chrx:xxx-xxx is 1-based. When copying this data into bed format to create the chromcoordinate file the 5' values are converted to 0 based ie each 5' value is subtracted by 1

##transcriptfile set up takes the following format
##'Title can take spaces 0PanNo'^I$
##'NM_accession_number'^I'GeneName'$
##Repeat preceding row as appropriate

#python OOBed3.py --codingup 30  --codingdown 20 --up 30 --down 20 --coordinatefile /home/kevin/Documents/NGS_Pipeline/BedFiles/Chromcoordinates/FHchromcoordinates.txt --coordup 0 --coorddown 0 --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/FHver1BedFile.csv --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/FHtranscripts.txt
#python OOBed5.py --codingup 0 --codingdown 0 --coordinatefile /home/kevin/Documents/NGS_Pipeline/BedFiles/Chromcoordinates/FHchromcoordinates.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/NRXNcodingregionsBedFile.csv --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/NRXNtranscripts.txt
#python OOBed5.py --codingup 30 --codingdown 20 --up 30 --coordinatefile /home/kevin/Documents/NGS_Pipeline/BedFiles/Chromcoordinates/FHchromcoordinates.txt --coordup 0 --coorddown 0 --StopFlank 50 --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/FHver2BedFile.csv --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/FHtranscripts.txt
#python OOBed5.py --codingup 30 --codingdown 20 --up 30 --StopFlank 50 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TP53only_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TP53onlyBedFile.csv --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/TP53onlyTranscripts.txt
#python OOBed5.py --codingup 30 --codingdown 20 --up 30 --StopFlank 50 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/WholeExomeAnalysis3/Pantest_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/WholeExomeAnalysis3/Pantest.csv --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/Holdingfolder/Pan59.txt

#python /home/kevin/Documents/NGS_Pipeline/BedemoveFiles/OOBed5.py --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/WholeExomeAnalysis/NM_032470PlusMinus5_LogFile.txt --coordinatefile /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/Pantranscriptfiles/NM_032470Coordinates.txt --coordup 5 --coorddown 5 --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/NM_032470PlusMinus5BedFile.csv
#python /home/kevin/Documents/NGS_Pipeline/BedFiles/OOBed5.py --codingup 5 --codingdown 5 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/WholeExomeAnalysis/${bedname}_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/WholeExomeAnalysis/${bedname}data.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/transcriptfiles/$transcript

#python /home/kevin/Documents/NGS_Pipeline/BedFiles/OOBed5.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/KBTBD13_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/KBTBD13data.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/KBTBD13_CMpanelMissingGene.txt

#python /home/kevin/Documents/NGS_Pipeline/BedFiles/OOBed5.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/OldCM_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/OldCMdata.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/CMpanelTranscriptsOld.txt

#python /home/kevin/Documents/NGS_Pipeline/BedFiles/OOBed5.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/OldCM_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/OldCMdata.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/CM_Panel/CMpanelTranscriptsOld.txt

#python OOBed5.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/NewCM_CNV_pre_processed_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/NewCM_CNV_pre_processedBedFile.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/CMpanelTranscriptsNew.txt

#python OOBed6.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TestNewCM_CNV_pre_processed_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TestNewCM_CNV_pre_processedBedFile.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/CMpanelTranscriptsNew.txt --CNVoutput /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/NewTestCMCNVdata.bed

#python OOBed6.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/ryank/Databases/BRCA_LogFile.txt --outputfile /home/ryank/Databases/BRCAdata.bed --transcripts /home/ryank/Databases/Transcripts/BRCATranscripts.txt --CNVoutput /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/NewTestCMCNVdata.bed

#python OOBed6.py --codingup 30 --codingdown 20 --coordinatefile /home/kevin/Documents/NGS_Pipeline/BedFiles/Chromcoordinates/BRCAchromcoordinates.txt --coordup 30 --coorddown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/BRCA_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/BRCAdata.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/BRCA1+2Transcriptsonly.txt

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/PTEN_CNV_pre_processed_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/PTEN_CNV_pre_processedBedFile.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/PTENonlyTranscripts.txt --CNVoutput /home/kevin/Documents/NGS_Pipeline/BedFiles/PTENCNVdata.bed

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/PTEN_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/PTENdata.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/PTENonlyTranscripts.txt

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/STK11_CNV_pre_processed_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/STK11_CNV_pre_processedBedFile.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/STK11onlyTranscripts.txt --CNVoutput /home/kevin/Documents/NGS_Pipeline/BedFiles/STK11CNVdata.bed

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/STK11_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/STK11data.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/STK11onlyTranscripts.txt

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TP53_CNV_pre_processed_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TP53_CNV_pre_processedBedFile.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/TP53onlyTranscripts.txt --CNVoutput /home/kevin/Documents/NGS_Pipeline/BedFiles/TP53CNVdata.bed

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TP53_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/TP53data.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/TP53onlyTranscripts.txt

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/OldCM_CNV_pre_processed_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/OldCM_CNV_pre_processedBedFile.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/CMpanelTranscriptsOld.txt --CNVoutput /home/kevin/Documents/NGS_Pipeline/BedFiles/OldCMCNVdata.bed

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/Test/OldCM_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/Test/OldCMdata.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/CMpanelTranscriptsOld.txt

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --up 0 --down 0 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/Test/NewCM_CNV_pre_processed_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/Test/NewCM_CNV_pre_processedBedFile.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/CMpanelTranscriptsNew.txt --CNVoutput /home/kevin/Documents/NGS_Pipeline/BedFiles/Test/NewCMCNVdata.bed

#python OOBed7_uses_mirrored_database_.py --codingup 30 --codingdown 20 --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/NewCM_LogFile.txt --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/NewCMdata.bed --transcripts /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/CMpanelTranscriptsNew.txt



class Bedfile:

	def __init__(self):
		self.Chr = []
		self.Start=[]
		self.Stop=[]
		self.Accession=[]
		self.GeneName=[]
		self.up = ''
		self.upstream = ''
		self.down = ''
		self.downstream = ''
		self.coding = ''
		self.codingup = ''
		self.codingdown = ''
		self.transcripts = ''
		self.transcriptlist = ''
		self.useaccessionslist = ''
		self.mergeboundariesboolean = ''
		self.genes = ''
		self.coordinatefile = ''
		self.coordinates = ''
		self.coordup = ''
		self.coorddown = ''
		self.outputfile = ''
		self.output = ''
		self.CNVoutput = ''
		self.CNVoutputboolean = ''
		self.StartFlanking = ''
		self.StartFlank = ''
		self.StopFlanking = ''
		self.StopFlank = ''
		self.bedfile = pd.DataFrame()
		self.bed = pd.DataFrame()
		self.chrlist = []
		self.listlength = 0
		self.Chrom = []
		self.Acc = []
		self.Gene = []
		self.Startmerge = []
		self.Stopmerge = []
		self.lastgene=''
		self.prevselfstart = []
		self.prevselfstop = []
		self.entrezid = []
		self.entrezidmerge = []
		self.g = ''
		self.refGene = ''
		self.refseqoutput = ''
		self.minuschr = ''
		self.strand = []
		self.strandmerge = []
		self.listgeneposition = []
	

	def usage(self):

		usage = """
		-h --help Prints this
		-m --name of mokafile  	Moka input file to be cross-referenced
		-s --name of sangerfile	Sanger input file to be checked against
		-o --name of outputfile	Output file to be generated
		Sangercheck will cross-reference variants generated by the Moka Pipeline against Mutation Reports generated by the Clinical Scientist from the NextGene software
		"""
		print usage
	
	def refseqfile(self):
		
		# Load bed file output automatically into the refseqfile		
		bed = pd.read_table(self.outputfile, header= 1, dtype={'#Chr':object, 'Start':int, 'Stop':int, 'EntrezID':int, 'Gene_Accession':object})

		

		# Generate columns in Pandas series format which will be used to generate the RefSeq columns
		Chrser = bed.groupby(['EntrezID', '#Chr'])['#Chr'].apply(lambda x: ''.join(sorted(set(map(str, list(x))))))
		Startser =bed.groupby(['EntrezID', '#Chr'])['Start'].apply(lambda x: ",".join(map(str, list(x))))
		Stopser =bed.groupby(['EntrezID', '#Chr'])['Stop'].apply(lambda x: ",".join(map(str, list(x))))
		NMacc = bed.groupby(['EntrezID', '#Chr'])['Gene_Accession'].apply(lambda x: ''.join(sorted(set(list(x)))))
		exonCount = bed.groupby(['EntrezID', '#Chr'])['Start'].apply(len)
		Stranddf = pd.DataFrame(zip(self.strand, self.entrezid, self.Chr),  columns = ["Strand","EntrezID", "#Chr"])
		Newstrand = Stranddf.groupby(['EntrezID', "#Chr"])["Strand"].apply(lambda x: ''.join(sorted(set(map(str, list(x))))))
		txStart = bed.groupby(['EntrezID', '#Chr'])['Start'].apply(lambda x: list(x)[0])
		txEnd = bed.groupby(['EntrezID', '#Chr'])['Stop'].apply(lambda x: list(x)[-1])
		cdsStart = bed.groupby(['EntrezID', '#Chr'])['Start'].apply(lambda x: int(list(x)[0]))
		cdsEnd = bed.groupby(['EntrezID', '#Chr'])['Stop'].apply(lambda x: int(list(x)[-1]))
		score = pd.Series(index = Chrser.index)
		name2 = bed.groupby(['EntrezID', '#Chr'])['Gene_Accession'].apply(lambda x: ''.join(sorted(set(list(x)))).split(';')[0])
		cdsStartStat = pd.Series(index = Chrser.index)
		cdsEndStat = pd.Series(index = Chrser.index)
		exonFrameslist = []
		# Set exonFrames to 0
		for val in exonCount.values:
			ef = ['0'] * val
			efstr = ','.join(ef)
			#efstrformatted = efstr[1:-1]
			exonFrameslist.append(efstr)
		
		#Exonframedf = pd.DataFrame(zip(self.strand, self.entrezid),  columns = ["Strand","EntrezID"])
		exonFrames = pd.Series(exonFrameslist, index = Chrser.index)

		# Concatanate the list of pandas series into a single dataframe which is to be outed as a text file
		df = pd.DataFrame(zip(NMacc.values, Chrser.values, Newstrand.values, txStart.values, txEnd.values, cdsStart.values, cdsEnd.values, exonCount.values, Startser.values, Stopser.values, score.values, name2.values, cdsStartStat.values, cdsEndStat.values, exonFrames.values), columns = ['name', 'chrom', 'strand', 'txStart', 'txEnd', 'cdsStart', 'cdsEnd', 'exonCount', 'exonStarts', 'exonSEnds', 'score', 'name2', 'cdsStartStat', 'cdsEndStat', 'exonFrames'], index=Chrser.index)
		
		#df = pd.concat([NMacc.reset_index(), Chrser.reset_index().reset_index().reset_index().reset_index(), Newstrand.reset_index().reset_index().reset_index(), txStart.reset_index().reset_index(), txEnd.reset_index()], axis=1)
		
		df["score"] = df["score"].astype(str)
		df["cdsStartStat"] = df["cdsStartStat"].astype(str)
		df["cdsEndStat"] = df["cdsEndStat"].astype(str)
		# Replace X and Y values in chrom column with numerical values 23 ands 24. This is required for sorting the columns in numerical order
		
		df['chrom'].replace(['X', 'Y'], ['23', '24'], inplace =True)
		# Convert the chrom, cdsStart and cdsEnd columns to integers. This is required for sorting the columns in numerical order
		df['chrom'] = df['chrom'].astype(str).astype('int')
		df['cdsStart'] = df['cdsStart'].astype(str).astype('int')
		df['cdsEnd'] = df['cdsEnd'].astype(str).astype('int')
		
		df.sort(['chrom', 'cdsStart', 'cdsEnd'], inplace = True)
		df['chrom'] = df['chrom'].astype(str)
		df['chrom'].replace(['23', '24'], ['X', 'Y'], inplace =True)
		df2 = df.fillna('NULL')
		df2 = df2.reset_index().drop("#Chr", axis=1)
		df2.set_index('EntrezID', inplace=True)
		#df2.reset_index(inplace=True).drop("#Chr", axis=1)
		

		# Ammend index header so it is in line with RefSeq format
		df2.index.name = "#bin"
	
		# Generate file path without extension
		self.refseqoutput = os.path.splitext(self.outputfile)[0] + "RefSeqFormat.txt"
		
		# Output dataframe as a RefSeq flat file
		df2.to_csv(path_or_buf=self.refseqoutput, sep='\t')
	
	def filereader(self):
		
		if self.coordinatefile:
			self.bed = pd.read_table(self.coordinatefile, header= 0)
		if self.genes:
			self.bed = pd.read_table(self.genes, header= 0)
		if self.transcripts:
			# check the transcript file has a header line
			with open(self.transcripts, 'r') as f:
				# read the first line only
				first_line = f.readline()
			# check the first line doesn't contain "NM_" and the header contains a string that should be present in at least one of the column headers (header is GuysAccession	approvedsymbol	GuysAccessionVersion)
			if "Accession" in first_line and "NM_" not in first_line:
				# read the file into a pandas table
				self.bed = pd.read_table(self.transcripts, header= 0)
			else:
				# if no header report the missing header and exit
				sys.exit("missing header in transcript file")

	def coordfile(self):
		#Set up bed file using a bed file where the start positions for each exon are base 0
		#Bed files need to contain headers in first row Chr, Start, Stop, Accession, GeneName, and all rows need to contain the same number of tab delimited spaces
		bed = pd.read_table(self.coordinatefile, header= 0)

		startnumber = int(self.coordup)
		endnumber = int(self.coorddown)
		newstart = bed.Start - startnumber
		self.Start.extend(int(newstart))
		newstop = bed.Stop + endnumber
		self.Stop.extend(int(newstop))
		#Append Accessions for this list
		self.Accession.extend(bed.Accession)
		#Append gene names for this list
		self.GeneName.extend(bed.GeneName)
		#Append Chr numbers for this list
		self.Chr.extend(bed.Chr)
		
	def bedsplitter(self):
		#bed = pd.read_table(sys.argv[1], header= 0)
		#print self.bedfile
		Delta = []
		Newstart = []
		Newend = []
		Chromosome = []
		Acc = []
		Name = []
		Start = self.bedfile.Start
		Stop = self.bedfile.Stop
		#print Stop
	
		counter = 0
		for row in Start:
			#Difference = (bed.Stop[counter] -bed.Start[counter])/50
			#Difference = str(Difference).split('.')
			#Delta.append(Difference[0])
			Newstart.append(self.bedfile.Start[counter])
			Chromosome.append(self.bedfile.index[counter])
			Acc.append(self.bedfile.Accession[counter])
			Name.append(self.bedfile.GeneName[counter])
			while (row + 50 < self.bedfile.Stop[counter]) and (self.bedfile.Stop[counter] -row > 75):
				row = row + 50
				Newend.append(row)
				row += 1
				Newstart.append(row)
				Chromosome.append(self.bedfile.index[counter])
				Acc.append(self.bedfile.Accession[counter])
				Name.append(self.bedfile.GeneName[counter])
			Newend.append(self.bedfile.Stop[counter]) 
		
		
			counter += 1
		
		Chromosome = pd.Series(Chromosome)
		Newstart = pd.Series(Newstart)
		Newend = pd.Series(Newend)
		Acc = pd.Series(Acc)
		Name = pd.Series(Name)
		#Reminder you need to call the values function 
		Chromosome = Chromosome.values
		Newstart = Newstart.values
		Newend = Newend.values
		Acc = Acc.values
		Name = Name.values
		CNVoutputfile = pd.DataFrame(zip(Newstart, Newend, Acc, Name),  columns = ["Start", "Stop", "Accession", "Names"], index=[Chromosome])
		CNVoutputfile.index.name = "#Chr"
		CNVoutputfile.to_csv(path_or_buf=self.CNVoutput, sep='\t')
		
	def writefile(self):
	#Write columns to a csv bed file
	# Once the final gene has been processed then re-define the lists to be outputted to the final bed file
		if self.Startmerge:
			self.Start = self.Startmerge
		if self.Stopmerge:	
			self.Stop = self.Stopmerge
		if self.Chrom:
			self.Chr = self.Chrom
		if self.Acc:
			self.Accession = self.Acc
		if self.Gene:
			self.GeneName = self.Gene
		if self.entrezidmerge:
			self.entrezid = self.entrezidmerge
		if self.strandmerge:
			self.strand = self.strandmerge
	
		Chr = pd.Series(self.Chr)	
		Start = pd.Series(self.Start)
		Stop = pd.Series(self.Stop)
		#Re-format GeneName and Accession columns so that they are merged using a semicolon delimiter
		Accession_formatted = map(lambda x: re.sub('[\[\'\] ]', '', str(x)), self.Accession)
		Gene_Accession = map(lambda (x,y): x + ";" + y, zip(self.GeneName, Accession_formatted))
		Gene_Acc = pd.Series(Gene_Accession)
		#Accession = pd.Series(self.Accession)
		#GeneName = pd.Series(self.GeneName)
		Entrezid = pd.Series(self.entrezid)
		#Needed to ammend this script as updated Pandas was printing index number and data type info field as well as the values.
		#To print just the values I need to re-assign the Chr, Start and Stop series to just the values using the .values function
		Chr = Chr.values
		# If --minuschr command is issued
		if self.minuschr:
			Chrremoved = map( lambda x: x.replace( 'chr', ''), Chr)
			self.Chr = Chrremoved

		Start = Start.values
		Stop = Stop.values

		self.bedfile = pd.DataFrame(zip(Start, Stop, Entrezid, Gene_Acc),  columns = ["Start", "Stop", "EntrezID", "Gene_Accession"], index=[self.Chr])
		#print self.bedfilepandas indexing
		
		#bedfile = pd.DataFrame(zip(Start, Stop, GeneName),  columns = ["Start", "Stop", "GeneName"], index=[Chr])

		#Check if all values in Start column are less than the corresponding values in the Stop column
		counter=0
		for row in Start:
			
			if Start[counter] > Stop[counter]:
				print "Error on line ", counter," Not all Start values are less than corresponding Stop values"
				
			counter += 1
		#self.bedfile.sort_values("Stop", ascending=True,inplace=True)
		#self.bedfile.sort_values("Start",ascending=True, inplace=True)
		#self.bedfile.sort_index(inplace=True,ascending=True)
		
		#Add in empty columns to ensure that the bed file generated is in Bed detail format
		output_reindex = self.bedfile.reindex(columns=['Start', 'Stop', 'EntrezID', '', '', '', '', '', '', '', '', '', 'Gene_Accession'])
		output_reindex.index.name = "#Chr"

		
		#print "this is bedfile", self.bedfile
		#CSV file with column headers
		output_reindex.to_csv(path_or_buf=self.outputfile, sep='\t')
		
		#CSV file without column headers (needs to be in this format in order to get coverage stats from pipeline.THIS IS NOT CORRECT!!!!)
		#YOU CAN INCLUDE HEADERS BUT THE LINE MUST START WITH #
		#bedfile.to_csv(path_or_buf=self.outputfile, header=False, sep='\t')
		
		timestamp = "#" + str(datetime.datetime.now())
		subprocess.call("sed -i '1 i\%s' %s" % (timestamp, self.outputfile), shell=True)
		
		# call function to order the bedfile
		self.order_refseq_file()

		
	def order_refseq_file(self):
		#open self.outputfile
		refseq_file=open(self.outputfile,'r')
		#list for bedfile lines 
		coord_list=[]
		#list for headers
		header=[]
		#loop through the newly created befile
		for line in refseq_file:
			#capture headers
			if line.startswith('#'):
				header.append(line)
			else:
				# for each line of genomic coords split on tab
				splitline=line.split('\t')

				# capture the chromosome and replace the chr if not removed above
				splitline[0]=splitline[0].replace('chr','')

				# if it's not a sex chrom convert to integer to ensure sort works correctly NB sorting will put integers first, then letters
				if splitline[0] not in ('X','Y'):
					splitline[0]=int(splitline[0])
				# covert start and stop to integer
				splitline[1]=int(splitline[1])
				splitline[2]=int(splitline[2])
				#append the whole line to a list
				coord_list.append(splitline)
	
		#sort this list first on stop, then start then chr
		coord_list.sort(key=lambda tup: tup[2])  # sorts on stop
		coord_list.sort(key=lambda tup: tup[1])  # sorts on start
		coord_list.sort(key=lambda tup: tup[0])  # sorts on chr 1 -> 22 then X then Y 
				
		#close file
		refseq_file.close()
		#reopen file but as write (will overwrite the file)
		refseq_file2=open(self.outputfile,'w')
		# write the header
		for line in header:
			refseq_file2.write(line)
		# write the sorted bedfile 
		for line in coord_list:
			#first convert all elements in each line to strings (needed by the join function)
			string_list=[str(element) for element in line]
			#if --minuschr is not given we need to replace the chr which was removed above
			if not self.minuschr:
				string_list[0]='chr'+string_list[0]
			# write the line, joining each element with a tab
			refseq_file2.write("\t".join(string_list))
		
		#close file
		refseq_file2.close()

	def calldb(self, database='hg19'):
		self.g = cruzdb.Genome(db=database)
		self.refGene = self.g.refGene
		return self.g


	def mergeboundaries(self):
		
		#This will mirror the hg19 RefSeq data from UCSC and store it locally at the file location /home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db
		#g = cruzdb.Genome(db="hg19")
		#gs = g.mirror(['refGene'], 'sqlite:////home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db')
		
		#To access the locally stored database invoke the command below
		#g = cruzdb.Genome(db='/home/ryank/LiveReferenceSequencs/Versions/Downloaded160612/160612/refGene.db')
		
		# Query Live RefGene Table on UCSC
		#self.g = cruzdb.Genome(db=database)
		#refGene = g.refGene
		
		#bed = pd.read_table(self.genes, header= 0)
		#The 2 lines below show you how to query the live database at UCSC 
		#g = cruzdb.Genome(db="hg19")
		#refGene = g.refGene
		
		self.calldb()
		#Create instances of the classes holding the tables to be queried (creating instances increases the speed of the script as it doesn't have to keep re-reading the contents of the table in on every loop 
		liveacc = Liveaccversion()
		liveref = LiveRefLink()
		# Synonyms not in refgene file
		synonym=os.path.splitext(self.outputfile)[0] + "_Synonym.txt"
		
		synonym_nocoding=os.path.splitext(self.outputfile)[0] + "_Synonymnocoding.txt"
		
		fr = open(synonym,'w')
		fr.close()
		fc = open(synonym_nocoding, 'w')
		fc.close()
		genepos = self.refGene.filter_by(name2="NOX4MOCK").filter(or_(self.refGene.chrom=='chr1', self.refGene.chrom=='chr2', self.refGene.chrom=='chr3', self.refGene.chrom=='chr4', self.refGene.chrom=='chr5', self.refGene.chrom=='chr6', self.refGene.chrom=='chr7', self.refGene.chrom=='chr8', self.refGene.chrom=='chr9', self.refGene.chrom=='chr10', self.refGene.chrom=='chr11', self.refGene.chrom=='chr12', self.refGene.chrom=='chr13', self.refGene.chrom=='chr14', self.refGene.chrom=='chr15', self.refGene.chrom=='chr16', self.refGene.chrom=='chr17', self.refGene.chrom=='chr18', self.refGene.chrom=='chr19', self.refGene.chrom=='chr20', self.refGene.chrom=='chr21', self.refGene.chrom=='chr22', self.refGene.chrom=='chrX', self.refGene.chrom=='chrY')).all()
		
		self.lastgene = self.bed.iget_value(-1,0)
		#If using pandas 0.10.1 use for loop in line below
		for index, gene in self.bed[self.bed.columns[0:1]].itertuples():
			mergecds = []
			mergeexon = []
			namelist = []
			entrezlist = []
			genepos = []
			posexons=[]
			uniqueentrez = ''
			
		#If using pandas 0.13.1 or greater use for loop in line below
		#for index, gene in bed[[0]].itertuples():
			
			try:
				geneobj = self.refGene.filter_by(name2=gene).filter(or_(self.refGene.chrom=='chr1', self.refGene.chrom=='chr2', self.refGene.chrom=='chr3', self.refGene.chrom=='chr4', self.refGene.chrom=='chr5', self.refGene.chrom=='chr6', self.refGene.chrom=='chr7', self.refGene.chrom=='chr8', self.refGene.chrom=='chr9', self.refGene.chrom=='chr10', self.refGene.chrom=='chr11', self.refGene.chrom=='chr12', self.refGene.chrom=='chr13', self.refGene.chrom=='chr14', self.refGene.chrom=='chr15', self.refGene.chrom=='chr16', self.refGene.chrom=='chr17', self.refGene.chrom=='chr18', self.refGene.chrom=='chr19', self.refGene.chrom=='chr20', self.refGene.chrom=='chr21', self.refGene.chrom=='chr22', self.refGene.chrom=='chrX', self.refGene.chrom=='chrY')).all()
				
			except:
				geneobj = self.refGene.filter_by(name2=gene).filter(or_(self.refGene.chrom=='chrX')).all()
			#exonframes = genepos.exonframes
			

			
			# For each gene append the exon boundaries for each accession entry to the list "coding"
			
			# Generate an output file showing the list of gene symbols not in RefGene
			with open(synonym,'a') as notinrefgene:
				if not geneobj:
					notinrefgene.write(gene + "\n")
			
			#Generate a list of gene objects splitting the object across chromosomes if gene maps to more than one chromosome
			# Create a list of chromosomes for where the gene maps
			chrs = list(set([posexons.chrom for posexons in geneobj]))
			# Generate a set of lists where the index of the dictionary refers to a specific list
			chrlists = {}
			for val in chrs:
				chrlists[val] = []

			# Populate each chromosome specific list with gene objects for that chromosome
			for posexons in geneobj:
				chrlists[posexons.chrom].append(posexons)
			


			#Iterate over each chromosome specific gene object
			self.listgeneposition = []

			for chromoz in chrlists:
				mergecds = []
				mergeexon = []
				namelist = []
				entrezlist = []
				mergecdsboundaries = []
				mergeexonboundaries = []
				for posexons in chrlists[chromoz]:

					if posexons.cds:
						cds = posexons.cds
					mergecds.extend(posexons.cds)
					mergeexon.extend(posexons.exons)
					#print posexons.name.encode('ascii', 'ignore')
					access = posexons.name.encode('ascii', 'ignore')
					#print access
					
					# Generate the version number for each accession number
					version = liveacc.versionfinder(access)
					versionenc = version.encode('ascii', 'ignore')
					namelist.append(versionenc)
				# Generate the entrezid for the gene symbol inserted based on its associated NM accesions
				entrez = liveref.entrezidretrieve(access)
				entrezlist.append(entrez)
				uniqueentrez = len(set(entrezlist))
										
				# If statement indicates if more than one entrez id has been identified for a gene symbol
				# If so a ValueError is raised and a message indicating for which gene symbol this occurred
				if uniqueentrez != 1:
					raise ValueError('uniqueentrez list shows more than one entrez id was retieved for the gene symbol %s' % (gene))
				else:
					# entrezid generated
					entrezid = "".join(str(val) for val in set(entrezlist))
					print entrezid

				with open(synonym_nocoding,'a') as nocoding:
					if not mergecds:
						nocoding.write(gene + "\n")
				
				#Generate output file showing a list of gene symbols which don't have a coding region annoated
				#if not cds:
				#	with open('Synonymsnocodingregions', 'a') as nocodingregions:
				#		nocodingregions.write(gene + "\n")
				cds = []
					
					
				
				# Submit the list "coding as an argument to the function "merge_ranges" which will remove duplicate entries and generate the maximum non-verlapping set of intervals eg ((1,5),(3,7),(4,9)) would be merged into the interval (1,9)
				mergecdsboundaries = [val for val in self.merge_ranges(mergecds)]
				#yield mergecdsboundaries
				mergeexonboundaries = [val for val in self.merge_ranges(mergeexon)]
				#Reset the attributes to the geneposition class
				class atrib():
					pass
				geneposition = atrib()
				setattr(geneposition, "cds", mergecdsboundaries)
				setattr(geneposition, "exons", mergeexonboundaries)
				setattr(geneposition, "name", namelist)
				setattr(geneposition, "name2", posexons.name2.encode('ascii', 'ignore'))
				setattr(geneposition, "chrom", posexons.chrom)
				setattr(geneposition, "strand", posexons.strand)
				setattr(geneposition, "entrezid", entrez)
				
				
				#self.flankingregion(geneposition = geneposition, positionsexons= geneposition.exons, positionscds = geneposition.cds)
				#yield "here",mergecds
				self.listgeneposition.append(geneposition)
			chrlists.clear()
			yield self.listgeneposition

			
	def merge_ranges(self, ranges):
		ranges = iter(sorted(ranges))
		current_start, current_stop = next(ranges)
		#print current_start, current_stop
		for start, stop in ranges:
			if start > current_stop:
			# Gap between segments: output current segment and start a new one.
				yield current_start, current_stop
				current_start, current_stop = start, stop
			else:
				# Segments adjacent or overlapping: merge.
				current_stop = max(current_stop, stop)
		yield current_start, current_stop
	
	def useaccessions(self):
	
		#This will mirror the hg19 RefSeq data from UCSC and store it locally at the file location /home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db
		#g = cruzdb.Genome(db="hg19")
		#gs = g.mirror(['refGene'], 'sqlite:////home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db')
		
		#To access the locally stored database invoke the command below
		#g = cruzdb.Genome(db='hg19')
		#g = cruzdb.Genome(db='/home/ryank/LiveReferenceSequencs/Versions/Downloaded160612/160612/refGene.db')
		#refGene = g.refGene
		
		self.calldb()
		#Create instances of the classes holding the tables to be queried (creating instances increases the speed of the script as it doesn't have to keep re-reading the contents of the table in on every loop 
		liveacc = Liveaccversion()
		liveref = LiveRefLink()
		

		bed = pd.read_table(self.transcripts, header= 0)
		#The 2 lines below show you how to query the live database at UCSC 
		#g = cruzdb.Genome(db="hg19")
		#refGene = g.refGene
		
		#If using pandas 0.10.1 use for loop in line below
		for index, acc, gene in bed[bed.columns[0:2]].itertuples():
		
		#If using pandas 0.13.1 or greater use for loop in line below
		#for index, gene in bed[[0]].itertuples():
		
			try:
				genepos = self.refGene.filter_by(name=acc).filter(or_(self.refGene.chrom=='chr1', self.refGene.chrom=='chr2', self.refGene.chrom=='chr3', self.refGene.chrom=='chr4', self.refGene.chrom=='chr5', self.refGene.chrom=='chr6', self.refGene.chrom=='chr7', self.refGene.chrom=='chr8', self.refGene.chrom=='chr9', self.refGene.chrom=='chr10', self.refGene.chrom=='chr11', self.refGene.chrom=='chr12', self.refGene.chrom=='chr13', self.refGene.chrom=='chr14', self.refGene.chrom=='chr15', self.refGene.chrom=='chr16', self.refGene.chrom=='chr17', self.refGene.chrom=='chr18', self.refGene.chrom=='chr19', self.refGene.chrom=='chr20', self.refGene.chrom=='chr21', self.refGene.chrom=='chr22', self.refGene.chrom=='chrX', self.refGene.chrom=='chrY')).one()
			except:
				genepos = self.refGene.filter_by(name=acc).filter(or_(self.refGene.chrom=='chrX')).one()
			# Set the exon boundaries and assign to variable positionsexons
			posexons=genepos.exons
			# Set the coding exon boundaries and assign to variable positionsexons
			poscds=genepos.cds
			access = genepos.name.encode('ascii', 'ignore')
			
			try:
				version = liveacc.versionfinder(access)
				versionenc = version.encode('ascii', 'ignore')
				
			except ValueError:
				print "The accession %s has no valid version number" % (access)

				
			print versionenc
			print genepos.name2.encode('ascii', 'ignore')
			
			
			# Generate the entrezid for the gene symbol inserted based on its associated NM accesions
			entrez = liveref.entrezidretrieve(access)
			
				
			class atrib():
				pass
			geneposition = atrib()
			setattr(geneposition, "cds", poscds)
			setattr(geneposition, "exons", posexons)
			setattr(geneposition, "name", versionenc)
			setattr(geneposition, "name2", genepos.name2.encode('ascii', 'ignore'))
			setattr(geneposition, "chrom", genepos.chrom)
			setattr(geneposition, "strand", genepos.strand)
			setattr(geneposition, "entrezid", entrez)
			
			
			self.flankingregion(geneposition = geneposition, positionsexons= geneposition.exons, positionscds = geneposition.cds)

	def flankingregion(self, geneposition, positionsexons, positionscds):
		"""
		#This will mirror the hg19 RefSeq data from UCSC and store it locally at the file location /home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db
		#g = cruzdb.Genome(db="hg19")
		#gs = g.mirror(['refGene'], 'sqlite:////home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db')
		
		#To access the locally stored database invoke the command below
		g = cruzdb.Genome(db='/home/ryank/LiveReferenceSequencs/Versions/Downloaded160612/160612/refGene.db')
		refGene = g.refGene
		
		bed = pd.read_table(self.transcripts, header= 0)
		#The 2 lines below show you how to query the live database at UCSC 
		#g = cruzdb.Genome(db="hg19")
		#refGene = g.refGene
		
		#If using pandas 0.10.1 use for loop in line below
		for index, acc, gene in bed[bed.columns[0:2]].itertuples():
		
		#If using pandas 0.13.1 or greater use for loop in line below
		#for index, gene in bed[[0]].itertuples():
		
			try:
				geneposition = refGene.filter_by(name=acc).filter(or_(refGene.chrom=='chr1', refGene.chrom=='chr2', refGene.chrom=='chr3', refGene.chrom=='chr4', refGene.chrom=='chr5', refGene.chrom=='chr6', refGene.chrom=='chr7', refGene.chrom=='chr8', refGene.chrom=='chr9', refGene.chrom=='chr10', refGene.chrom=='chr11', refGene.chrom=='chr12', refGene.chrom=='chr13', refGene.chrom=='chr14', refGene.chrom=='chr15', refGene.chrom=='chr16', refGene.chrom=='chr17', refGene.chrom=='chr18', refGene.chrom=='chr19', refGene.chrom=='chr20', refGene.chrom=='chr21', refGene.chrom=='chr22', refGene.chrom=='chrX', refGene.chrom=='chrY')).one()
			except:
				geneposition = refGene.filter_by(name=acc).filter(or_(refGene.chrom=='chrX')).one()
			# Set the exon boundaries and assign to variable positionsexons
			positionsexons=geneposition.exons
			# Set the coding exon boundaries and assign to variable positionsexons
			positionscds=geneposition.cds
			"""
		#self.upstream adds to the 5'UTR of the first exon
		#self.downstream adds to the 3'UTR of the last exon
		#self.codingup and self.codingdown add to the ends of each internal coding exon
		if self.up == True and self.down == True and self.coding == True and geneposition.strand == "+":
	
						
			#Generate the Chr column			
			for row in positionsexons:
					
				self.Chr.append(geneposition.chrom)
				self.Accession.append(geneposition.name)
				self.GeneName.append(geneposition.name2)
				self.entrezid.append(geneposition.entrezid)
				self.strand.append(geneposition.strand)
				
			#Generate Accession column				
			#for row in positionsexons:
			#	self.Accession.append(geneposition.name)
			
			#Generate GeneName column				
			#for row in positionsexons:
			#	self.GeneName.append(geneposition.name2)
			#Generate the Start and Stop columns
			counter = 0			
			for a, b in positionsexons:
				if counter == 0:
					upstream = long(self.upstream)				
					upstreamUTR = a - upstream				
					
					self.Start.append(upstreamUTR)
					down = long(self.codingdown)
					exons3 = b + down
					
					self.Stop.append(exons3)
					counter += 1
				elif counter > 0 and counter != (len(positionsexons) - 1):
					up = long(self.codingup)
					exons5 = a - up
					self.Start.append(exons5)
					down = long(self.codingdown)
					exons3 = b + down
					self.Stop.append(exons3)
					counter += 1
				
				else:
					up = long(self.codingup)
					exons5 = a - up
					self.Start.append(exons5)
					downstream = long(self.downstream)				
					downstreamUTR = b + downstream				
					self.Stop.append(downstreamUTR)					
				
			
		#For genes on the minus strand
		#self.upstream adds to the 5'UTR of the first exon
		#self.downstream adds to the 3'UTR of the last exon
		#self.codingup and self.codingdown add to the ends of each internal coding exon
		elif self.up == True and self.down == True and self.coding == True and geneposition.strand == "-":
			#Generate the Chr column			
			for row in positionsexons:
				
				self.Chr.append(geneposition.chrom)
				self.Accession.append(geneposition.name)
				self.GeneName.append(geneposition.name2)
				self.entrezid.append(geneposition.entrezid)
				self.strand.append(geneposition.strand)
				
# 			#Generate Accession column				
# 			for row in positionsexons:
# 				self.Accession.append(geneposition.name)
# 			
# 			#Generate GeneName column				
# 			for row in positionsexons:
# 				self.GeneName.append(geneposition.name2)			
			#Generate the Start and Stop columns
			counter = 0			
			for a, b in positionsexons:
				if counter == 0:
					downstream = long(self.downstream)				
					downstreamUTR = a - downstream
					self.Start.append(downstreamUTR)
					up = long(self.codingup)
					exons5 = b + up
					self.Stop.append(exons5)
					counter += 1
				elif counter > 0 and counter != (len(positionsexons) - 1):
					down = long(self.codingdown)
					exons3 = a - down
					self.Start.append(exons3)
					up = long(self.codingup)
					exons5 = b + up
					self.Stop.append(exons5)
					counter += 1
		
				else:
					down = long(self.codingdown)
					exons3 = a - down
					self.Start.append(exons3)
					upstream = long(self.upstream)				
					upstreamUTR = b + upstream
					self.Stop.append(upstreamUTR)
		#self.upstream adds to the 5'UTR of the first exon
		#self.codingup and self.codingdown add to the ends of each internal coding exon
		#self.codingdown adds to the end of the coding region of the last exon			
		elif self.up == True and self.down == False and self.coding == True and geneposition.strand == "+":

						
							
			counter = 0
			for a, b in positionsexons:
				
				print "cds begins"
				
				if counter == 0:
					upstream = long(self.upstream)				
					upstreamUTR = a - upstream
					self.Start.append(upstreamUTR)
					down = long(self.codingdown)
					exons3 = b + down
					self.Stop.append(exons3)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.entrezid.append(geneposition.entrezid)
					self.GeneName.append(geneposition.name2)
					self.strand.append(geneposition.strand)
					
					counter += 1
				elif counter > 0 and b < positionscds[-1][1]:
					up = long(self.codingup)
					exons5 = a - up
					self.Start.append(exons5)
					down = long(self.codingdown)
					exons3 = b + down
					self.Stop.append(exons3)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.entrezid.append(geneposition.entrezid)
					self.GeneName.append(geneposition.name2)
					self.strand.append(geneposition.strand)
					counter += 1
			
				else:
					up = long(self.codingup)
					exons5 = positionscds[-1][0] - up
					self.Start.append(exons5)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)
					#Define flanking region round Stop codon
					if self.StopFlanking == True:
						StopFlank = long(self.StopFlank)
						exons3 = positionscds[-1][1] + StopFlank
						self.Stop.append(exons3)
					else:
						down = long(self.codingdown)
						exons3 = positionscds[-1][1] + down
						self.Stop.append(exons3)
					#break is here to break out of the for loop thus preventing any further non-coding exons to be inputted 
					break
		#self.upstream adds to the 5'UTR of the first exon
		#self.codingup and self.codingdown add to the ends of each internal coding exon
		#self.codingdown adds to the end of the coding region of the last exon	
		elif self.up == True and self.down == False and self.coding == True and geneposition.strand == "-":		
			
			#Generate the Start and Stop columns
			counter = 0
			for a, b in positionsexons:
				
				
				if a < positionscds[0][0]:
					#exons3 = []
					#if not exons3:					
					if b == positionscds[0][1]:		
						if self.StopFlanking == True:
							StopFlank = long(self.StopFlank)
							exons3 = positionscds[0][0] - StopFlank
							self.Start.append(exons3)
						else:
							down = long(self.codingdown)
							exons3 = positionscds[0][0] - down
							self.Start.append(exons3)
						up = long(self.codingup)				
						exons5 = positionscds[0][1] + up
						self.Stop.append(exons5)
						self.Chr.append(geneposition.chrom)
						self.Accession.append(geneposition.name)
						self.GeneName.append(geneposition.name2)
						self.entrezid.append(geneposition.entrezid)
						self.strand.append(geneposition.strand)
						counter += 1
					else:
						counter += 1
				elif a > positionscds[0][0] and counter != (len(positionsexons) - 1):
					down = long(self.codingdown)
					exons3 = a - down
					self.Start.append(exons3)
					up = long(self.codingup)
					exons5 = b + up
					self.Stop.append(exons5)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)
					counter += 1
			
				else:
					down = long(self.codingdown)
					exons3 = a - down
					self.Start.append(exons3)
					upstream = long(self.upstream)				
					upstreamUTR = b + upstream
					self.Stop.append(upstreamUTR)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)
		#self.codingup adds to the 5' end of the first coding exon
		#self.codingup and self.codingdown add to the ends of each internal coding exon
		#self.codingdownstream adds to the end of the 3'UTR of the last exon	
		elif self.up == False and self.down == True and self.coding == True and geneposition.strand == "+":

			
			#Generate the Start and Stop columns
			counter = 0
			for a, b in positionsexons:
				
				if a < positionscds[0][0]:
					#exons3 = []					
					#if not exons3:
					if b == positionscds[0][1]:
						if self.StartFlanking == True:
							StartFlank = long(self.StartFlank)
							exons5 = positionscds[0][0] - StartFlank
							self.Start.append(exons5)			
						else:
							up = long(self.codingup)
							exons5 = positionscds[0][0] - up
							self.Start.append(exons5)
						down = long(self.codingdown)				
						exons3 = positionscds[0][1] + down
						self.Stop.append(exons3)
						self.Chr.append(geneposition.chrom)
						self.Accession.append(geneposition.name)
						self.GeneName.append(geneposition.name2)
						self.entrezid.append(geneposition.entrezid)
						self.strand.append(geneposition.strand)
						counter += 1
					else:
						counter += 1
				elif a > positionscds[0][0] and counter != (len(positionsexons) - 1):
					up = long(self.codingup)
					exons5 = a - up
					self.Start.append(exons5)
					down = long(self.codingdown)
					exons3 = b + down
					self.Stop.append(exons3)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)
					counter += 1
			
				else:
					up = long(self.codingup)
					exons5 = a - up
					self.Start.append(exons5)
					downstream = long(self.downstream)				
					downstreamUTR = b + downstream
					self.Stop.append(downstreamUTR)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)			
		#self.codingup adds to the 5' end of the first coding exon
		#self.codingup and self.codingdown add to the ends of each internal coding exon
		#self.codingdownstream adds to the end of the 3'UTR of the last exon	
		elif self.up == False and self.down == True and self.coding == True and geneposition.strand == "-":

			
			#Generate the Start and Stop columns
			counter = 0
			for a, b in positionsexons:
				
				print "cds begins"
				
				if counter == 0:
					downstream = long(self.downstream)				
					downstreamUTR = a - downstream
					self.Start.append(downstreamUTR)
					up = long(self.codingup)
					exons5 = b + up
					self.Stop.append(exons5)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)
					counter += 1
					
				elif a > positionscds[0][0] and counter != (len(positionsexons) - 1):
					down = long(self.codingdown)
					exons3 = a - down
					self.Start.append(exons3)
					up = long(self.codingup)
					exons5 = b + up
					self.Stop.append(exons5)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)
					counter += 1
			
				else:
					down = long(self.codingdown)
					exons3 = positionscds[-1][0] - down
					self.Start.append(exons3)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
					self.entrezid.append(geneposition.entrezid)
					self.strand.append(geneposition.strand)
					if self.StartFlanking == True:
							StartFlank = long(self.StartFlank)
							exons5 = positionscds[-1][1] + StartFlank
							self.Stop.append(exons5)
					else:
						up = long(self.codingup)
						exons5 = positionscds[-1][1] + up
						self.Stop.append(exons5)
					break
		#self.coding up and self.coding down added to 5' and 3' ends respectively of all coding exons
		elif self.up == False and self.down == False and self.coding == True and geneposition.strand == "+":

			#Generate the Chr column			
			for row in positionscds:
				
				self.Chr.append(geneposition.chrom)
				
				
			#Generate Accession column				
			for row in positionscds:
				self.Accession.append(geneposition.name)
			
			#Generate GeneName column				
			for row in positionscds:
				self.GeneName.append(geneposition.name2)
				
			#Generate entrezid and strand column				
			for row in positionscds:
				self.entrezid.append(geneposition.entrezid)
				self.strand.append(geneposition.strand)
			
			
			
			#Generate the Start and Stop columns
			#itemlist = []
			counter = 0
			for a, b in positionscds:
				#itemlist.append(a)
				#if len(itemlist) == 1:
				if counter == 0:
					if self.StartFlanking == True:
						StartFlank = long(self.StartFlank)
						exons5 = a - StartFlank
						self.Start.append(exons5)
						down = long(self.codingdown)
						exons3 = b + down
						self.Stop.append(exons3)
					else:	
						up = long(self.codingup)				
						exons5 = a - up
						self.Start.append(exons5)
						down = long(self.codingdown)
						exons3 = b + down
						self.Stop.append(exons3)
					counter += 1
				#elif len(itemlist) == (len(positionscds) -1):
				elif a > positionscds[0][0] and counter != (len(positionscds) - 1):
					up = long(self.codingup)				
					exons5 = a - up
					self.Start.append(exons5)
					down = long(self.codingdown)
					exons3 = b + down
					self.Stop.append(exons3)
					counter += 1
				else:
					if self.StopFlanking == True:
						up = long(self.codingup)				
						exons5 = a - up
						self.Start.append(exons5)
						StopFlank = long(self.StopFlank)
						exons3 = b + StopFlank
						self.Stop.append(exons3)
					else:
						up = long(self.codingup)				
						exons5 = a - up
						self.Start.append(exons5)
						down = long(self.codingdown)
						exons3 = b + down
						self.Stop.append(exons3)
		elif self.up == False and self.down == False and self.coding == True and geneposition.strand == "-":
			#Generate the Chr column			
			for row in positionscds:	
				self.Chr.append(geneposition.chrom)
				
				
			#Generate Accession column				
			for row in positionscds:
				self.Accession.append(geneposition.name)
			
			#Generate GeneName column				
			for row in positionscds:
				self.GeneName.append(geneposition.name2)
				
			#Generate entrezid and strand columns				
			for row in positionscds:
				self.entrezid.append(geneposition.entrezid)
				self.strand.append(geneposition.strand)
			
			
			#Generate the Start and Stop columns
			#itemlist = []
			counter = 0
			for a, b in positionscds:
				#itemlist.append(a)
				#if len(itemlist) == 1:
				if counter == 0:
					if self.StopFlanking == True:
						StopFlank = long(self.StopFlank)
						exons3 = a - StopFlank
						self.Start.append(exons3)
						up = long(self.codingup)		
						exons5 = b + up
						self.Stop.append(exons5)
					else:
						down = long(self.codingdown)				
						exons3 = a - down
						self.Start.append(exons3)
						up = long(self.codingup)		
						exons5 = b + up
						self.Stop.append(exons5)
					counter += 1
						
				#elif len(itemlist) == (len(positionscds) -1):
				elif a > positionscds[0][0] and counter != (len(positionscds) - 1):
					down = long(self.codingdown)				
					exons3 = a - down
					self.Start.append(exons3)
					up = long(self.codingup)		
					exons5 = b + up
					self.Stop.append(exons5)
					counter += 1
					
				else:
					if self.StartFlanking == True:
						down = long(self.codingdown)				
						exons3 = a - down
						self.Start.append(exons3)
						StartFlank = long(self.StartFlank)
						exons5 = b + StartFlank
						self.Stop.append(exons5)
					else:
						down = long(self.codingdown)				
						exons3 = a - down
						self.Start.append(exons3)
						up = long(self.codingup)		
						exons5 = b + up
						self.Stop.append(exons5)
					
		else:
			print "You need to provide --coding arguments"

		#print self.Chr
		#print len(self.Start), len(self.Chr)
		# Re-run data through merge_ranges to ensure overlapping regions are merged
		# Run following section if mergeboundaries command is set
		if self.mergeboundariesboolean == True:
			# Set mergestart to the list of start positions defined by self.Start
			mergestart = self.Start
			# Set mergestop to the list of stop positions defined by self.Stop
			mergestop = self.Stop
			# Run following if code to remove previously loaded start positions from self.Start
			if self.prevselfstart and self.prevselfstop:
				for st, sp in zip(self.prevselfstart, self.prevselfstop):
					mergestart.remove(st)
					mergestop.remove(sp)
			#deepcopy ensures that self.prevselfstart and self.prevselfstop lists are not linked to the original lists self.Start and self.Stop
			self.prevselfstart = deepcopy(self.Start)
			self.prevselfstop = deepcopy(self.Stop)
			
			#Run the start positions defined by self.flankingregion through merge_ranges this merges any regions that become overalapping as a result of the extra bases added
			tuplestartstop = zip(mergestart, mergestop)
			mergeboundariespostflankingregion = [val for val in self.merge_ranges(tuplestartstop)]
			startmerge, stopmerge = [a[0] for a in mergeboundariespostflankingregion], [a[1] for a in mergeboundariespostflankingregion]
			self.Startmerge.extend(startmerge)
			self.Stopmerge.extend(stopmerge)
			self.Chrom.extend([geneposition.chrom] * len(mergeboundariespostflankingregion))
			#print len(mergeboundariespostflankingregion)
			self.Acc.extend([geneposition.name] * len(mergeboundariespostflankingregion))
			self.Gene.extend([geneposition.name2] * len(mergeboundariespostflankingregion))
			self.entrezidmerge.extend([geneposition.entrezid] * len(mergeboundariespostflankingregion))
			self.strandmerge.extend([geneposition.strand] * len(mergeboundariespostflankingregion))
			
			
	
		
			
#python Cruzdb.py --coding 10 --transcripts NM_000546 NM_004360 NM_000059 NM_000314 NM_007294 NM_000455
def UTR(argv):
	bedfile = Bedfile()
	log = ''	
#Generates and interprets a list of options which can be passed as arguments to the function UTR
	try:
  		opts, args = getopt.getopt(sys.argv[1:], "h", ["coordinatefile=", "coordup=", "coorddown=", "up=", "down=", "codingup=", "codingdown=", "StartFlank=", "StopFlank=", "logfile=", "outputfile=", "CNVoutput=", "transcripts=", "mergeboundaries", "genes=", "useaccessions", "minuschr"])
	except getopt.GetoptError, err:
		print str(err)
		bedfile.usage()
		sys.exit(2)
	output = None
	verbose = False
	
	
	print opts
	for o, a in opts:

		if o in ("-h", "--help"):
			bedfile.usage()
			sys.exit()
		elif o == "--coordinatefile":
			if a in ("-h", "--help", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --coordinatefile"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.coordinatefile = a
				bedfile.coordinates = True

		elif o == "--coordup":
			if a in ("-h", "--help", "--coordinatefile", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --coordup"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.coordup = a
				bedfile.coordinates = True

		elif o == "--coorddown":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --coordup"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.coorddown = a
				bedfile.coordinates = True


		elif o == "--up":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --up"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.upstream = a
				bedfile.up = True

		elif o == "--down":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --down"
				bedfile.usage()
				sys.exit()
			else:			
				bedfile.downstream = a
				bedfile.down = True
		elif o == "--codingup":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --codingup"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.codingup = a		
				bedfile.coding = True
				
		elif o == "--codingdown":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --codingdown"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.codingdown = a		
				bedfile.coding = True
				
		elif o == "--StartFlank":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --StartFlank"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.StartFlank = a		
				bedfile.StartFlanking = True
				
		elif o == "--StopFlank":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --StartFlank"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.StopFlank = a		
				bedfile.StopFlanking = True
		
		elif o == "--logfile":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --logfile"
				bedfile.usage()
				sys.exit()
			else:
				logfile = a
				log = True		
			
				
		elif o == "--outputfile":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--transcripts", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --outputfile"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.outputfile = a
				bedfile.output = True	
				
		elif o == "--CNVoutput":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--transcripts", "--outputfile", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --CNVoutput"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.CNVoutput = a
				bedfile.CNVoutputboolean = True
						


		elif o == "--transcripts":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes", "--minuschr"):
				print "need to define --transcripts"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.transcripts = a
				bedfile.transcriptlist = True
				
		elif o == "--genes":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--minuschr"):
				print "need to define --genes"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.genes = a
				bedfile.genelist = True
				
		elif o == "--mergeboundaries":
			bedfile.mergeboundariesboolean = True
		
		
		elif o == "--useaccessions":
			
			bedfile.useaccessionslist = True	
			
		elif o == "--minuschr":
			
			bedfile.minuschr = True	
		

		else:
			assert False, "unhandled option"
	if log == True:		
		log = open(logfile, 'w+')
		log.write("Time Stamp:" + str(datetime.datetime.now()) + "\n")
		log.write("Command arguments executed:\n")
		log.write("RefSeq table format version generated as %s" % os.path.splitext(bedfile.outputfile)[0] + "RefSeqFormat.txt\n")
		for item in sys.argv:
			str(item)
			log.write("%s " % item)
		log.write("\n\n Python version: %s" % sys.version)
		log.write("\n\n getopt module file path: %s" % getopt.__file__)
		log.write("\n\n os module file path: %s" % os.__file__)
		log.write("\n\n pd class file path: %s" % pd.__file__)
		log.write("\n\n cruzdb module file path: %s" % cruzdb.__file__)
		if str(bedfile.calldb()) == "Genome('mysql://genome@genome-mysql.cse.ucsc.edu/hg19')":
			log.write("\n\n Querying Live UCSC database: %s and table: %s" % (bedfile.g, bedfile.refGene))
			#sub=subprocess.Popen(['git', 'describe', '--tags'], stdout=subprocess.PIPE)
			##process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
 		##print proc_stdout
 		##proc_stdout = process.communicate()[0].strip()
 	 	sub=subprocess.Popen('cd /home/$USER/mokabed; git describe --tags', stdout=subprocess.PIPE, shell=True)
 	  	gitversion = sub.communicate()[0].strip('\n')
 	   	#gitversion = sub.stdout.read().strip('\n')
 		log.write("\n\n" + "version as defined by git tag = " + gitversion)
			 #from cruzdb import Genome
	else:
		print "WARNING you need to define --logfile"
		bedfile.usage()
		sys.exit()
#Ensure I assign False values to variables up and down if they have not been assigned True in the previous for loop
	if bedfile.down != True:
		bedfile.down = False
	if bedfile.up != True:
		bedfile.up = False
	if bedfile.coding != True:
		bedfile.coding = False
	
#Initiate flankingregion method from class Bedfile		
	bedfile.filereader()
	if bedfile.transcriptlist == True and bedfile.useaccessionslist == True:
		bedfile.useaccessions()
		#bedfile.flankingregion()
	if bedfile.mergeboundariesboolean == True and bedfile.genelist == True:
		for val in (bedfile.mergeboundaries()):
			for v in val:
				bedfile.flankingregion(geneposition=v, positionsexons=v.exons, positionscds=v.cds)
		
	if bedfile.coordinates == True:
		bedfile.coordfile()
	if bedfile.output == True:
		bedfile.writefile()
	else:
		print "You have not supplied a file name to write to using argument --outputfile"
	if bedfile.CNVoutputboolean == True:
		bedfile.bedsplitter()
		
	# Automatically generate refseq format version of bed file
	bedfile.refseqfile()
	# Create sambamba file
	sambamba = Sambamba()
	bedfile.sambambaoutput = os.path.splitext(bedfile.outputfile)[0] + "Sambamba.bed"
	sambamba.create_sambamba_bed(bedfile=bedfile.outputfile, refseqfile=bedfile.refseqoutput, sambambaoutput =bedfile.sambambaoutput)
	


if __name__=="__main__":
	start_time = time.time()
	UTR(sys.argv[1:])
	print("--- %s seconds ---" % (time.time() - start_time))