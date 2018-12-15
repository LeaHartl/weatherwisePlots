#! /usr/bin/env python3 
# fml
#--------------------- 
 
import numpy as np 
from numpy import meshgrid
from mpl_toolkits.basemap import Basemap 
import matplotlib.pyplot as plt 
from matplotlib.colors import ListedColormap, BoundaryNorm 
import matplotlib.colors as colors
from scipy.interpolate import griddata
import scipy.ndimage
from PIL import Image


# set the colormap and center the colorbar
class MidpointNormalize(colors.Normalize):
  """
  Normalise the colorbar so that diverging bars work there way either side from a prescribed midpoint value)

  e.g. im=ax1.imshow(array, norm=MidpointNormalize(midpoint=0.,vmin=-100, vmax=100))
  """
  def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
    self.midpoint = midpoint
    colors.Normalize.__init__(self, vmin, vmax, clip)

  def __call__(self, value, clip=None):
    # I'm ignoring masked values and all kinds of edge cases to make a
    # simple example...
    x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
    return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))


#----scatter maps f Tony---------------
def scatterMap(datDF, param, month, year):
  # this is the data
  data  = np.round(datDF[param].values, decimals = 1)

  # set colors etc
  if param == 'temp':
    cm="RdYlBu_r"
    datnorm = MidpointNormalize(midpoint=0.0, vmin=min(data), vmax=max(data))
    cblabel = 'Temperature Scale (°F)'
    pltTitle =  year + "-" + month + ", Mean Temperature Departure From Normal (1981-2010)"

  if param == 'precip':
    cm="PiYG"
    datnorm = MidpointNormalize(midpoint=100.0, vmin=min(data), vmax=max(data))
    cblabel = 'Precipitation Scale (%)'
    pltTitle =  year + "-" + month + ", Mean Precipitation Departure From Normal (1981-2010)"

  # start plot, make map
  fig = plt.figure(figsize=(15, 10)) 
  ax  = fig.add_subplot(111) 

  m = Basemap(width=3500000, height=2500000, 
                resolution='i', projection='aea', 
                lat_1=40, lat_2=70, lon_0=-145+360, lat_0=63) 
  # project to map coords
  projected_lon, projected_lat = m(*(datDF.lon.values, datDF.lat.values))

  m.drawcoastlines()
  m.drawstates()
  m.drawcountries()

  # # draw station markers
  sctr = m.scatter(
      projected_lon,
      projected_lat,
      c=data,
      marker="o", 
      edgecolor="dimgrey", 
      linewidth=0.5, 
      s=40,
      cmap=cm, 
      norm=datnorm,
      ax=ax,
      zorder=5)

# label points with values
  for i, (x, y) in enumerate(zip(projected_lon, projected_lat), start=0):
    # print(data[i])
    ax.annotate(str(data[i]), (x,y), xytext=(5, 5), textcoords='offset points')

# draw colorbar and labels
  cbar = plt.colorbar(sctr, orientation='horizontal', fraction=.057, pad=0.05)
  cbar.ax.tick_params(labelsize=20, length=0 ) 
  cbar.set_label(cblabel, fontsize=18)
  plt.title(pltTitle, fontsize=18)

  # plt.show()
  plt.savefig(year + month + "_" + param + '.png', dpi=200, bbox_inches='tight')
  plt.close()


#----contour maps---------------
def contourMap(datDF, param, month, year, interp):

  # set colors etc
  if param == 'temp':
    levels = [-4, -2, 0, 2, 4, 6, 8, 10, 12]
    colors = ['teal', 'c', 'bisque', 'gold', 'orange', 'peru', 'salmon', 'tomato']
    cblabel = 'Temperature Scale (°F)'
    pltTitle =  year + "-" + month + ", Mean Temperature Departure From Normal (1981-2010), interp. " +interp

  if param == 'precip':
    levels = [0, 50, 100, 150, 200, 250]
    colors = ['red', 'peru', 'green', 'teal', 'navy', 'k']
    cblabel = 'Precipitation (%)'
    pltTitle =  year + "-" + month + ", Mean Precipitation Departure From Normal (1981-2010), interp. " +interp



  # start plot, make map
  fig = plt.figure(figsize=(15, 10)) 
  ax  = fig.add_subplot(111) 

  m = Basemap(width=3500000, height=2500000, 
                resolution='i', projection='aea', 
                lat_1=40, lat_2=65, lon_0=-155+360, lat_0=63) 
  # project to map coords
  projected_lon, projected_lat = m(*(datDF.lon.values, datDF.lat.values))

  m.shadedrelief()
  m.drawcoastlines()
  m.drawstates()
  m.drawcountries()

  # sf = shapefile.Reader('shapefiles/states', name='STATE_NAME')
  # ss = sf.shapes()
  # poly1 = Polygon(ss[0].points)
  # m.readshapefile('shapefiles/states', name='STATE_NAME', drawbounds=True) 
 
  # patches   = [] 
 
  # for info, shape in zip(temp_map.STATE_NAME_info, temp_map.STATE_NAME): 
  #   if info['STATE_NAME'] == 'Alaska': 
  #       patches.append( Polygon(np.array(shape), True) ) 
         
  # ax.add_collection(PatchCollection(patches, facecolor= 'lightgrey', zorder=1))

  # this is the data
  data  = datDF[param].values

  # do the grid stuff
  xgrid = np.linspace(projected_lon.min(), projected_lon.max(), len(datDF.lon.values))
  ygrid = np.linspace(projected_lat.min(), projected_lat.max(), len(datDF.lon.values))

  xi, yi = np.meshgrid(xgrid, ygrid)

  zi = griddata((projected_lon, projected_lat),data,(xi,yi),method=interp)

  # plot contour f
  conf = m.contourf(xi,yi,zi,zorder=4, alpha=0.4 ,colors = colors, levels=levels)  
  # add contour lines
  con = m.contour(xi,yi,zi,zorder=4, alpha=1 ,colors = 'k', levels=levels)  
  plt.clabel(con, fmt="%1.0f", fontsize=16)

  # # draw stations
  m.scatter(
      projected_lon,
      projected_lat,
      edgecolor='#ffffff',
      alpha=.5,
      c=data,
      cmap=conf.cmap,
      ax=ax,
      zorder=4)
  #
  # draw colorbar and labels
  cbar = plt.colorbar(conf, orientation='horizontal', fraction=.057, pad=0.05)
  cbar.ax.tick_params(labelsize=20, length=0 ) 
  cbar.set_label(cblabel, fontsize=18)
  plt.title(pltTitle, fontsize=18)

  # plt.show()
  plt.savefig(year + month + "_" + param + '_Contour_'+interp+'.png', dpi=200, bbox_inches='tight')
  plt.close()
