#!/usr/bin/python
import sys, getopt, os
import pandas as pd

#Need to module load python/2.7
#python CNVbedSizeAnalysis1.py '/home/ryank/Databases/BRCAdata.bed' "/home/ryank/Databases/CNVbedfiles/BRCACNVdata.bed"
#python CNVbedSizeAnalysis1.py '/home/ryank/Databases/BRCA_NGS_CNV_exons_plus_40bpJoCbed.txt' "/home/ryank/Databases/CNVbedfiles/BRCACNVJoCdata.bed"
#python CNVbedSizeAnalysis1.py '/home/ryank/Databases/Alportdata.bed' "/home/ryank/Databases/CNVbedfiles/AlportCNVdata.bed"
#python CNVbedSizeAnalysis1.py '/home/ryank/Databases/CNVbedfiles/OldCM_CNV_pre_processedBedFile.bed' "/home/ryank/Databases/CNVbedfiles/OldCMCNVdata.bed"


print sys.argv[1]

def bedsplitter():
	bed = pd.read_table(sys.argv[1], header= 0)
	print bed
	Delta = []
	Newstart = []
	Newend = []
	Chromosome = []
	Name = []
	Start = bed.Start
	Stop = bed.Stop
	print Stop
	
	counter = 0
	for row in Start:
		#Difference = (bed.Stop[counter] -bed.Start[counter])/50
		#Difference = str(Difference).split('.')
		#Delta.append(Difference[0])
		Newstart.append(bed.Start[counter])
		Chromosome.append(bed['#Chr'][counter])
		Name.append(bed.GeneName[counter])
		while (row + 50 < bed.Stop[counter]) and (bed.Stop[counter] -row > 75):
			row = row + 50
			Newend.append(row)
			row += 1
			Newstart.append(row)
			Chromosome.append(bed['#Chr'][counter])
			Name.append(bed.GeneName[counter])
		Newend.append(bed.Stop[counter]) 
		
		
		counter += 1
		#print Difference
	print len(Newstart)
	print len(Newend)
	print len(Chromosome)
	Chromosome = pd.Series(Chromosome)
	Newstart = pd.Series(Newstart)
	Newend = pd.Series(Newend)
	Name = pd.Series(Name)
	#Reminder you need to call the values function 
	Chromosome = Chromosome.values
	Newstart = Newstart.values
	Newend = Newend.values
	Name = Name.values
	outputfile = pd.DataFrame(zip(Newstart, Newend, Name),  columns = ["Start", "Stop", "Names"], index=[Chromosome])
	outputfile.index.name = "Chr"
	outputfile.to_csv(path_or_buf=sys.argv[2], sep='\t')


bedsplitter()
	


