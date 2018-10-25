#! /usr/bin/env python3 
# fml
#--------------------- 
 
# load external modules 
import argparse  
import numpy as np 
import pandas as pd 
from urllib.request import Request, urlopen
import urllib 
import json 
import os.path
from datetime import datetime

# load local modules 
import getAK_weatherwise as AKww
import russian_connectionLH as RUScon
import canada_connectionLH as CANcon
import makeFigs as mF

def fixLon(datDF):
  datDF.lon.loc[datDF.lon<0] = datDF.lon +360 ## copy warning : I don't care
  return datDF

def procData(datDF):
  datDF = datDF[['lat', 'lon', 'precip', 'temp']]
  datDF = fixLon(datDF)
  tempDF = datDF[['lat', 'lon', 'temp']]
  tempDF = tempDF.dropna()
  pcpDF = datDF[['lat', 'lon', 'precip']]
  pcpDF = pcpDF.dropna()
  return tempDF, pcpDF

# -----------------------------------------------------------

# parse command line 
parser = argparse.ArgumentParser() 
parser.add_argument("year", help="Specify year YYYY") 
parser.add_argument("month", help="Specify month MM") 
args = parser.parse_args() 
 
ak_file = args.year + args.month + 'AKdata.csv'
ca_file = args.year + args.month + 'CANdata.csv'
ru_file = args.year + args.month + 'RUSdata.csv'


# check if data files already exist and load if so, if not call helper fncts to pull data. AK helper is VERY SLOW
# load AK csv
if os.path.exists(ak_file):
  datDF = pd.read_csv(args.year + args.month + 'AKdata.csv')
else :
# this will get the ak data but it takes forever. run it once, then load the csv.
  datDF = AKww.getAK(args.year, args.month)

# load Canada csv
if os.path.exists(ca_file):
  canDF = pd.read_csv(args.year + args.month + 'CANdata.csv')  
else:
  canDF = CANcon.download_canada_data(args.year, args.month)

# load Russia csv
if os.path.exists(ru_file):
  rusDF = pd.read_csv(args.year + args.month + 'RUSdata.csv')
else:
  rusDF = RUScon.download_russia_data(args.year, args.month)

# split into temp and precip DFs
tempDF, pcpDF = procData(datDF)
tempCan, pcpCan = procData(canDF)
tempRus, pcpRus = procData(rusDF)

# merge AK, CAN, RUS data 
tempDF =tempDF.append([tempRus, tempCan], ignore_index=True)
pcpDF =pcpDF.append([pcpRus, pcpCan], ignore_index=True)

# these make the plots. scatter map is a map with the station locations plotted w colour scale & labels, contourMap is the contour map

# mF.scatterMap(tempDF, 'temp', args.month, args.year)
# mF.scatterMap(pcpDF, 'precip', args.month, args.year)
mF.contourMap(tempDF, 'temp', args.month, args.year, 'linear') #last argument is the interpolation method for griddata. can be "cubic", "linear", oder 'nearest'
mF.contourMap(pcpDF, 'precip', args.month, args.year, 'linear')

