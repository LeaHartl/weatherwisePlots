#! /usr/bin/env python3 
# Pull Russian stations from SOME RANDOM SPANISH website
import urllib3
import re
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import numpy as np
import pandas as pd

def download_russia_data(year, month):
  # THESE NORMALS ARE SKETCHY, I HAVE NO IDEA WHERE THEY CAME FROM. DEPARTURES SEEM REALLY HIGH, WHAT REFERENCE PERIOD IS THIS??
  russian_stations = {
    "Anadyr'":{
      "lat":177.5667,
      "lon":64.7831,
      "temp_norm":[-22.5, -21.9, -19.1, -12.7, -1.4, 6.9, 12.1, 10.5, 4.9, -4.6, -13.3, -19.2],
      "precip_norm":[45.33, 40.39, 33.03, 23.29, 13.04, 18.24, 34.26, 42.83, 31.06, 26.18, 33.41, 41.87]
      },
    "Egvekinot":{
      "lat":-179.1,
      "lon":66.3497,
      "temp_norm":[-18.7, -18.1, -16.3, -11.0, -0.7, 6.4, 10.6, 9.5, 4.3, -3.7, -10.5, -15.8],
      "precip_norm":[32.64, 29.96, 26.13, 20.14, 27.24, 41.72, 76.72, 87.51, 58.88, 47.12, 48.57, 34.10]
      },
    "Mys Billingsa":{
      "lat":175.77,
      "lon":69.8797,
      "temp_norm":[-26.9, -26.9, -24.5, -17.8, -5.1, 1.9, 4.0, 3.7, 0.6, -7.9, -16.9, -23.8],
      "precip_norm":[11.16, 8.50, 7.33, 10.52, 10.43, 15.82, 27.98, 27.46, 23.91, 21.58, 18.53, 11.70]
      },
    "Mys Uelen":{
      "lat":-169.8,
      "lon":66.17,
      "temp_norm":[-20.6, -20.7, -19.6, -12.9, -3.0, 2.9, 7.1, 6.8, 3.6, -1.5, -7.8, -15.8],
      "precip_norm":[21.13, 19.82, 13.10, 17.21, 17.58, 15.59, 31.50, 47.27, 43.17, 38.85, 27.97, 24.58]
      },
    "Ostrov Vrangelja":{
      "lat":-178.4833,
      "lon":70.9831,
      "temp_norm":[-22.9, -23.5, -22.3, -16.6, -5.6, 1.2, 3.5, 3.1, 0.1, -6.3, -13.0, -19.7],
      "precip_norm":[6.84, 7.19, 5.23, 6.60, 7.70, 10.48, 20.69, 24.94, 16.53, 12.78, 10.10, 8.06]
      }
    }

  rus_url = "http://www.ogimet.com/cgi-bin/gclimat?lang=en&mode=1&state=Russ&ord=REV&verb=yes&year=" + year + "&mes=" + month

# LOL
# "El objetivo de este sitio es proporcionar a los usuarios información meteorológica actualizada de una forma rápida y profesional. 
# Este servidor esta conectado a la internet mediante una banda relativamente estrecha. Todo corre en un PC que pueden ver aquí .
# Por favor, no abuse solicitando grandes cantidades de información:
# https://www.ogimet.com/img/ogi_machine.jpg"

  all_results = {}

  http = urllib3.PoolManager()
  request = http.request('GET', rus_url).data


  only_tr_tags = SoupStrainer("tr")
  soup = BeautifulSoup(request, 'html.parser')
  station_table = soup.find_all('table')[3]
  # print(station_table)

  for key, data in russian_stations.items():
    for tr_tag in station_table.findAll('tr'):
      if tr_tag.find('a', string=re.compile(key)):
        td_tag = tr_tag.findAll('td')
        all_results[key] = []
        all_results[key].append(data['lat'])  # lat
        all_results[key].append(data['lon'])  # lon

        # print(td_tag[13])
        tmp= td_tag[4].text
        pcp= td_tag[13].text
        # print(tmp)
        # print(pcp)
        tmp = float(tmp)
        # check for missing data
        if pcp == '\n----' : pcp =  np.nan   #fix hardcoded no data string
        pcp = float(pcp)

        temp_depart = round(float(tmp) - data['temp_norm'][int(month)-1], 2)
        precip_depart = round(float(pcp) / data['precip_norm'][int(month)-1] * 100, 2) #departure as percentage

        all_results[key].append(tmp) 
        all_results[key].append(temp_depart) 
        all_results[key].append(pcp)        # temp depart from normal
        all_results[key].append((precip_depart)) # precentage precip of normal

  # THIS IS METRIC !
  rus_df = pd.DataFrame.from_dict(all_results, orient='index')
  rus_df.columns = ['lon', 'lat', 'tempAbs', 'temp', 'precipAbs', 'precip']
  # CONVERT TO FREEDOM
  rus_df[ 'precipAbs'] = np.round(rus_df['precipAbs'] * 0.039, decimals = 2)
  rus_df[ 'tempAbs'] = np.round(rus_df[ 'tempAbs'] * 9/5 + 32, decimals = 2)
  rus_df[ 'temp'] = np.round(rus_df[ 'temp'] * 9/5, decimals = 2)

  rus_df.to_csv(year + month +'RUSdata.csv', sep=',')
  return rus_df


