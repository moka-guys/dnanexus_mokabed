# dnanexus_mokabed - v1.2

## What does this app do?
This app utilises the MokaBED code to generate BED files.

The app clones the production branch of the mokabed code (https://github.com/woook/mokabed)

The app requires a list of gene symbols or transcripts, a set of parameters which are used to query the UCSU databases (cruzdb_refGene.db and gbCdnaInfo.db) and outputs bedfiles in a range of formats (more below).

## What data are required for this app to run?

This app requires an input file:

This input file should be named PanX.txt where X is the panelnumber generated by Moka. This number will be used to name all the bedfiles produced.

1.  If using a list of genes:
    * The list of gene symbols must contain at least 1 column. 
    * The first column must contain a list of gene symbols.
    * A header is present
    * You must not mix accessions with gene symbols.

	Eg:

	GeneSymbol 

	A1BG

	A1CF

2. If using a list of transcripts:
    * The list of accessions must contain at least two columns.
    * A header is present (each column contains a header).
    * The first column should contain the list of NM accessions without version numbers. 
    * You must not mix gene symbols with accessions in this first column. 
    * There is no stipulation on what the second column should contain but generally it contains the corresponding gene symbol for the accession in the first column.
    * The third column can be used to specify an accession number.

	Eg:

	Accession	ApprovedSymbol	GuysAccessionVersion

	NM_022051		 EGLN1		1

	NM_000143		 FH	2

	NM_001077196 	PDE11A	3


The app also requires a number of parameters:

1.Coding up/down

Extends the coding exons by this number of bases.

2. Up/Down

Extends the UTR (non-coding exons) by this number of bases.

3. Merge boundaries

A boolean flag which, if set, combines any overlapping exons or regions into a single line in the bed file. Eg 

	Chr1	100	150

	Chr1	140	200

If merge boundaries is True the above would be output as: 

	Chr1 100	200

4.Remove Chr

A boolean flag which, if set, does not add the string ‘Chr’ to the chromosome field of the bed file. 
 

## What does this app output?
This app produces at least four outputs:

1. PanXdata.bed

This bed file is used by HS Metrics function to generate QC.

2. PanXdataRefSeqFormat.txt

This bed file was used by GATK depth of coverage (Not in use)

3.  PanXdatasambamba.bed

This bed file is used to calculate clinical coverage

4. PanX_LogFile.txt

Contains all the commands and instructions used to create this bed file.


If using a list of gene symbols two further files are produced:

1. Synonymsnotinrefgene 

Lists the gene symbols that were loaded from the gene symbol list that were not found in the RefGene table.

2. Synonymsnocodingregions 

Lists gene symbols that were not found to have any coding regions. 

**If either file contains any gene symbols are flagged up in either of these files then the gene symbol list will need to be discussed with the bioinformatics team.**


If using transcripts and one cannot be found the script will stop with an error.

## Limitations of the App
The following UCSC databases are queried:
* cruzdb_refGene.db 
* gbCdnaInfo.db

## Created by
This app was created within the Viapath Genome Informatics section
