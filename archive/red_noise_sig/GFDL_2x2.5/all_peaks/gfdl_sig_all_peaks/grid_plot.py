import numpy as np
import glob
import string
import os
import glob
import sys
import matplotlib.pyplot as plt
from scipy.fftpack import fft,fftfreq, rfft
from mpl_toolkits.basemap import Basemap, shiftgrid, addcyclic
from matplotlib.patches import Polygon
from matplotlib.colors import LogNorm
from cmath import *
import colorsys
from scipy import signal
import re

def sort_nicely( l ):
    """ Sort the given list in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )
    return l

#Ask if want to save out full image, no borders
#full_image = raw_input('Do you want to save out full image? Y or N?\n')
#if full_image == 'Y':
#    f_name = 'gc_2x2.5_%s_%s.png'%(period,type)

#if type == 'magnitude':
#    type_f = 'magnitudes'
    
#else:
#    type_f = 'phases'

#set up plot
fig =plt.figure(figsize=(20,12))
fig.patch.set_facecolor('white')

#if full_image == 'Y':
#    ax = plt.Axes(fig, [0., 0., 1., 1.])
#    ax.set_axis_off()
#    fig.add_axes(ax)

lat = np.arange(-90,91,2)
lon = np.arange(-180,181,2.5)

lat_c = np.arange(-89,90,2)
lon_c = np.arange(-178.75,180,2.5)


for i in range(len(lat_c)): 
    try:
        big_latlon = np.vstack((big_latlon,lon_c))
    except:
        big_latlon = lon_c



model_f = files = glob.glob('modified_GFDL_spectra/*')
model_f = sort_nicely(model_f)

periods = np.load('periods.npy')

#read in all spectra and take key period magnitude
days = 365.25
#key_period =  min(range(len(periods)), key=lambda i: abs(periods[i]-days))
key_period =  min(range(len(periods)), key=lambda i: abs(periods[i]-days))

values = []
for i in model_f:
    print i
    spectra = np.load(i)
    values.append(spectra[key_period])

gridboxes_n = []
remove_one = 'modified_GFDL_spectra/'
remove_two = '.npy'
#get gridbox numbers
for filename in model_f:
    stripped = filename.replace(remove_one,"")
    stripped = stripped.replace(remove_two,"")
    stripped = int(stripped)
    gridboxes_n.append(stripped)

#check for missing invalid gridboxes, if number missing, value is 0
check = range(12960)
missingitems = [x for x in check if not x in gridboxes_n]
values = np.insert(values,missingitems,0)

#check for significant gridboxes for period, use 90% significance
sigs = np.load('significant_periods/sig_period_90.npy')
sigs_boo = np.zeros(len(sigs))
counter = 0
for i in sigs:
    tester = False
    for j in i:
        if j == days:
            tester = True
    if tester == True:
        sigs_boo[counter] = True
    else:
        sigs_boo[counter] = False
    counter+=1 
            
            

start = 0
end = 144

for i in range(90):
	new_list = values[start:end]
	new_list = np.array(new_list)
	try:
		z =np.vstack((z,new_list))
	except:
		z = [new_list]
		z=np.array(z)
	start+=144
	end+=144

#change data from 0 to 360 lon to -180 to 180 lon
z = z.flatten()

start_point = 72
end_point = 144 



for i in range(144):
	array = z[start_point:end_point]
	sig_array = sigs_boo[start_point:end_point]
	try:
		new_array = np.concatenate((new_array,array))
		
	except:
		new_array = array
	
	start_point -= 72
	end_point -= 72
    
	array = z[start_point:end_point]
	new_array = np.concatenate((new_array,array))
	start_point+=216
	end_point+=216

z = np.reshape(new_array,(90,144))

print z.shape
print z[0].shape
print z[1].shape
print big_latlon.shape

#setup basemap projection
m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
                   llcrnrlon=-180,\
                    urcrnrlon=180,\
                   resolution='c')

#if full_image == 'N':
m.drawcoastlines()
m.drawmapboundary()
parallels = np.arange(-90,91,15)
meridians = np.arange(-180,151,30)
plt.xticks(meridians)
plt.yticks(parallels)
m.drawparallels(parallels)
m.drawmeridians(meridians)

#plot model gridboxes
#poly = m.pcolor(lon, lat, z,norm=LogNorm(vmin=np.min(z), vmax=np.max(z)+1),cmap = plt.cm.coolwarm)
poly = m.pcolor(lon, lat, z,vmin=np.min(z), vmax=np.max(z)+0.1,cmap = plt.cm.coolwarm)


#X,Y = m(obs_lons_sig,obs_lats_sig)
#overlay signficant point circles in centres of gridboxes
#m.scatter(X,Y,c=cut_obs,s=15, norm=LogNorm(vmin=np.min(z),vmax=np.max(z)+1),cmap = plt.cm.coolwarm,edgecolor='black',linewidth=0.5)

#if full_image == 'N':
cb = plt.colorbar(poly, ax = m.ax,shrink=0.8,orientation = 'horizontal', format='%.2f')
cb.set_label('ppbv', fontsize = 16)
plt.xlabel('Longitude',fontsize = 20)
plt.ylabel('Latitude',fontsize = 20)
cb.ax.tick_params(labelsize=16)
plt.title('GFDL O3 %s Days'%(days), fontsize = 18)
plt.show()
#else:
#    extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
#    plt.savefig(f_name,bbox_inches=extent)


