#!/usr/bin/python


class Sambamba(object):

    def create_sambamba_bed(self, bedfile,  refseqfile, sambambaoutput): #refseqfile, sambambaoutput):
            '''convert to a bedfile with all columns needed for sambamba'''
            # open input bedfile
            bed = open(bedfile, 'r')
            # open output sambamba file
            sambamba = open(sambambaoutput, 'w')
            # loop through bedfile
            for line in bed:
                strand = "X"
                # write headers
                if line.startswith("#2"):
                    #sambamba.write(line)
                    pass
                elif line.startswith("#Chr"):
                    pass
                    #sambamba.write("#chr\tstart\tstop\tname\tscore\tstrand\ttranscript\tgene symbol\n")
                else:
                    # capture the required info from bedfile
                    splitline = line.split("\t")
                    chr = str(splitline[0].replace("chr", ""))
                    start = str(splitline[1])
                    stop = str(splitline[2])
                    entrez = str(splitline[3])
                    gene_acc = splitline[-1].rstrip()
                    splitgene_acc = gene_acc.split(";")
                    genesymbol = splitgene_acc[0].rstrip()
                    transcripts = splitgene_acc[1]
                    gene_transcripts = genesymbol + ";" + transcripts
                    strand = "+"

                    # create name and score values
                    F3 = chr + "-" + start + "-" + stop
                    F4 = "0"
                    # # open refseq file to capture strand
                    refseq = open(refseqfile, 'r')
                    # loop through refseq file
                    for line2 in refseq:
                        # skip if strand is already captured or if a header
                        if strand != "X" or line2.startswith("#"):
                             pass
                        else:
                            # capture the gene symbol
                            splitline2 = line2.split("\t")
                            gene_acc2 = splitline2[1].rstrip()
                            splitgene_acc2 = gene_acc2.split(";")
                            genesymbol2 = splitgene_acc2[0].rstrip()
                            transcripts2 = splitgene_acc2[1]
                            # if gene symbol in refseq file matches that of bedfile capture the strand
                            if str(genesymbol2) == str(genesymbol):
                                strand = splitline2[3].rstrip()
                    # important to close refseq file so it loops through again for next line in bedfile
                    refseq.close()

                    # write sambamba bedfile line
                    tab = "\t"
                    sambamba.write(chr + tab + start + tab + stop + tab + F3 + tab + F4 + tab + strand + tab + gene_transcripts + tab + entrez + "\n")
            bed.close()
            sambamba.close()


if __name__ == '__main__':
    sam = Sambamba()
    sam.create_sambamba_bed(bedfile="/home/ryank/mokabed/LiveBedfiles/Pan468data.bed", refseqfile="/home/ryank/mokabed/LiveBedfiles/Pan468dataRefSeqFormat.txt", sambambaoutput="/home/ryank/mokabed/LiveBedfiles/Pan468dataSambamba.bed")
    pass