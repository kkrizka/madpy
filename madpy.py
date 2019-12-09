from math import *
import xml.etree.ElementTree as ET
import glob

import pandas as pd

def load_lhe_pattern(pattern):
    dfs=[]
    for path in glob.glob(pattern)[0:10]:
        doc=ET.parse(path)
        df=pd.DataFrame({'raw':[e for e in doc.iter('event')]})
        df=df.raw.apply(parse_mg_raw)
        dfs.append(df)
    return pd.concat(dfs)


class Particle:
    def __init__(self,pdg=None,status=None,px=0,py=0,pz=0,E=0):
        self.pdg=pdg
        self.status=status
        
        self.px=px
        self.py=py
        self.pz=pz
        self.E =E

    @property
    def M(self):
        return sqrt(self.E**2-self.px**2-self.py**2-self.pz**2)

    @property
    def pT(self):
        return sqrt(self.px**2+self.py**2)

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
            p=Particle(int(parts[0]),int(parts[1]),float(parts[6]),float(parts[7]),float(parts[8]),float(parts[9]))
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
