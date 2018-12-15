#! /usr/bin/env python3 
# Get data from ACIS stations
#--------------------- 
 
# load external modules 
import argparse 
import numpy as np 
import pandas as pd 
import requests
import urllib.request
import json 
import os.path
from datetime import datetime

 
# load local modules 
# import data_helpers as dh 
import stations as ws               # ACRC station list 
 
# base URL to REST endpoint
acis_meta_url = "https://data.rcc-acis.org/StnMeta"
acis_multi_station_url = "https://data.rcc-acis.org/MultiStnData?"
acis_meta_valid = {"meta":"valid_daterange", "elems":"avgt"}
acis_depart_elems = { 
  "elems": [{"vX":43, "duration":"mly", "interval":"mly", "reduce":"mean","normal":"departure", "maxmissing":3}, 
            {"vX":4, "duration":"mly", "interval":"mly", "reduce":"sum", "maxmissing":3}, 
            {"vX":4, "duration":"mly", "interval":"mly", "reduce":"mean", "normal":"normal", "maxmissing":3}, 
  ] 
} 

# read data from REST endpoint
def read_data( url, params, header="" ):
  resq = requests.get(url, headers=header, params=params)
  # print( resq.url )
  return resq.json()



def getAK(year, month):

  # date used to check the validity of the station normals
  check_date = datetime(1980, 12, 30)
   
  # set ACIS params
  acis_params = {} 
  acis_params['date'] = year + '-' + month
  acis_params['bbox'] = "-190,48,-125,72"
  acis_params.update(acis_depart_elems) 

   
  # setup data dict
  acis_data = { 
    'stn':[],
    'lat':[], 
    'lon':[], 
    'temp':[], 
    'precip':[], 
  } 

  # encode request and get data from ACIS
  request_params = urllib.parse.urlencode({'params':json.dumps(acis_params)}) 
  acis_station_data = read_data(acis_multi_station_url, params=request_params) 
   
  for station in acis_station_data["data"]:
    # print(station)
    if 'meta' in station: 
      acis_meta_valid["sids"] = station["meta"]["sids"][0]
      acis_station_meta = read_data( acis_meta_url, params=acis_meta_valid) 


      # reject station if it has no valid metadata
      if len(acis_station_meta['meta']) == 0:
        continue

      # reject station if it doesn't have full 30 year normals
      valid_range = acis_station_meta['meta'][0]['valid_daterange'][0]
      start_date = datetime.strptime(valid_range[0], '%Y-%m-%d')
      if start_date > check_date:
        continue

      station_ll = station['meta']['ll'] 
      lon, lat = station_ll 
      stn = station['meta']['name']
   
      station_data = station['data'] 
      deptemp, precip, pnorm = station_data 
      # print (station_data)
  # fix strings temp
      if deptemp=='M': deptemp = np.nan 
      acis_data['stn'].append(stn) 
      acis_data['lat'].append(lat) 
      acis_data['lon'].append(lon) 
      acis_data['temp'].append(round(float(deptemp), 1)) 

  # fix strings precip
      if precip == 'T': precip = 0.0
      if precip == 'M': precip = np.nan
      if pnorm == 'M': pnorm = np.nan
      precip_percentage = np.around(((float(precip))/float(pnorm))*100) 
      acis_data['precip'].append(precip_percentage)

  # print(acis_data)
  # make df and dump
  datDF = pd.DataFrame(acis_data)
  datDF.to_csv(year + month +'AKdata.csv', sep=',')
  return datDF

