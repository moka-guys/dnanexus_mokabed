#!/usr/bin/python
import io, sys
import pandas as pd
import re
import cruzdb
from sqlalchemy import create_engine, Column, Integer, String, or_, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:////home/ryank/LiveReferenceSequencs/Versions/Downloaded160612/160612/gbCdnaInfo.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

session = Session()

class RefGenecopy(Base):
    __tablename__ = 'refGenecopy'
    id = Column(Integer, primary_key=True)
    bin  = Column(Integer)
    name  = Column(String(100))
    chrom = Column(String(100))     
    strand  = Column(String(100))
    txStart  = Column(String(100))
    txEnd  = Column(String(100))
    cdsStart  = Column(String(100))
    cdsEnd  = Column(String(100))
    exonCount = Column(String(100))
    exonStarts = Column(String(100))
    exonEnds = Column(String(100))
    score = Column(String(100))
    name2 = Column(String(100))
    cdsStartStat = Column(String(100))
    cdsEndStat = Column(String(100))
    exonFrames = Column(String(100))
    
    def  __repr__(self):
        return "<refGenecopy(bin='%s', name='%s', chrom='%s', strand='%s', txStart='%s', txEnd='%s', cdsStart='%s', cdsEnd='%s', exonCount='%s', exonStarts='%s', exonEnds='%s', score='%s', name2='%s', cdsStartStat='%s', cdsEndStat='%s', exonFrames='%s')>" %(self.bin, self.name, self.chrom, self.strand, self.txStart, self.txEnd, self.cdsStart, self.cdsEnd, self.exonCount, self.exonStarts, self.exonEnds, self.score, self.name2, self.cdsStartStat, self.cdsEndStat, self.exonFrames)


class GbCdnaInfocopy(Base):
    __tablename__ = 'gbCdnaInfo'
    id = Column(Integer, primary_key=True)
    acc  = Column(String(100))
    version = Column(Integer)
    moddate = Column(String(100))
    type = Column(String(100))
    direction = Column(String(100))
    source = Column(Integer)
    organism = Column(Integer)
    library = Column(Integer)
    mrnaClone = Column(Integer)
    sex = Column(Integer)
    tissue = Column(Integer)
    development = Column(Integer)
    cell = Column(Integer)
    cds = Column(Integer)
    keyword = Column(Integer)
    description = Column(Integer)
    geneName = Column(Integer)
    productName = Column(Integer)
    author = Column(Integer)
    gi = Column(Integer)
    mol = Column(String(100))   
    
    def  __repr__(self):
        return "<bCdnaInfocopy(id='%s', acc='%s', version='%s', moddate='%s', type='%s', direction='%s', source='%s', organism='%s', library='%s', mrnaClone='%s', sex='%s', tissue='%s', development='%s', cell='%s', cds='%s', keyword='%s', description='%s', geneName='%s', productName='%s', author='%s', gi='%s', mol='%s')>" %(self.id, self.acc, self.version, self.moddate, self.type, self.direction, self.source, self.organism, self.library, self.mrnaClone, self.sex, self.tissue, self.development, self.cell, self.cds, self.keyword, self.description, self.geneName, self.productName, self.author, self.gi, self.mol)


class Accversion(GbCdnaInfocopy):
     
    def versionfinder(self, accession):
        engine = create_engine('sqlite:////home/ryank/LiveReferenceSequencs/Versions/Downloaded160612/160612/gbCdnaInfo.db', echo=False)
        Base = declarative_base()
        Session = sessionmaker(bind=engine)
    
        session = Session()
        gbCdnaInfocopy = session.query(GbCdnaInfocopy).filter_by(acc = accession).one()
        return gbCdnaInfocopy.acc + "." + str(gbCdnaInfocopy.version)
        
class Liveaccversion():

    def __init__(self):
        self.hgfixed = cruzdb.Genome(db="hgFixed")
        self.livegbcdninfo = self.hgfixed.gbCdnaInfo
        self.liverefLink = self.hgfixed.refLink
        
    def versionfinder(self, accession):
        gbCdnaInfocopy = self.livegbcdninfo.filter_by(acc = accession).one()
        return gbCdnaInfocopy.acc + "." + str(gbCdnaInfocopy.version)
        
        
class LiveRefLink(Liveaccversion):
    def entrezidretrieve(self, accession):
        refLink = self.liverefLink.filter_by(mrnaAcc = accession).one()
        return refLink.locusLinkId
        
        
def main():
    Session = sessionmaker(bind=engine)

    session = Session()

    gene='BRCA2'
    refgenequery = session.query(RefGenecopy).filter(RefGenecopy.name2.like('%' + gene + '%')).one()
    print refgenequery
    print refgenequery.chrom
    #gbCdnaInfocopy = session.query(GbCdnaInfocopy).filter_by(acc = 'AB062753').one()
    #print gbCdnaInfocopy
    #print gbCdnaInfocopy.acc + "." + str(gbCdnaInfocopy.version)
    vers = Accversion()
    vers.versionfinder(sys.argv[1])
    


if __name__ == '__main__':
    main()

