from math import *
import xml.etree.ElementTree as ET
import glob
import gzip

import pandas as pd

def load_lhe_pattern(pattern):
    dfs=[]
    for path in glob.glob(pattern):
        doc=ET.parse(gzip.open(path) if path.endswith('gz') else path)
        df=pd.DataFrame({'raw':[e for e in doc.iter('event')]})
        df=df.raw.apply(parse_mg_raw)
        dfs.append(df)
    return pd.concat(dfs)


class Particle:
    def __init__(self,pdg=None,status=None,px=0,py=0,pz=0,M=0):
        self.pdg=pdg
        self.status=status

        self.px=px
        self.py=py
        self.pz=pz
        self.M =M

    @property
    def E(self):
        return sqrt(self.M**2+self.px**2+self.py**2+self.pz**2)

    @property
    def pT(self):
        return sqrt(self.px**2+self.py**2)

    @property
    def eta(self):
        p=sqrt(self.px**2+self.py**2+self.pz**2)
        cosTheta=self.pz/p if p!=0 else 1.0
        if cosTheta*cosTheta < 1.:
            return -0.5* log( (1.0-cosTheta)/(1.0+cosTheta) )
        if self.pz == 0:
            return 0
        if self.pz > 0:
            return 10e10;
        return -10e10;
    
    @property
    def phi(self):
        return atan2(self.py,self.px)
    
    @property
    def stable(self):
        return self.status==1

    def __add__(self,other):
        spart=Particle()
        spart.px=self.px+other.px
        spart.py=self.py+other.py
        spart.pz=self.pz+other.pz
        spart.E =self.E +other.E

        return spart

def parse_mg_raw(raw):
    #
    # Parse the text content
    xsec=None
    particles=[]

    lines=raw.text.split('\n')
    for line in lines:
        line=line.strip()
        if line=='': continue

        if xsec==None: #first line
            xsec=float(line.split()[2])
        else: # particle
            parts=line.split()
            p=Particle(int(parts[0]),int(parts[1]),float(parts[6]),float(parts[7]),float(parts[8]),float(parts[10]))
            particles.append(p)

    #
    # Parse any extra weights
    weights=[]
    rwgt=raw.find('rwgt')
    if rwgt!=None:
        for w in rwgt.iter('wgt'):
            weights.append(float(w.text))
    if len(weights)==0:
        weights=[1.]

    return pd.Series({'xsec':xsec,'particles':particles,'weight':weights[0]})

def filter_stable(particles):
    return list(filter(lambda p: p.stable,particles))
