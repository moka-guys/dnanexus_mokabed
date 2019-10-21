'''
Created on 2 Dec 2016

@author: kevin
'''

import cruzdb, os
import pandas as pd, subprocess
from OOBed7_uses_mirrored_database_ import Bedfile
from sqlalchemy import or_

def refgenelist():
    

    ###################################### Generate list of NM gene symbols includes genes for which there exist NR accessions also #############
    g = cruzdb.Genome(db='hg19')
    ##Returns all Gene symbols in name2 column (this contains repeats and non-coding gene symbols)
    df_raw = g.dataframe('refGene')
    #Generate a subset of dataframe containing just the chr1-22,X and Y 
    df = df_raw.loc[df_raw['chrom'].isin(['chr1', 'chr2', 'chr3', 'chr4', 'chr5', 'chr6', 'chr7', 'chr8', 'chr9', 'chr10', 'chr11', 'chr12', 'chr13', 'chr14', 'chr15', 'chr16', 'chr17', 'chr18', 'chr19', 'chr20', 'chr21', 'chr22', 'chrX', 'chrY'])].copy()
    
    #####Generate a list of true false values indicating the presence or absence of an NM accession string in the name column
    df['Boolean_NMaccessions'] = df.name.str.contains(pat='NM_')
    #####Generate a df which contains only those rows which contain a NM accession in the name column
    df4 = df[df['Boolean_NMaccessions'] == True]
    #####Remove duplicate gene symbol names
    df5 = df4.drop_duplicates('name2')
    
    
    #####Return just the Gene Symbol list
    df6 = pd.DataFrame(zip(df5['name2']),  columns = ["GeneSymbol"])
    ##### Concatanate Gene Symbol list with empty Accession column
    df7 = pd.concat([df6, pd.DataFrame(columns=['Accession'])])
    ##### Re-index data frame so that GeneSymbol column is the index
    df7_reindex = df7.reindex(columns=['Accession'], index=[df6['GeneSymbol']])
    
    df7_reindex.index.name = "GeneSymbol"
    
    ##### Write the list of GeneSymbols to a text file
    #df7_reindex.to_csv(path_or_buf='/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/RefGene_gene_list_2016_12_02/RefGene_Gene_symbols_removeduplicates_NMaccessionGenes_Pan468.csv', sep='\t')
    df7_reindex.to_csv(path_or_buf='/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan468.txt', sep='\t')

    
     
    
    ################### Verify that all coding regions have been captured by  running the code below #######################################

    df['Boolean'] = df['cdsEndStat'].str.contains(pat='cmpl')
    
    df2 = df[df['Boolean'] == True]
    
    df3 = df2.drop_duplicates('name2')
    
    #####Calculate the number of entries relating to gene symbols containing NM accessions
    #logger = open("/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/RefGene_gene_list_2016_12_02/refgenelist_log.txt", "w+")
    logger = open("/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan468_Pan492_Pan493_refgenelist_log.txt", "w+")
    logger.write("Total number of coding gene entries (counts number of NM accessions) in RefGene table = " + str(len(df5[df5['Boolean_NMaccessions'] == True])) + "\n")
    logger.write("Alternative method to generate total number of coding gene entries (counts number cdsEndStat entries = cmpl) of cds in RefGene table = " + str(len(df3[df3['Boolean'] == True])) + "\n")
   
    logger.close()
    
        
    ###################################### Generate list of NR gene symbols includes genes for which there exist NM accessions also #############
    
    ##### Return True value if NR_ accession present otherwise return False
    df['Boolean'] = df['name'].str.contains(pat='NR_')
    
    ##### Generate a df which contains only those rows which contain a NR accession in the name column
    df8 = df[df['Boolean'] == True]
    
    ##### Remove duplicate gene symbol names
    df9 = df8.drop_duplicates('name2')
    #####Return just the Gene Symbol list
    df10 = pd.DataFrame(zip(df9['name2']),  columns = ["GeneSymbol"])
    ##### Concatenate Gene Symbol list with empty Accession column
    df11 = pd.concat([df10, pd.DataFrame(columns=['Accession'])])
    ##### Re-index data frame so that GeneSymbol column is the index
    df11_reindex = df11.reindex(columns=['Accession'], index=[df11['GeneSymbol']])
    
    df11_reindex.index.name = "GeneSymbol"
    
    ##### Write the list of GeneSymbols to a text file
    #df11_reindex.to_csv(path_or_buf='/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/RefGene_gene_list_2016_12_02/RefGene_Gene_symbols_removeduplicates_NRaccessionGenes.csv', sep='\t')


    ################### Verify that all non-coding regions have been captured by running the code below #######################################

    df['Boolean_alternative'] = df['cdsEndStat'].str.contains(pat='unk')

    df12 = df[df['Boolean_alternative'] == True]
    
    df13 = df12.drop_duplicates('name2')
    
    len(df13[df13['Boolean_alternative'] == True])
    
    #####Calculate the number of entries relating to non-coding gene symbols
    #logger = open("/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/RefGene_gene_list_2016_12_02/refgenelist_log.txt", "a+")
    logger = open("/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan468_Pan492_Pan493_refgenelist_log.txt", "a+")
    logger.write("Total number of non-coding gene entries (counts number of NR accessions) in RefGene table = " + str(len(df9[df9['Boolean'] == True])) + "\n")
    logger.write("Alternative method to generate total number of non-coding gene entries (counts number cdsEndStat entries = unk) in RefGene table = " + str(len(df13[df13['Boolean_alternative'] == True])) + "\n")
                                                                                                                
    logger.close()
    
    ###################################### Generate list of NR gene symbols - do not include genes for which there exist NM accessions also #############
       
    # df column indicating True for Genes with NM and NR accessions and False otherwise
    df10['BooleanTrueNRNM'] = df10['GeneSymbol'].isin(df6['GeneSymbol'])
    # df containing just genes which have an NR accession but no corresponding NM accession
    dfNR_minusNMgenes = df10.loc[df10['BooleanTrueNRNM'] == False]
    
    ##### Concatenate Gene Symbol list with empty Accession column
    dfNR_minusNMgenes = pd.concat([dfNR_minusNMgenes, pd.DataFrame(columns=['Accession'])])
    ##### Re-index data frame so that GeneSymbol column is the index
    dfNR_minusNMgenes_reindex = dfNR_minusNMgenes.reindex(columns=['Accession'], index=[dfNR_minusNMgenes['GeneSymbol']])
    dfNR_minusNMgenes_reindex.to_csv(path_or_buf='/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan492.txt', sep='\t')
    
        
    
    # Merge df7 (list of genes which contain a NM accession or a NM and NR accession) merged with df11 (list of genes containing NR or NM and NR accesion)
    # This merge returns just the genes which have both NM and NR accessions
    dfmerge = pd.merge(df7, df11, on=["GeneSymbol"], how='inner')
    
    
    
        
    #logger = open("/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/RefGene_gene_list_2016_12_02/refgenelist_log.txt", "a+")
    logger = open("/run/user/1000/gvfs/sftp:host=athena.kcl.ac.uk,user=ryank/home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan468_Pan492_Pan493_refgenelist_log.txt", "a+")
    logger.write("Breakdown of gene symbols with NR accessions \n.Total number of coding gene entries in RefGene table with a non-coding accession = " + str(len(dfmerge)) + "\n")
    logger.write("Total number of gene entries in RefGene table with a non-coding accession and no corresponding NM accession = " + str(len(dfNR_minusNMgenes_reindex)) + "\n")
    if (len(dfNR_minusNMgenes_reindex) + len(dfmerge)) == len(df9[df9['Boolean'] == True]):
        logger.write("The number of NR related genes tally:" + " " + str(len(dfNR_minusNMgenes_reindex)) + " + " + str(len(dfmerge)) + " = " + str(len(df9[df9['Boolean'] == True])) + "\n")
    else:
        logger.write("ERROR the number of NR related genes do not tally check the number of genes which just have NR accessions only plus genes which have NM and NR accessions equal the total number of genes which have a NR accession\n")
                                                                                                     
    logger.close()
    
    
    
    return len(dfNR_minusNMgenes_reindex), len(dfmerge), len(df9[df9['Boolean'] == True])
    
def convert(v):
    try:
        return int(v)
    except ValueError:
        return v


def concatenaterefseqfiles():

    #Take the RefSeq files that have been generated 
    refseq1 = pd.read_table('/home/ryank/mokabed/LiveBedfiles/Pan492dataRefSeqFormat.txt', header= 0)
    refseq2 = pd.read_table('/home/ryank/mokabed/LiveBedfiles/Pan468dataRefSeqFormat.txt', header= 0)
    # Append the dataframes together
    combinedrefseq = refseq1.append(refseq2)
    
    # Alter number values to integers in chrom column
    chromvals = [convert(val) for val in combinedrefseq['chrom'].values]
    print len(chromvals)
    print len(combinedrefseq['chrom'].values)
    # Replace chrom column with formatted list chromvals
    mapping = {'1' : 1, '2' : 2, '3' : 3, '4' : 4, '5' : 5, '6' : 6, '7' : 7,  '8' : 8, '9' : 9, '10' : 10, '11' : 11, '12' : 12, '13' : 13, '14' : 14, '15' : 15,
'16' :16, '17' : 17, '18' : 18, '19' : 19, '20' : 20, '21' : 21, '22' : 22} 
    combinedrefseq.replace({'chrom' : mapping}, inplace=True)
    #Reorder refseq file based on chrom, cdsStart, cdsStop
    result = combinedrefseq.sort(['chrom', 'cdsStart', 'cdsEnd', '#bin'], ascending=[1, 1, 1, 1])
    
    #result = combinedrefseq.sort_values(['chrom', 'cdsStart', 'cdsEnd'], ascending=[1, 1, 1])  # updated version of pandas df.sort()
    result.set_index(['#bin'], inplace=True)
    result1 = result.applymap(lambda x: str(x))
    finalresult1 = result1.fillna('NULL')
    #Write file out to csv file
    finalresult1.to_csv(path_or_buf='/home/ryank/mokabed/LiveBedfiles/Pan493dataRefSeqFormat.txt' ,sep='\t')
    return '/home/ryank/mokabed/LiveBedfiles/Pan493dataRefSeqFormat.txt'

def concatenaterefseqfilescheck(refseqfile):

    #Test generation of concatenated refseq file
    #Alternative method of generating concatenated refseq file
    filenames = ['/home/ryank/mokabed/LiveBedfiles/Pan492dataRefSeqFormat.txt', '/home/ryank/mokabed/LiveBedfiles/Pan468dataRefSeqFormat.txt']
    out = '/home/ryank/test/Pan493dataRefSeqFormattest.txt'
    with open(out, 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                if filenames.index(fname) == 1:
                    for i, line in enumerate(infile):
                            if i == 0:
                                pass
                            else:
                                outfile.write(line)
                else:
                    for line in infile:
                        outfile.write(line)
    finaloutfile = '/home/ryank/test/Pan493dataRefSeqFormattestfinal.txt'
    # sort refseq file based on chrom, cdsStart, cdsStop
    #with open(finaloutfile, "w") as finalout:
    with open(out, 'r') as outfile:
        header = outfile.readline()
    
    p1 = subprocess.Popen('tail -n +2 "%s" | sort -k3,3V -k7,7n -k8,8n -k1,1n > "%s"'% (out, finaloutfile), shell=True)
    # Need to wait until p1 has finished before p2 can begin
    p1.wait()
    # Add header
    p2 = subprocess.Popen("sed -i '1 i\%s' %s"% (header, finaloutfile), shell=True)
    # Need to wait until p2 has finished before p3 can begin
    p2.wait()   
    # Perform diff of refseq files      
    p3 = subprocess.Popen("diff  %s %s > /home/ryank/test/filecheck.txt"% (refseqfile, finaloutfile), shell=True)


def calldb(database='hg19'):
    g = cruzdb.Genome(db=database)
    refGene = g.refGene
    return refGene

#Return number of overlapping bases
def getOverlap(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))

def disparateregiongenes(gene):
        
    
    # Checks if any of the returned regions for a gene do not overlap indicating that the genes are mapped to alternative regions
    try:
        regionslist = refGene.filter_by(name2=gene).filter(or_(refGene.chrom=='chr1', refGene.chrom=='chr2', refGene.chrom=='chr3', refGene.chrom=='chr4', refGene.chrom=='chr5', refGene.chrom=='chr6', refGene.chrom=='chr7', refGene.chrom=='chr8', refGene.chrom=='chr9', refGene.chrom=='chr10', refGene.chrom=='chr11', refGene.chrom=='chr12', refGene.chrom=='chr13', refGene.chrom=='chr14', refGene.chrom=='chr15', refGene.chrom=='chr16', refGene.chrom=='chr17', refGene.chrom=='chr18', refGene.chrom=='chr19', refGene.chrom=='chr20', refGene.chrom=='chr21', refGene.chrom=='chr22', refGene.chrom=='chrX', refGene.chrom=='chrY')).all()
                
    except:
        regionslist = refGene.filter_by(name2=gene).filter(or_(refGene.chrom=='chrX')).all()

    
    regions = []
    #Generate a list of intervals for the gene
    for region in regionslist:
        regionstartstop = [region.name2, region.chrom, region.start, region.end]
        regions.append(regionstartstop)

    #Iterate over regions list and genrate a list of regions that don't overlap
    #First sort the list in-place in genomic order based on chr then start and stop
    regions = sorted(regions)
        
    nonoverlaps = []
    compare=''
    if len(regions) > 1:
        for i, r in enumerate(regions[:-1]):
            compare2 = regions[i+1][2:]
            if not compare:     
                compare = r[2:]
                appendval = r
                
            if getOverlap(compare, compare2) == 0:
                if appendval not in nonoverlaps:
                    nonoverlaps.append(appendval)
                if regions[i+1] not in nonoverlaps:
                    nonoverlaps.append(regions[i+1])
                compare = ''
                 
    
            else:
                mergelist = [compare, compare2]
                mergeboundaries = [val for val in Bedfile().merge_ranges(mergelist)]
                compare = mergeboundaries[0]
                #print list(mergeboundaries[0])
                appendval = r[:2] + list(mergeboundaries[0])
            
    return nonoverlaps



if __name__ == '__main__':
    
    #print refgenelist() #Uncomment this line to the left if you want to generate a list of refgene genes (generates coding gene list(some of these genes will have NM and NR accessions associated with them) and a seaparate list of non-coding genes
    refseq = concatenaterefseqfiles() # Uncomment this line if you want to concatenate the refseq gene list files (i.e. use it for concatenating the coding and non-coding refseq files)
    concatenaterefseqfilescheck(refseq) # Checks that the refseq files have been concatenated correctly that were generated by the function concatenaterefseqfiles()
    #Take the RefSeq files that have been generated 
    #refseq1 = pd.read_table('/home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan492.txt', header= 0)
    #refseq2 = pd.read_table('/home/ryank/mokabed/LiveBedfiles/Transcripts/Pantranscriptfiles/Pan468.txt', header= 0)
    #refseq1 = pd.read_table('/home/ryank/test/Pan492check.txt', header= 0)
    #refseq2 = pd.read_table('/home/ryank/test/Pan468check.txt', header= 0)
    # Append the dataframes together
    #combinedrefseq = refseq1.append(refseq2)
    #refGene = calldb()
    #totalnonoverlapregions = filter(lambda x: True if len(x) > 0 else False, map(disparateregiongenes, combinedrefseq['GeneSymbol']))
    #totalnonoverlapgenes = filter(disparateregiongenes, combinedrefseq['GeneSymbol'])
    #seriesnonoverlapregions = pd.Series(totalnonoverlapregions)
    #seriesnonoverlapgenes = pd.Series(totalnonoverlapgenes)
    #nonoverlapgenes = pd.DataFrame(zip(seriesnonoverlapregions, seriesnonoverlapgenes),  columns = ["Non-overlap_regions", "Non-overlap_genes"])
    #nonoverlapgenes.to_csv(path_or_buf='/home/ryank/test/non-overlap_genes', sep='\t')
    #nonoverlapgenes.to_csv(path_or_buf='/home/ryank/test/non-overlap_genes_includePARs', sep='\t')
    #nonoverlapgenes.to_csv(path_or_buf='/home/ryank/test/non-overlap_genes_includeCHECK', sep='\t')

