#!/usr/bin/env python

import gzip
import pandas as pd
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import madpy

# Open the LHE file
doc=ET.parse(gzip.open('Zjj.lhe.gz'))
df=pd.DataFrame({'raw':[e.text for e in doc.iter('event')]})

# Parse the event entries
df=df.raw.apply(madpy.parse_mg_raw)

# Calculate a few useful variables
df['stable']=df.particles.apply(madpy.filter_stable) # list of sable particles
df['minv']=df.stable.apply(lambda ps: sum(ps,madpy.Particle()).M) # invariant mass of all stable particles

# Plot!
plt.hist(df.minv,bins=40,range=(0,200),weights=df.xsec)
plt.show()
