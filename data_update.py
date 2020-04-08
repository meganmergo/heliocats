'''
https://github.com/cmoestl/heliocats  data_update.py

for updating data every day 



MIT LICENSE
Copyright 2020, Christian Moestl 
Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:
The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''


import pickle
import importlib
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import sys
import numpy as np
import datetime
import scipy.signal
import urllib
import json
import os   


#import 

from heliocats import data as hd
importlib.reload(hd) #reload again while debugging

from heliocats import plot as hp
importlib.reload(hp) #reload again while debugging


#for server
matplotlib.use('Agg')
#matplotlib.use('qt5agg')

data_path='/nas/helio/data/insitu_python/'
plot_path='/nas/helio/data/insitu_python/plots/'
noaa_path='/nas/helio/data/noaa_rtsw/'
position_path='/nas/helio/data/insitu_python/plots_positions/'


##########################################################

#########################################################################################



#for easier debugging - do not download and process data but do everything else
get_new_data=True

#~/miniconda/envs/helio/bin/python /home/cmoestl/pycode/heliocats/sc_positions_insitu_orbit1.py
#~/miniconda/envs/helio/bin/python /home/cmoestl/pycode/heliocats/sc_positions_insitu_orbit2.py



################################# PSP

print('load PSP data') #from heliosat, converted to SCEQ similar to STEREO-A/B

filepsp='psp_2018_2019_rtn.p'
hd.save_psp_data(data_path,filepsp, sceq=False)   

filepsp='psp_2018_2019_sceq.p'
hd.save_psp_data(data_path,filepsp, sceq=True)   


################################# Wind

filewin="wind_2018_2019_gse.p" 
start=datetime.datetime(2018, 1, 1)
end=datetime.datetime(2019, 12, 31)
hd.save_wind_data(data_path,filewin,start,end,heeq=False)


filewin="wind_2018_2019_heeq.p" 
start=datetime.datetime(2018, 1, 1)
end=datetime.datetime(2019, 12, 31)
hd.save_wind_data(data_path,filewin,start,end,heeq=True)




######################################### spacecraft positions image
hp.plot_positions(datetime.datetime.utcnow(),position_path, 'HEEQ',now=True)



########################################### NOAA real time

print('download NOAA real time solar wind plasma and mag')
datestr=str(datetime.datetime.utcnow().strftime("%Y_%b_%d_%H_%M"))
print(datestr+' UTC')

plasma='http://services.swpc.noaa.gov/products/solar-wind/plasma-7-day.json'
mag='http://services.swpc.noaa.gov/products/solar-wind/mag-7-day.json'

try: urllib.request.urlretrieve(plasma, noaa_path+'plasma-7-day_'+datestr+'.json')
except urllib.error.URLError as e:
  print(' ', plasma,' ',e.reason)

try: urllib.request.urlretrieve(mag, noaa_path+'mag-7-day_'+datestr+'.json')
except urllib.error.URLError as e:
  print(' ', mag,' ',e.reason)
  
print()
print()



########################################### #SDO images now
hd.get_sdo_realtime_image()






##################### standard data update each day



#STEREO-A
filesta="sta_2020_now_beacon.p" 
start=datetime.datetime(2020, 1, 1)
end=datetime.datetime.utcnow()
if get_new_data: hd.save_stereoa_beacon_data(data_path,filesta,start,end)
[sta,hsta]=pickle.load(open(data_path+filesta, "rb" ) ) 

start=sta.time[-1]-datetime.timedelta(days=14)
end=datetime.datetime.utcnow()     
hp.plot_insitu_update(sta, start, end,'STEREO-A_beacon',plot_path,now=True)




#NOAA
filenoaa='noaa_rtsw_jan_2020_now.p'
if get_new_data: hd.save_noaa_rtsw_data(data_path,noaa_path,filenoaa)
[noaa,hnoaa]=pickle.load(open(data_path+filenoaa, "rb" ) ) 

start=noaa.time[-1]-datetime.timedelta(days=14)
end=datetime.datetime.utcnow() #noaa.time[-1]     
hp.plot_insitu_update(noaa, start, end,'NOAA_RTSW',plot_path,now=True)

start=noaa.time[-1]-datetime.timedelta(days=55)
end=datetime.datetime.utcnow() #noaa.time[-1]     
hp.plot_insitu_update(noaa, start, end,'NOAA_RTSW',plot_path,now2=True)





'''
#Wind
filewin="wind_2018_now.p" 
start=datetime.datetime(2018, 1, 1)
end=datetime.datetime.utcnow()
if get_new_data: hd.save_wind_data(data_path,filewin,start,end)
[win,hwin]=pickle.load(open(data_path+filewin, "rb" ) )  

start=win.time[-1]-datetime.timedelta(days=100)
end=datetime.datetime.utcnow()         
hp.plot_insitu(win, start, end,'Wind',plot_path,now=True)
'''

#OMNI2


fileomni="omni_1963_now.p"
overwrite=1
if get_new_data: hd.save_omni_data(data_path,fileomni,overwrite)
[o,ho]=pickle.load(open(data_path+fileomni, "rb" ) )  

start=datetime.datetime.utcnow() -datetime.timedelta(days=365)
end=datetime.datetime.utcnow() 
hp.plot_insitu_update(o, start, end,'OMNI2',plot_path,now=True)


# Chris  11:00 Uhr
# ganz simpel sind die files; monatlich magnetfeld 1 min ascii mit position 
# https://spdf.gsfc.nasa.gov/pub/data/wind/mfi/ascii/1min_ascii/
#  https://spdf.gsfc.nasa.gov/pub/data/wind/swe/ascii/2-min/




# selbiges für SWE https://spdf.gsfc.nasa.gov/pub/data/wind/swe/ascii/2-min/






# load wind data 

# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2014/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2015/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2016/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2017/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2018/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2019/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2020/*.cdf"


# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/swe/swe_h1/2018/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/swe/swe_h1/2019/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/wind/swe/swe_h1/2020/*.cdf"


# https://spdf.gsfc.nasa.gov/pub/data/wind/swe/swe_h1/{YYYY}/wi_h1_swe_{YYYY}{MM}{DD}_v[0-9]{2}.cdf"



# https://spdf.gsfc.nasa.gov/pub/data/wind/mfi/mfi_k0/2018/


# check psp probleme (evt gleich in spacecraft.json mit version nummern)



# load PSP data
# go to heliosat directory psp_fields_l2

# wget "ftps://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/mag_rtn_1min/2018/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/psp/fields/l2/mag_rtn_1min/2019/*.cdf"

# psp_spc_l2
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/psp/sweap/spc/l2/l2i/2018/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/psp/sweap/spc/l2/l2i/2019/*.cdf"



# psp_spc_l3
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/psp/sweap/spc/l3/l3i/2018/*.cdf"
# wget "ftps://spdf.gsfc.nasa.gov/pub/data/psp/sweap/spc/l3/l3i/2019/*.cdf"


# psp new orbit


# mfi h0
# https://wind.nasa.gov/mission/wind/mfi/
# swe k0
# https://wind.nasa.gov/mission/wind/swe_gsfc/swekp/
# wind testen, heeq etc. files da usw





#################### write header file for daily updates
text = open('/nas/helio/data/insitu_python/data_update_headers.txt', 'w')
text.write('Contains headers for the data files which are updated in real time.'+'\n \n')
text.write('File creation date:  '+datetime.datetime.utcnow().strftime("%Y-%b-%d %H:%M") +' \n \n')


text.write('NOAA real time solar wind: '+filenoaa+'\n \n'+ hnoaa+' \n \n')
text.write('load with: >> [noaa,hnoaa]=pickle.load(open("'+data_path+filenoaa+'", "rb"))') 
text.write(' \n \n \n \n')

text.write('STEREO-A beacon: '+filesta+'\n \n'+ hsta+' \n \n')
text.write('load with: >> [sta,hsta]=pickle.load(open("'+data_path+filesta+'", "rb"))') 
text.write(' \n \n \n \n')

text.write('Wind: '+filewin+'\n \n'+ hwin+' \n \n')
text.write('load with: >> [win,hwin]=pickle.load(open("'+data_path+filewin+'", "rb" ))') 
text.write(' \n \n \n \n')


text.write('OMNI2: '+fileomni+'\n \n'+ ho+' \n \n')
text.write('load with: >> [o,ho]=pickle.load(open("'+data_path+fileomni+'", "rb" ))') 
text.write(' \n \n \n \n')

text.close()









'''
# #STEREO-A to SCEQ
filesta2='stereoa_2015_2019_sceq.p'
start=datetime.datetime(2015, 7, 21)
end=datetime.datetime(2020, 1, 1)
hd.save_stereoa_science_data(data_path,filesta2,start,end,sceq=True)   
#[sta2,hsta2]=pickle.load(open(data_path+filesta2, "rb" ))

# #PSP to SCEQ
filepsp="psp_2018_2019_no_sceq.p"
hd.save_psp_data(data_path, filepsp,sceq=False)

# #PSP to SCEQ
filepsp="psp_2018_2019_sceq.p"
hd.save_psp_data(data_path, filepsp,sceq=True)

'''





sys.exit()







####################################

## long jobs


data_path='/nas/helio/data/insitu_python/'

'''
#################### PSP 
filepsp="psp_2018_2019_sceq.p"
hd.save_psp_data(data_path, filepsp)
[psp,hpsp]=pickle.load(open(data_path+filepsp, "rb" ) ) 

filepsp="psp_2018_2019_non_merged.p"
hd.save_psp_data_non_merged(data_path, filepsp)
[psp_orbit,psp_mag,psp_plasma,header_psp]=pickle.load(open(data_path+filepsp, "rb" ) )  

#####################
















'''


'''
filestb="stereob_2007_2014_beacon.p"
start=datetime.datetime(2007, 3, 20)
end=datetime.datetime(2014, 9, 27)
hd.save_stereob_beacon_data(data_path, filestb,start, end)
#[stb,hstb]=pickle.load(open(data_path+filestb, "rb" ) ) 

filesta2="stereoa_2007_2019_beacon.p"
start=datetime.datetime(2007, 3, 20)
end=datetime.datetime(2019, 12, 31)
hd.save_stereoa_beacon_data(data_path, filesta2,start, end)
#[sta,hsta]=pickle.load(open(data_path+filesta2, "rb" ) ) 


filewin="wind_2007_2019.p" 
start=datetime.datetime(2007, 1, 1)
end=datetime.datetime(2019, 12, 31)
hd.save_wind_data(data_path,filewin, start, end)
#[win,hwin]=pickle.load(open(data_path+filewin, "rb" ) )  



filewin2="wind_2007_2019.p" 
start=datetime.datetime(2007, 1, 1)
end=datetime.datetime(2019, 31, 12)
hd.save_wind_data(data_path,filewin2, start, end)
[win,hwin]=pickle.load(open(data_path+filewin2, "rb" ) )  


filesta2="stereoa_2007_2019_beacon.p"
start=datetime.datetime(2007, 1, 1)
end=datetime.datetime(2019, 31, 12)
hd.save_stereoa_beacon_data(data_path, filesta2,start, end)
[sta,hsta]=pickle.load(open(data_path+filesta2, "rb" ) ) 


sys.exit()



#STEREO-B science data
import importlib
import heliocats.data as hd 
importlib.reload(hd)
from config import data_path
filestb2="stereob_2013_2014.p"
start=datetime.datetime(2013, 1, 1)
end=datetime.datetime(2014, 9, 25)
hd.save_stereob_science_data(data_path, filestb2, start, end)
[stb2,header]=pickle.load(open(data_path+filestb2, "rb" ) ) 



#STEREO-A science data
import heliocats
import importlib
import heliocats.data as hd 
importlib.reload(hd)
from config import data_path
filesta2="stereoa_2015_2019.p"
start=datetime.datetime(2015, 7, 21)
end=datetime.datetime(2019, 12, 31)
hd.save_stereoa_science_data(data_path, filesta2, start, end)
[sta2,header]=pickle.load(open(data_path+filesta2, "rb" ) ) 




filemav='maven_2014_2018_removed_smoothed.p'
hd.MAVEN_smooth_orbit(data_path,filemav) 

sys.exit()


#filepsp="psp_2018_2019.p"
#hd.save_psp_data(data_path, filepsp)
#sys.exit()


sys.exit()

sys.exit()


    # save files from raw data if necessary for updates
    #hd.save_psp_data(filepsp)
    #hd.save_wind_data(filewin2)
    #hd.save_stereoa_data(filesta2)
    #hd.convert_MAVEN_mat_to_pickle() data from C. S. Wedlund
    # ADD BepiColombo  
    # ADD Solar Orbiter
    #sys.exit()


    #make a single helcats data file if necessary
    #hd.save_helcats_datacat()



filemav='maven_2014_2018.p'
hd.convert_MAVEN_mat_original(data_path,filemav) 
#[mav,hmav]=pickle.load(open(filemav, 'rb' ) )

filemav='maven_2014_2018_removed.p'
hd.convert_MAVEN_mat_removed(data_path,filemav) 
#[mav,hmav]=pickle.load(open(filemav, 'rb' ) )

filemav='maven_2014_2018_removed_smoothed.p'
hd.convert_MAVEN_mat_removed_orbit(data_path,filemav) 
#[mav,hmav]=pickle.load(open(filemav, 'rb' ) )




hd.save_psp_data(data_path, filepsp)

filepsp="psp_2018_2019.p"
data_path='/nas/helio/data/insitu_python/'
[psp,hpsp]=pickle.load(open(data_path+filepsp, "rb" ) )  

sys.exit()

hd.save_wind_data(data_path,filewin2)
hd.save_stereoa_data(data_path, filesta2)



#filemav=data_path+'maven_2014_2018_removed.p'
#[mav,hmav]=pickle.load(open(filemav, 'rb' ) )

sys.exit()


hd.save_helcats_datacat(data_path,removed=True)
hd.save_helcats_datacat(data_path,removed=False)



file='data/helios.p'
hd.save_helios_data(file)
sys.exit()

filecas='data/cassini_1999_2000.p'
hd.save_cassini_data(filecas)
sys.exit()
'''

