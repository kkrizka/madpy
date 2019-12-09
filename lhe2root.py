#!/usr/bin/env python

import array
import ROOT
import madpy
import argparse
import glob
import gzip
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Convert LHE XML files to a ROOT file.')
parser.add_argument('input',type=str,help='glob pattern to use as input files')
parser.add_argument('-o','--output',type=str,default='data.root',help='output name')
args=parser.parse_args()

MAXNPART=10

#
# Define the output file
fh=ROOT.TFile.Open(args.output,'RECREATE')
t=ROOT.TTree('outTree','outTree')

br_weight=array.array('f',[0])
t.Branch('weight',br_weight,'weight/F')

br_nparticle=array.array('i',[0])
t.Branch('nparticle',br_nparticle,'nparticle/I')

br_particle_pt =array.array('f',[0]*MAXNPART)
t.Branch('particle_pt',br_particle_pt,'particle_pt[nparticle]/F')

br_particle_eta=array.array('f',[0]*MAXNPART)
t.Branch('particle_eta',br_particle_eta,'particle_eta[nparticle]/F')

br_particle_phi=array.array('f',[0]*MAXNPART)
t.Branch('particle_phi',br_particle_phi,'particle_phi[nparticle]/F')

br_particle_m  =array.array('f',[0]*MAXNPART)
t.Branch('particle_m',br_particle_m,'particle_m[nparticle]/F')

br_particle_pdg=array.array('i',[0]*MAXNPART)
t.Branch('particle_pdg',br_particle_pdg,'particle_pdg[nparticle]/I')

br_particle_status=array.array('i',[0]*MAXNPART)
t.Branch('particle_status',br_particle_status,'particle_status[nparticle]/I')

for path in glob.glob(args.input):
    df=madpy.load_lhe_pattern(path)
    for i,row in df.iterrows():
        br_weight[0]=row['weight']

        br_nparticle[0]=0
        for particle in row['particles']:
            br_particle_pt    [br_nparticle[0]]=particle.pT
            br_particle_eta   [br_nparticle[0]]=particle.eta
            br_particle_phi   [br_nparticle[0]]=particle.phi
            br_particle_m     [br_nparticle[0]]=particle.M
            br_particle_status[br_nparticle[0]]=particle.status
            br_particle_pdg   [br_nparticle[0]]=particle.pdg
            br_nparticle[0]+=1

        t.Fill()

fh.Write()
fh.Close()
