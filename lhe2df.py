#!/usr/bin/env python

import pandas as pd
import madpy
import argparse

parser = argparse.ArgumentParser(description='Convert LHE XML files to a file containing a pandas DataFrame.')
parser.add_argument('input',type=str,help='glob pattern to use as input files')
parser.add_argument('-t','--type',type=str,default='pickle',help='output type')
parser.add_argument('-o','--output',type=str,default='data',help='output name without extension')
args=parser.parse_args()


df=madpy.load_lhe_pattern(args.input)

if args.type=='pickle':
    df.to_pickle('{}.pkl'.format(args.output))
else:
    print('Error: unknown output type {}'.format(args.type))
