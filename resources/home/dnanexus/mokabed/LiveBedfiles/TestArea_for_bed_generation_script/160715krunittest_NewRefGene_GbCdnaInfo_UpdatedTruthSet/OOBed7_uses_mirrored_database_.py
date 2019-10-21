#!/usr/bin/python
import sys, getopt, os
import pandas as pd
import cruzdb
from sqlalchemy import or_
from versionnumber import Accversion
import time
from copy import deepcopy
import subprocess

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

#python /home/kevin/Documents/NGS_Pipeline/BedFiles/OOBed5.py --logfile /home/kevin/Documents/NGS_Pipeline/BedFiles/WholeExomeAnalysis/NM_032470PlusMinus5_LogFile.txt --coordinatefile /home/kevin/Documents/NGS_Pipeline/BedFiles/Transcripts/Pantranscriptfiles/NM_032470Coordinates.txt --coordup 5 --coorddown 5 --outputfile /home/kevin/Documents/NGS_Pipeline/BedFiles/NM_032470PlusMinus5BedFile.csv
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
	

	def usage(self):

	    usage = """
	    -h --help                 Prints this
	    -m --name of mokafile  	Moka input file to be cross-referenced
	    -s --name of sangerfile	Sanger input file to be checked against
	    -o --name of outputfile	Output file to be generated
	    Sangercheck will cross-reference variants generated by the Moka Pipeline against Mutation Reports generated by the Clinical Scientist from the NextGene software
	    """
	    print usage
	    
	def filereader(self):
		
		if self.coordinatefile:
			self.bed = pd.read_table(self.coordinatefile, header= 0)
		if self.genes:
			self.bed = pd.read_table(self.genes, header= 0)
		if self.transcripts:
			self.bed = pd.read_table(self.transcripts, header= 0)

	def coordfile(self):
		#Set up bed file using a bed file where the start positions for each exon are base 0
		#Bed files need to contain headers in first row Chr, Start, Stop, Accession, GeneName, and all rows need to contain the same number of tab delimited spaces
		bed = pd.read_table(self.coordinatefile, header= 0)

		startnumber = int(self.coordup)
		endnumber = int(self.coorddown)
		newstart = bed.Start - startnumber
		self.Start.extend(newstart)
		newstop = bed.Stop + endnumber
		self.Stop.extend(newstop)
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
			#print Difference
		#print len(Newstart)
		#print len(Newend)
		#print len(Chromosome)
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
		Chr = pd.Series(self.Chr)		
		Start = pd.Series(self.Start)
		Stop = pd.Series(self.Stop)
		Accession = pd.Series(self.Accession)
		GeneName = pd.Series(self.GeneName)
		#Needed to ammend this script as updated Pandas was printing index number and data type info field as well as the values.
		#To print just the values I need to re-assign the Chr, Start and Stop series to just the values using the .values function
		Chr = Chr.values
		Start = Start.values
		Stop = Stop.values
		self.bedfile = pd.DataFrame(zip(Start, Stop, Accession, GeneName),  columns = ["Start", "Stop", "Accession", "GeneName"], index=[Chr])
		
		#bedfile = pd.DataFrame(zip(Start, Stop, GeneName),  columns = ["Start", "Stop", "GeneName"], index=[Chr])

		#Check if all values in Start column are less than the corresponding values in the Stop column
		counter=0
		for row in Start:
			
			if Start[counter] > Stop[counter]:
				print "Error on line ", counter," Not all Start values are less than corresponding Stop values"
				
			counter += 1
		self.bedfile.index.name = "#Chr"
		#print "this is bedfile", self.bedfile
		#CSV file with column headers
		self.bedfile.to_csv(path_or_buf=self.outputfile, sep='\t')
		
		#CSV file without column headers (needs to be in this format in order to get coverage stats from pipeline.THIS IS NOT CORRECT!!!!)
		#YOU CAN INCLUDE HEADERS BUT THE LINE MUST START WITH #
		#bedfile.to_csv(path_or_buf=self.outputfile, header=False, sep='\t')

	def mergeboundaries(self, database='/home/ryank/GithubRepoLive/mokapipe/LiveBedfiles/Cruzdb/cruzdb_refGene.db', table="refGene"):
		
		#This will mirror the hg19 RefSeq data from UCSC and store it locally at the file location /home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db
		#g = cruzdb.Genome(db="hg19")
		#gs = g.mirror(['refGene'], 'sqlite:////home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db')
		
		#To access the locally stored database invoke the command below
		#g = cruzdb.Genome(db='/home/ryank/GithubRepoLive/mokapipe/LiveBedfiles/Cruzdb/cruzdb_refGene.db')
		if table == "refGene":
			g = cruzdb.Genome(db=database)
			refGene = g.refGene
		else:
			g = cruzdb.Genome(db=database)
			refGene = g.refGeneLookup
		
		#bed = pd.read_table(self.genes, header= 0)
		#The 2 lines below show you how to query the live database at UCSC 
		#g = cruzdb.Genome(db="hg19")
		#refGene = g.refGene
		fr = open('Synonymsnotinrefgene','w')
		fr.close()
		fc = open('Synonymsnocodingregions', 'w')
		fc.close()
		genepos = refGene.filter_by(name2="NOX4MOCK").filter(or_(refGene.chrom=='chr1', refGene.chrom=='chr2', refGene.chrom=='chr3', refGene.chrom=='chr4', refGene.chrom=='chr5', refGene.chrom=='chr6', refGene.chrom=='chr7', refGene.chrom=='chr8', refGene.chrom=='chr9', refGene.chrom=='chr10', refGene.chrom=='chr11', refGene.chrom=='chr12', refGene.chrom=='chr13', refGene.chrom=='chr14', refGene.chrom=='chr15', refGene.chrom=='chr16', refGene.chrom=='chr17', refGene.chrom=='chr18', refGene.chrom=='chr19', refGene.chrom=='chr20', refGene.chrom=='chr21', refGene.chrom=='chr22', refGene.chrom=='chrX', refGene.chrom=='chrY')).all()
		
		self.lastgene = self.bed.iget_value(-1,0)
		#If using pandas 0.10.1 use for loop in line below
		for index, gene in self.bed[self.bed.columns[0:1]].itertuples():
			mergecds = []
			mergeexon = []
			namelist = []
			genepos = []
			posexons=[]
		#If using pandas 0.13.1 or greater use for loop in line below
		#for index, gene in bed[[0]].itertuples():
			
			try:
				genepos = refGene.filter_by(name2=gene).filter(or_(refGene.chrom=='chr1', refGene.chrom=='chr2', refGene.chrom=='chr3', refGene.chrom=='chr4', refGene.chrom=='chr5', refGene.chrom=='chr6', refGene.chrom=='chr7', refGene.chrom=='chr8', refGene.chrom=='chr9', refGene.chrom=='chr10', refGene.chrom=='chr11', refGene.chrom=='chr12', refGene.chrom=='chr13', refGene.chrom=='chr14', refGene.chrom=='chr15', refGene.chrom=='chr16', refGene.chrom=='chr17', refGene.chrom=='chr18', refGene.chrom=='chr19', refGene.chrom=='chr20', refGene.chrom=='chr21', refGene.chrom=='chr22', refGene.chrom=='chrX', refGene.chrom=='chrY')).all()
				
			except:
				genepos = refGene.filter_by(name2=gene).filter(or_(refGene.chrom=='chrX')).all()
			#print genepos
			
			# For each gene append the exon boundaries for each accession entry to the list "coding"
			
			# Generate an output file showing the list of gene symbols not in RefGene
			with open('Synonymsnotinrefgene','a') as notinrefgene:
				if not genepos:
					notinrefgene.write(gene + "\n")
			
			for posexons in genepos:
				if posexons.cds:
					cds = posexons.cds
				mergecds.extend(posexons.cds)
				mergeexon.extend(posexons.exons)
				#print posexons.name.encode('ascii', 'ignore')
				access = posexons.name.encode('ascii', 'ignore')
				#print access
				try:
					version = Accversion().versionfinder(access)
					versionenc = version.encode('ascii', 'ignore')
					namelist.append(versionenc)
				except:
					#print access
					pass

			with open('Synonymsnocodingregions','a') as nocoding:
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
			
			
			#self.flankingregion(geneposition = geneposition, positionsexons= geneposition.exons, positionscds = geneposition.cds)
			#yield "here",mergecds
			yield geneposition
			
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
		g = cruzdb.Genome(db='/home/ryank/GithubRepoLive/mokapipe/LiveBedfiles/Cruzdb/cruzdb_refGene.db')
		#g = cruzdb.Genome(db='/home/ryank/GithubRepoLive/mokapipe/LiveBedfiles/Cruzdb/cruzdb_refGene.db')
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
				genepos = refGene.filter_by(name=acc).filter(or_(refGene.chrom=='chr1', refGene.chrom=='chr2', refGene.chrom=='chr3', refGene.chrom=='chr4', refGene.chrom=='chr5', refGene.chrom=='chr6', refGene.chrom=='chr7', refGene.chrom=='chr8', refGene.chrom=='chr9', refGene.chrom=='chr10', refGene.chrom=='chr11', refGene.chrom=='chr12', refGene.chrom=='chr13', refGene.chrom=='chr14', refGene.chrom=='chr15', refGene.chrom=='chr16', refGene.chrom=='chr17', refGene.chrom=='chr18', refGene.chrom=='chr19', refGene.chrom=='chr20', refGene.chrom=='chr21', refGene.chrom=='chr22', refGene.chrom=='chrX', refGene.chrom=='chrY')).one()
			except:
				genepos = refGene.filter_by(name=acc).filter(or_(refGene.chrom=='chrX')).one()
			# Set the exon boundaries and assign to variable positionsexons
			posexons=genepos.exons
			# Set the coding exon boundaries and assign to variable positionsexons
			poscds=genepos.cds
			access = genepos.name.encode('ascii', 'ignore')

			try:
				version = Accversion().versionfinder(access)
				versionenc = version.encode('ascii', 'ignore')
				#namelist.append(versionenc)
			except ValueError:
				print "The accession access has no valid version number"
				
			print versionenc
			print genepos.name2.encode('ascii', 'ignore')
			class atrib():
				pass
			geneposition = atrib()
			setattr(geneposition, "cds", poscds)
			setattr(geneposition, "exons", posexons)
			setattr(geneposition, "name", versionenc)
			setattr(geneposition, "name2", genepos.name2.encode('ascii', 'ignore'))
			setattr(geneposition, "chrom", genepos.chrom)
			setattr(geneposition, "strand", genepos.strand)
			
			self.flankingregion(geneposition = geneposition, positionsexons= geneposition.exons, positionscds = geneposition.cds)


	def flankingregion(self, geneposition, positionsexons, positionscds):
		"""
		#This will mirror the hg19 RefSeq data from UCSC and store it locally at the file location /home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db
		#g = cruzdb.Genome(db="hg19")
		#gs = g.mirror(['refGene'], 'sqlite:////home/kevin/Documents/NGS_Pipeline/BedFiles/cruzdb_refGene.db')
		
		#To access the locally stored database invoke the command below
		g = cruzdb.Genome(db='/home/ryank/GithubRepoLive/mokapipe/LiveBedfiles/Cruzdb/cruzdb_refGene.db')
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
					self.GeneName.append(geneposition.name2)
					
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
					self.GeneName.append(geneposition.name2)
					counter += 1
			
				else:
					up = long(self.codingup)
					exons5 = positionscds[-1][0] - up
					self.Start.append(exons5)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
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
			print "correct channel1"
						
			
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
		#self.codingup adds to the 5' end of the first coding exon
		#self.codingup and self.codingdown add to the ends of each internal coding exon
		#self.codingdownstream adds to the end of the 3'UTR of the last exon	
		elif self.up == False and self.down == True and self.coding == True and geneposition.strand == "+":
			print "correct channel2"
						
			
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
					counter += 1
			
				else:
					down = long(self.codingdown)
					exons3 = positionscds[-1][0] - down
					self.Start.append(exons3)
					self.Chr.append(geneposition.chrom)
					self.Accession.append(geneposition.name)
					self.GeneName.append(geneposition.name2)
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
			self.Acc.extend([geneposition.name] * len(mergeboundariespostflankingregion))
			self.Gene.extend([geneposition.name2] * len(mergeboundariespostflankingregion))
			
			# Once the final gene has been processed then re-define the lists to be outputted to the final bed file
			if geneposition.name2 == self.lastgene:
				self.Start = self.Startmerge
				self.Stop = self.Stopmerge
				self.Chr = self.Chrom
				self.Accession = self.Acc
				self.GeneName = self.Gene
		
		
			
#python Cruzdb.py --coding 10 --transcripts NM_000546 NM_004360 NM_000059 NM_000314 NM_007294 NM_000455
def UTR(argv):
	bedfile = Bedfile()
	log = ''	
#Generates and interprets a list of options which can be passed as arguments to the function UTR
	try:
      		opts, args = getopt.getopt(sys.argv[1:], "h", ["coordinatefile=", "coordup=", "coorddown=", "up=", "down=", "codingup=", "codingdown=", "StartFlank=", "StopFlank=", "logfile=", "outputfile=", "CNVoutput=", "transcripts=", "mergeboundaries", "genes=", "useaccessions"])
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
			if a in ("-h", "--help", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --coordinatefile"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.coordinatefile = a
				bedfile.coordinates = True

		elif o == "--coordup":
			if a in ("-h", "--help", "--coordinatefile", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --coordup"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.coordup = a
				bedfile.coordinates = True

		elif o == "--coorddown":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --coordup"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.coorddown = a
				bedfile.coordinates = True


		elif o == "--up":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --up"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.upstream = a
				bedfile.up = True

		elif o == "--down":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --down"
				bedfile.usage()
				sys.exit()
			else:			
				bedfile.downstream = a
				bedfile.down = True
		elif o == "--codingup":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingdown", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --codingup"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.codingup = a		
				bedfile.coding = True
				
		elif o == "--codingdown":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--StartFlank", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --codingdown"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.codingdown = a		
				bedfile.coding = True
				
		elif o == "--StartFlank":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StopFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --StartFlank"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.StartFlank = a		
				bedfile.StartFlanking = True
				
		elif o == "--StopFlank":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --StartFlank"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.StopFlank = a		
				bedfile.StopFlanking = True
		
		elif o == "--logfile":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--StopFlank", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --logfile"
				bedfile.usage()
				sys.exit()
			else:
				logfile = a
				log = True		
			
				
		elif o == "--outputfile":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--transcripts", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --outputfile"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.outputfile = a
				bedfile.output = True	
				
		elif o == "--CNVoutput":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--transcripts", "--outputfile", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --CNVoutput"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.CNVoutput = a
				bedfile.CNVoutputboolean = True
						


		elif o == "--transcripts":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions", "--genes"):
				print "need to define --transcripts"
				bedfile.usage()
				sys.exit()
			else:
				bedfile.transcripts = a
				bedfile.transcriptlist = True
				
		elif o == "--genes":
			if a in ("-h", "--help", "--coordinatefile", "--coordup", "--coorddown", "--up", "--down", "--codingup", "--codingdown", "--StartFlank", "--logfile", "--StopFlank", "--transcripts", "--outputfile", "--CNVoutput", "--mergeboundaries", "--useaccessions"):
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
		

		else:
			assert False, "unhandled option"
	if log == True:		
		log = open(logfile, 'w+')
		log.write("Command arguments executed:\n")
		for item in sys.argv:
			str(item)
			log.write("%s " % item)
		log.write("\n\n Python version: %s" % sys.version)
		log.write("\n\n getopt module file path: %s" % getopt.__file__)
		log.write("\n\n os module file path: %s" % os.__file__)
		log.write("\n\n pd class file path: %s" % pd.__file__)
		log.write("\n\n cruzdb module file path: %s" % cruzdb.__file__)
		sub=subprocess.Popen(['git', 'describe', '--tags'], stdout=subprocess.PIPE)
		gitversion = sub.stdout.read().strip('\n')
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
		for val in bedfile.mergeboundaries():
			bedfile.flankingregion(geneposition = val, positionsexons= val.exons, positionscds = val.cds)
		
	if bedfile.coordinates == True:
		bedfile.coordfile()
	if bedfile.output == True:
		bedfile.writefile()
	else:
		print "You have not supplied a file name to write to using argument --outputfile"
	if bedfile.CNVoutputboolean == True:
		bedfile.bedsplitter()
	


if __name__=="__main__":
	start_time = time.time()
	UTR(sys.argv[1:])
	print("--- %s seconds ---" % (time.time() - start_time))
