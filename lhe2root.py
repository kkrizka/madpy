#!/usr/bin/env python

import array
import ROOT
import argparse
import glob
import gzip
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Convert LHE XML files to a ROOT file.')
parser.add_argument('input',type=str,help='glob pattern to use as input files')
parser.add_argument('-o','--output',type=str,default='data.root',help='output name')
args=parser.parse_args()

MAXNPART=64

#
# Define the output file
fh=ROOT.TFile.Open(args.output,'RECREATE')
t=ROOT.TTree('outTree','outTree')

br_weight=array.array('f',[0])
t.Branch('weight',br_weight,'weight/F')

br_nparticle=array.array('i',[0])
t.Branch('nparticle',br_nparticle,'nparticle/I')

br_particle_pt    =array.array('f',[0]*MAXNPART)
t.Branch('particle_pt'    ,br_particle_pt    , 'particle_pt[nparticle]/F'    )

br_particle_eta   =array.array('f',[0]*MAXNPART)
t.Branch('particle_eta'   ,br_particle_eta   , 'particle_eta[nparticle]/F'   )

br_particle_phi   =array.array('f',[0]*MAXNPART)
t.Branch('particle_phi'   ,br_particle_phi   , 'particle_phi[nparticle]/F'   )

br_particle_m     =array.array('f',[0]*MAXNPART)
t.Branch('particle_m'     ,br_particle_m     , 'particle_m[nparticle]/F'     )

br_particle_pdg   =array.array('i',[0]*MAXNPART)
t.Branch('particle_pdg'   ,br_particle_pdg   , 'particle_pdg[nparticle]/I'   )

br_particle_status=array.array('i',[0]*MAXNPART)
t.Branch('particle_status',br_particle_status, 'particle_status[nparticle]/I')

br_weights={}

#
# the loop
p4=ROOT.TLorentzVector()

for path in glob.glob(args.input):
    print(path)
    for event,element in ET.iterparse(gzip.open(path) if path.endswith('gz') else path):
        if element.tag=='event':
            # Parse the particles in the event
            xsec=None
            br_nparticle[0]=0
            
            lines=element.text.split('\n')
            for line in lines:
                line=line.strip()
                if line=='': continue
                if line[0]=='#': continue

                if xsec==None: #first line
                    xsec=float(line.split()[2])
                else: # particle
                    parts=line.split()
                    pdg=int(parts[0])
                    status=int(parts[1])
                    px=float(parts[ 6])
                    py=float(parts[ 7])
                    pz=float(parts[ 8])
                    e =float(parts[ 9])

                    p4.SetPxPyPzE(px,py,pz,e)
                    br_particle_pt    [br_nparticle[0]]=p4.Pt ()
                    br_particle_eta   [br_nparticle[0]]=p4.Eta()
                    br_particle_phi   [br_nparticle[0]]=p4.Phi()
                    br_particle_m     [br_nparticle[0]]=p4.M  ()
                    br_particle_pdg   [br_nparticle[0]]=pdg
                    br_particle_status[br_nparticle[0]]=status
                    br_nparticle[0]+=1
            br_weight[0]=xsec


            # Parse extra weights in the event
            rwgt=element.find('rwgt')
            if rwgt!=None:
                for w in rwgt.iter('wgt'):
                    wname=w.attrib['id']
                    if wname not in br_weights: # create a new branch if needed
                        br_rwgt=array.array('f',[0])
                        t.Branch('weight_{}'.format(wname),br_rwgt,'weight_{}/F'.format(wname))
                        br_weights[wname]=br_rwgt

                    br_weights[wname][0]=float(w.text)

            # Fil the tree to finish the event
            t.Fill()
            element.clear()

fh.Write()
fh.Close()
