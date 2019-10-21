'''
Created on 30 Dec 2015

@author: kevin
'''
import unittest
import pandas as pd
import re
import cruzdb
#from OOBed7_uses_mirrored_database_ import Bedfile
import subprocess
import sys, getopt
from _ast import Lambda
import os, shutil
#from mock import patch

### Command to run test
### --newscript <new version of bedfile script> --livescript <current live version of script>
### Example:
### python unittest_OOBed7_uses_mirrored_database_.py --newscript OOBed7_uses_mirrored_database_new.py --livescript OOBed7_uses_mirrored_database_.py

"""
# read in the UCSC database
g = cruzdb.Genome(db='/home/kevin/Documents/PythonDocs/UnittestOOBed7_uses_mirrored_database/cruzdbrefGene.db')
# Select the refGene table
refGene = g.refGene
# Assign the class Befile from OOBed7_uses_mirrored_database_
bedfile= Bedfile()
# Assign the lists of transcripts to read in
bedfile.transcripts="/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthset.txt"
# Run filereader function to assign the transcript list to self.bed variable
bedfile.filereader()
bedfile.codingup = 30
bedfile.codingdown = 20
bedfile.coding=True
bedfile.up=False
bedfile.down=False




# Repalce the accessuion number with the accession number containing the .version number
bedfile.useaccessions()
#print bedfile.geneposition.strand
Chr = [val.encode('ascii', 'ignore') for val in bedfile.Chr]
print Chr
Start = [str(val) for val in bedfile.Start]
print Start
Stop = [str(val) for val in  bedfile.Stop]
print Stop

truebed = pd.read_table("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71data_truthset.bed", header=0)
print list(truebed['#Chr'])
print list(truebed.Start)
print list(truebed.Stop)
"""

# --newscript  OOBed7_uses_mirrored_database_resave.py --livescript OOBed7_uses_mirrored_database_old.py


class Runscripts(object):
    def __init__(self):
        self.newscript = ''
        self.livescript = ''
        self.output = ''
         
    def subprocessscripts(self):
    
    	#Add trailing backslash to output folder if one not added
    	self.output=os.path.join(self.output, '')
    	# Make output folder
    	os.makedirs(os.path.dirname(self.output))
    	
    
        # Run python script on test data for coding data - Accessions
        subprocess.call("python %s --codingup 30 --codingdown 20 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthset.txt --logfile %s/Pan71test_new_Logfile.txt --useaccessions --outputfile %s/newoutput.bed" % (self.newscript, self.output, self.output), shell=True)
        subprocess.call("python %s --codingup 30 --codingdown 20 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthset.txt --logfile %s/Pan71test_live_Logfile.txt --useaccessions --outputfile %s/liveoutput.bed" % (self.livescript, self.output, self.output), shell=True)
        
        # Run python script on test data for whole exon regions - Accessions
        subprocess.call("python %s --up 15 --codingup 0 --down 10 --codingdown 0 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthsubset.txt --logfile %s/Pan71testexon_new_Logfile.txt --useaccessions --outputfile %s/newoutputexon.bed" % (self.newscript, self.output, self.output), shell=True)
        subprocess.call("python %s --up 15 --codingup 0 --down 10 --codingdown 0 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthsubset.txt --logfile %s/Pan71testexon_live_Logfile.txt --useaccessions --outputfile %s/liveoutputexon.bed" % (self.livescript, self.output, self.output), shell=True)
        
        # Run python script on test data for coding regions where 5' and 3' coding regions receive different flanking value to internal coding regions - Accessions
        subprocess.call("python %s --StartFlank 50 --codingup 0 --StopFlank 100 --codingdown 0 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthsubset.txt --logfile %s/Pan71testUTR_new_Logfile.txt --useaccessions --outputfile %s/newoutputUTR.bed" % (self.newscript, self.output, self.output), shell=True)
        subprocess.call("python %s --StartFlank 50 --codingup 0 --StopFlank 100 --codingdown 0 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthsubset.txt --logfile %s/Pan71testUTR_live_Logfile.txt --useaccessions --outputfile %s/liveoutputUTR.bed" % (self.livescript, self.output, self.output), shell=True)
        
        # Run python script on test data for coding regions - Gene symbol list
        subprocess.call("python %s --codingup 30 --codingdown 20 --genes /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan81_subset_20genesymbols.txt --logfile %s/Pan81_subset_20genesymbols_codingexons_new_Logfile.txt --mergeboundaries --outputfile %s/Pan81_subset_20genesymbols_codingexons_new.bed"  % (self.newscript, self.output, self.output), shell=True)
        subprocess.call("python %s --codingup 30 --codingdown 20 --genes /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan81_subset_20genesymbols.txt --logfile %s/Pan81_subset_20genesymbols_codingexons_live_Logfile.txt --mergeboundaries --outputfile %s/Pan81_subset_20genesymbols_codingexons_live.bed" % (self.livescript, self.output, self.output), shell=True)
        
		# Run python script on test data for whole exon regions - Gene symbol list
        subprocess.call("python %s --up 30 --down 20 --codingup 30 --codingdown 20 --genes /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan81_subset_20genesymbols.txt --logfile %s/Pan81_subset_20genesymbols_wholeexon_new_Logfile.txt --mergeboundaries --outputfile %s/Pan81_subset_20genesymbols_wholeexon_new.bed" % (self.newscript, self.output, self.output), shell=True)
        subprocess.call("python %s --up 30 --down 20 --codingup 30 --codingdown 20 --genes /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan81_subset_20genesymbols.txt --logfile %s/Pan81_subset_20genesymbols_wholeexon_live_Logfile.txt --mergeboundaries --outputfile %s/Pan81_subset_20genesymbols_wholeexon_live.bed" % (self.livescript, self.output, self.output), shell=True)

        #Copy across the scripts being tested to output folder
        shutil.copy2(self.livescript, self.output)
        shutil.copy2(self.newscript, self.output)
        #Copy across the truth set for testing coding exon boundaries from a list of accessions
        shutil.copy2('/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCtruthsetmanual.bed', self.output)
        #Copy across the truth set for testing whole exon boundaries from a list of accessions
        shutil.copy2('/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCexons_manual.bed', self.output)
        #Copy across the truth set for translational start/end exon boundaries from a list of accessions
        shutil.copy2("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSC_UTR_manual.bed", self.output)
        #Copy across the truth set for testing coding exon boundaries from a list of genes
        shutil.copy2("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCgenesymbols_coding_manual.bed", self.output)
        #Copy across the truth set for testing whole exon boundaries from a list of genes
        shutil.copy2("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCgenesymbols_exons_manual.bed", self.output)
        
        #Delete new test file
        os.remove(self.newscript)
        

        
        
        
#subprocess.Popen("python %s --codingup 30 --codingdown 20 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthset.txt --logfile /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71test2_Logfile.txt --useaccessions --outputfile /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71test2.bed" % sys.argv[1], shell=True)
    def usage(self):
 
        usage = """
        -h --help                 Prints this
        --newscript name of new script to be tested
        --livescript name of livescript to be checked against
        """
        print usage
        
 
class Test(unittest.TestCase):
    
    	
    def setUp(self):

        self.output = "/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/160715krunittest_NewRefGene_GbCdnaInfo_UpdatedTruthSet/"
#         # read in the UCSC database
#         g = cruzdb.Genome(db='/home/kevin/Documents/PythonDocs/UnittestOOBed7_uses_mirrored_database/cruzdbrefGene.db')
#         # Select the refGene table
#         refGene = g.refGene
#         # Assign the class Befile from OOBed7_uses_mirrored_database_
#         bedfile= Bedfile()
#         # Assign the lists of transcripts to read in
#         bedfile.transcripts="/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthset.txt"
#         # Run filereader function to assign the transcript list to self.bed variable
#         bedfile.filereader()
#         bedfile.codingup = 30
#         bedfile.codingdown = 20
#         bedfile.coding=True
#         bedfile.up=False
#         bedfile.down=False
#         # Repalce the accessuion number with the accession number containing the .version number
#         bedfile.useaccessions()
#          
#         self.testChr = [val.encode('ascii', 'ignore') for val in bedfile.Chr]
#         self.testStart = [str(val) for val in bedfile.Start]
#         self.testStop = [str(val) for val in  bedfile.Stop]
        self.ucsctruth = pd.read_table("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCtruthsetmanual.bed", header=0)
        self.ucsctruthchr = list(self.ucsctruth['#Chr'])
        self.ucsctruthstart = list(self.ucsctruth.Start)
        self.ucsctruthstop = list(self.ucsctruth.Stop)
        
        self.ucscexontruth = pd.read_table("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCexons_manual.bed", header=0)
        self.ucscexontruthchr = list(self.ucscexontruth['#Chr'])
        self.ucscexontruthstart = list(self.ucscexontruth.Start)
        self.ucscexontruthstop = list(self.ucscexontruth.Stop)
        
        self.ucscutrtruth = pd.read_table("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSC_UTR_manual.bed", header=0)
        self.ucscutrtruthchr = list(self.ucscutrtruth['#Chr'])
        self.ucscutrtruthstart = list(self.ucscutrtruth.Start)
        self.ucscutrtruthstop = list(self.ucscutrtruth.Stop)
        
        
        

        self.ucsctruthgscoding = pd.read_table("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCgenesymbols_coding_manual.bed", header=0)
        self.ucsctruthgscoding = self.ucsctruthgscoding.sort(["#Chr", "Start", "Stop"], ascending = [1, 1, 1])
        self.ucsctruthgscodingchr = list(self.ucsctruthgscoding['#Chr'])
        self.ucsctruthgscodingstart = list(self.ucsctruthgscoding.Start)
        self.ucsctruthgscodingstop = list(self.ucsctruthgscoding.Stop)
        
        self.ucsctruthgswholeexon = pd.read_table("/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/UCSCgenesymbols_exons_manual.bed", header=0)
        self.ucsctruthgswholeexon = self.ucsctruthgswholeexon.sort(["#Chr", "Start", "Stop"], ascending = [1, 1, 1])
        self.ucsctruthgswholeexonchr = list(self.ucsctruthgswholeexon['#Chr'])
        self.ucsctruthgswholeexonstart = list(self.ucsctruthgswholeexon.Start)
        self.ucsctruthgswholeexonstop = list(self.ucsctruthgswholeexon.Stop)
        
        
        newbedinput = self.output + "newoutput.bed"
         
        self.newbed = pd.read_table(newbedinput, header=0)
        self.newbedchr = list(self.newbed['#Chr'])
        self.newbedstart = list(self.newbed.Start)
        self.newbedstop = list(self.newbed.Stop)
        
        oldbedinput = self.output + "liveoutput.bed"
         
        self.oldbed = pd.read_table(oldbedinput, header=0)
        self.oldbedchr = list(self.oldbed['#Chr'])
        self.oldbedstart = list(self.oldbed.Start)
        self.oldbedstop = list(self.oldbed.Stop)
        
        newbedexoninput = self.output + "newoutputexon.bed"
        
        self.newbedexon = pd.read_table(newbedexoninput, header=0)
        self.newbedexonchr = list(self.newbedexon['#Chr'])
        self.newbedexonstart = list(self.newbedexon.Start)
        self.newbedexonstop = list(self.newbedexon.Stop)
        
        oldbedexoninput = self.output + "liveoutputexon.bed"
         
        self.oldbedexon = pd.read_table(oldbedexoninput, header=0)
        self.oldbedexonchr = list(self.oldbedexon['#Chr'])
        self.oldbedexonstart = list(self.oldbedexon.Start)
        self.oldbedexonstop = list(self.oldbedexon.Stop)
        
        newbedutrinput = self.output + "newoutputUTR.bed"
        
        self.newbedutr = pd.read_table(newbedutrinput, header=0)
        self.newbedutrchr = list(self.newbedutr['#Chr'])
        self.newbedutrstart = list(self.newbedutr.Start)
        self.newbedutrstop = list(self.newbedutr.Stop)
        
        oldbedutrinput = self.output + "liveoutputUTR.bed"
         
        self.oldbedutr = pd.read_table(oldbedutrinput, header=0)
        self.oldbedutrchr = list(self.oldbedutr['#Chr'])
        self.oldbedutrstart = list(self.oldbedutr.Start)
        self.oldbedutrstop = list(self.oldbedutr.Stop)
        
        newbedgscodinginput = self.output + "Pan81_subset_20genesymbols_codingexons_new.bed"
        
        self.newbedgscoding = pd.read_table(newbedgscodinginput, header=0)
        self.newbedgscoding = self.newbedgscoding.sort(["#Chr", "Start", "Stop"], ascending = [1, 1, 1])
        self.newbedgscodingchr = list(self.newbedgscoding['#Chr'])
        self.newbedgscodingstart = list(self.newbedgscoding.Start)
        self.newbedgscodingstop = list(self.newbedgscoding.Stop)
        
        oldbedgscodinginput = self.output + "Pan81_subset_20genesymbols_codingexons_live.bed"
         
        self.oldbedgscoding = pd.read_table(oldbedgscodinginput, header=0)
        self.oldbedgscoding = self.oldbedgscoding.sort(["#Chr", "Start", "Stop"], ascending = [1, 1, 1])
        self.oldbedgscodingchr = list(self.oldbedgscoding['#Chr'])
        self.oldbedgscodingstart = list(self.oldbedgscoding.Start)
        self.oldbedgscodingstop = list(self.oldbedgscoding.Stop)
        
        newbedgswholeexoninput = self.output + "Pan81_subset_20genesymbols_wholeexon_new.bed"
        
        self.newbedgswholeexon = pd.read_table(newbedgswholeexoninput, header=0)
        self.newbedgswholeexon = self.newbedgswholeexon.sort(["#Chr", "Start", "Stop"], ascending = [1, 1, 1])
        self.newbedgswholeexonchr = list(self.newbedgswholeexon['#Chr'])
        self.newbedgswholeexonstart = list(self.newbedgswholeexon.Start)
        self.newbedgswholeexonstop = list(self.newbedgswholeexon.Stop)
        
        self.oldbedgswholeexoninput = self.output + "Pan81_subset_20genesymbols_wholeexon_live.bed"
         
        self.oldbedgswholeexon = pd.read_table(self.oldbedgswholeexoninput, header=0)
        self.oldbedgswholeexon = self.oldbedgswholeexon.sort(["#Chr", "Start", "Stop"], ascending = [1, 1, 1])
        self.oldbedgswholeexonchr = list(self.oldbedgswholeexon['#Chr'])
        self.oldbedgswholeexonstart = list(self.oldbedgswholeexon.Start)
        self.oldbedgswholeexonstop = list(self.oldbedgswholeexon.Stop)

        
 
    def tearDown(self):
        del self.newbedstart
        del self.oldbedstart

        
    def test_1_chr_truth(self):
        print 'In ucsc_chr column --coding arguments test compare old version with truth set'
        self.assertEqual(self.oldbedchr, self.ucsctruthchr, "Failed test - Chr sites not the same as ucsc truth set")
    
    def test_2_chr_truth(self):
        print 'In ucsc_chr column --coding arguments test compare new version with truth set'
        self.assertEqual(self.newbedchr, self.ucsctruthchr, "Failed test - Chr sites not the same as ucsc truth set")
        
    def test_3_chr_truth(self):
        print 'In ucsc_exonic chr column --up/down arguments test compare old version with truth set'
        self.assertEqual(self.oldbedexonchr, self.ucscexontruthchr, "Failed test - Chr sites not the same as ucsc truth set")
    
    def test_4_chr_truth(self):
        print 'In ucsc_exonic chr column --up/down arguments test compare new version with truth set'
        self.assertEqual(self.newbedexonchr, self.ucscexontruthchr, "Failed test - Chr sites not the same as ucsc truth set")
        
    def test_5_chr_truth(self):
        print 'In ucsc_utr chr column --Start/Stop arguments test compare old version with truth set'
        self.assertEqual(self.oldbedutrchr, self.ucscutrtruthchr, "Failed test - Chr sites not the same as ucsc truth set")
    
    def test_6_chr_truth(self):
        print 'In ucsc_utr chr column --Start/Stop arguments test compare new version with truth set'
        self.assertEqual(self.newbedutrchr, self.ucscutrtruthchr, "Failed test - Chr sites not the same as ucsc truth set")
        
    def test_7_start(self):
        print 'In test_start column --coding arguments test compare old version with truth set'
        self.assertEqual(self.oldbedstart, self.ucsctruthstart, "Failed test - Start sites not the same as ucsc truth set")
        
    def test_8_start(self):
        print 'In test_start column --coding arguments test compare new version with truth set'
        self.assertEqual(self.newbedstart, self.ucsctruthstart, "Failed test - Start sites not the same as ucsc truth set")
        
    def test_9_start(self):
        print 'In ucsc_exonic start column --up/down arguments test compare old version with truth set'
        self.assertEqual(self.oldbedexonstart, self.ucscexontruthstart, "Failed test - Start sites not the same as ucsc truth set")
    
    def test_10_start(self):
        print 'In ucsc_exonic start column --up/down arguments test compare new version with truth set'
        self.assertEqual(self.newbedexonstart, self.ucscexontruthstart, "Failed test - Start sites not the same as ucsc truth set")
        
    def test_11_start(self):
        print 'In ucsc_utr start column --Start/Stop arguments test compare old version with truth set'
        self.assertEqual(self.oldbedutrstart, self.ucscutrtruthstart, "Failed test - Start sites not the same as ucsc truth set")
    
    def test_12_start(self):
        print 'In ucsc_utr start column --Start/Stop arguments test compare new version with truth set'
        self.assertEqual(self.newbedutrstart, self.ucscutrtruthstart, "Failed test - Start sites not the same as ucsc truth set")
        
    def test_13_stop(self):
        print 'In test_stop column --coding arguments test compare old version with truth set'
        self.assertEqual(self.oldbedstop, self.ucsctruthstop, "Failed test - Stop sites not the same as ucsc truth set")
        
    def test_14_stop(self):
        print 'In test_stop column --coding arguments test compare new version with truth set'
        self.assertEqual(self.newbedstop, self.ucsctruthstop, "Failed test - Stop sites not the same as ucsc truth set")
        
    def test_15_stop(self):
        print 'In ucsc_exonic stop column --up/down arguments test compare old version with truth set'
        self.assertEqual(self.oldbedexonstop, self.ucscexontruthstop, "Failed test - Stop sites not the same as ucsc truth set")
    
    def test_16_stop(self):
        print 'In ucsc_exonic stop column --up/down arguments test compare new version with truth set'
        self.assertEqual(self.newbedexonstop, self.ucscexontruthstop, "Failed test - Stop sites not the same as ucsc truth set")
        
    def test_17_stop(self):
        print 'In ucsc_utr stop column --Start/Stop arguments test compare old version with truth set'
        self.assertEqual(self.oldbedutrstop, self.ucscutrtruthstop, "Failed test - Stop sites not the same as ucsc truth set")
    
    def test_18_stop(self):
        print 'In ucsc_utr stop column --Start/Stop arguments test compare new version with truth set'
        self.assertEqual(self.newbedutrstop, self.ucscutrtruthstop, "Failed test - Stop sites not the same as ucsc truth set")
    
    def test_19_stop(self):
        print 'In ucsc_gscoding chr column --coding arguments test compare new version with truth set'
        self.assertEqual(self.newbedgscodingchr, self.ucsctruthgscodingchr, "Failed test - Chr sites not the same as ucsc truth set")    
    
    def test_20_stop(self):
        print 'In ucsc_gscoding start column --coding arguments test compare new version with truth set'
        self.assertEqual(self.newbedgscodingstart, self.ucsctruthgscodingstart, "Failed test - Start sites not the same as ucsc truth set")    
    
    def test_21_stop(self):
        print 'In ucsc_gscoding stop column --coding arguments test compare new version with truth set'
        self.assertEqual(self.newbedgscodingstop, self.ucsctruthgscodingstop, "Failed test - Stop sites not the same as ucsc truth set")
        
    def test_22_stop(self):
        print 'In ucsc_gswholeexon chr column --up/down arguments test compare new version with truth set'
        self.assertEqual(self.newbedgswholeexonchr, self.ucsctruthgswholeexonchr, "Failed test - Chr sites not the same as ucsc truth set")    
    
    def test_23_stop(self):
        print 'In ucsc_gswholeexon start column --up/down arguments test compare new version with truth set'
        self.assertEqual(self.newbedgswholeexonstart, self.ucsctruthgswholeexonstart, "Failed test - Start sites not the same as ucsc truth set")    
    
    def test_24_stop(self):
        print 'In ucsc_gswholeexon stop column --up/down arguments test compare new version with truth set'
        self.assertEqual(self.newbedgswholeexonstop, self.ucsctruthgswholeexonstop, "Failed test - Stop sites not the same as ucsc truth set")
        
    def test_25_stop(self):
       print 'In ucsc_gswholeexon chr column --coding arguments test compare old version with truth set'
       self.assertEqual(self.oldbedgscodingchr, self.ucsctruthgscodingchr, "Failed test - Chr sites not the same as ucsc truth set")       
    
    def test_26_stop(self):
        print 'In ucsc_gscoding start column --coding arguments test compare old version with truth set'
        self.assertEqual(self.oldbedgscodingstart, self.ucsctruthgscodingstart, "Failed test - Start sites not the same as ucsc truth set")    
    
    def test_27_stop(self):
        print 'In ucsc_gscoding stop column --coding arguments test compare old version with truth set'
        self.assertEqual(self.oldbedgscodingstop, self.ucsctruthgscodingstop, "Failed test - Stop sites not the same as ucsc truth set")
        
    def test_28_stop(self):
        print 'In ucsc_gswholeexon chr column --up/down arguments test compare old version with truth set'
        self.assertEqual(self.oldbedgswholeexonchr, self.ucsctruthgswholeexonchr, "Failed test - Chr sites not the same as ucsc truth set")    
   
    def test_29_stop(self):
        print 'In ucsc_gswholeexon start column --up/down arguments test compare old version with truth set'
        self.assertEqual(self.oldbedgswholeexonstart, self.ucsctruthgswholeexonstart, "Failed test - Start sites not the same as ucsc truth set")    
        
    
    def test_30_stop(self):
        print 'In ucsc_gswholeexon stop column --up/down arguments test compare old version with truth set'
        self.assertEqual(self.oldbedgswholeexonstop, self.ucsctruthgswholeexonstop, "Failed test - Stop sites not the same as ucsc truth set")
        
    
 
 
def argums(argv):
    runscripts = Runscripts()
    log = ''
#Generates and interprets a list of options which can be passed as arguments to the function UTR
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["newscript=", "livescript=", "output="])
    except getopt.GetoptError, err:
        print str(err)
        runscripts.usage()
        sys.exit(2)
    output = None
    verbose = False
     
     
    print opts
    for o, a in opts:
 
        if o in ("-h", "--help"):
            runscripts.usage()
            sys.exit()
        elif o == "--newscript":
            if a in ("-h", "--help", "--livescript", "--output"):
                print "need to define --newscript"
                runscripts.usage()
                sys.exit()
            else:
                runscripts.newscript = a
                 
        elif o == "--livescript":
            if a in ("-h", "--help", "--newscript", "--output"):
                print "need to define --livescript"
                runscripts.usage()
                sys.exit()
            else:
                runscripts.livescript = a
                
        elif o == "--output":
            if a in ("-h", "--help", "--newscript", "--livescript"):
                print "need to define --output"
                runscripts.usage()
                sys.exit()
            else:
                runscripts.output = a

		
                
    if not runscripts.output:
       print "--output was not given"
       runscripts.usage()
       sys.exit(2)
                 
    runscripts.subprocessscripts()
                
if __name__ == "__main__":

    log_file = 'log_file.txt'
    f = open(log_file, "w")
    runner = unittest.TextTestRunner(f)
    #subprocess.call("python OOBed7_uses_mirrored_database_resave.py --codingup 30 --codingdown 20 --transcripts /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthset.txt --logfile /home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71test_new_Logfile.txt --useaccessions --outputfile '/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/newoutput.bed'")
    #subprocess.call(['python', 'OOBed7_uses_mirrored_database_resave.py', '--codingup', '30', '--codingdown', '20', '--transcripts', '/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71_truthset.txt', '--logfile', '/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/Pan71test_new_Logfile.txt', '--useaccessions', '--outputfile', '/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/newoutput.bed'])

    argums(sys.argv[1:])
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()
    unittest.main(argv=[sys.argv[0]],testRunner=runner, exit=False)
    print "Moving"
    shutil.move("log_file.txt", "/home/ryank/mokabed/LiveBedfiles/TestArea_for_bed_generation_script/160715krunittest_NewRefGene_GbCdnaInfo_UpdatedTruthSet/log_file.txt")
