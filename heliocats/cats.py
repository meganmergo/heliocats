#stats.py
#catalog creation for heliocats
#https://github.com/cmoestl/heliocats

import numpy as np
import pandas as pd
import scipy
from sunpy.time import parse_time
import copy
import matplotlib.dates as mdates
import matplotlib
import seaborn as sns
import datetime
import urllib
import json
import os
import pdb
import scipy.io
import pickle
import sys
import astropy
import importlib
import cdflib
import matplotlib.pyplot as plt
import heliosat

import heliopy.data.spice as spicedata
import heliopy.spice as spice

from astropy.io.votable import parse_single_table

from config import data_path


from heliocats import data as hd
importlib.reload(hd) #reload again while debugging





################################ HI arrival catalog operations


def load_higeocat_vot(file):
    #read HIGEOCAT from https://www.helcats-fp7.eu/catalogues/wp3_cat.html
    #https://docs.astropy.org/en/stable/io/votable/
    
    

    #    "columns" : [ "ID", "Date [UTC]", "SC", "L-N", "PA-N [deg]", "L-S", "PA-S [deg]", "Quality" 
    #       , "PA-fit [deg]"
    #       , "FP Speed [kms-1]", "FP Speed Err [kms-1]", "FP Phi [deg]", "FP Phi Err [deg]","FP HEEQ Long [deg]",  "FP HEEQ Lat [deg]",  "FP Carr Long [deg]", "FP Launch [UTC]"
    #       , "SSE Speed [kms-1]", "SSE Speed Err [kms-1]", "SSE Phi [deg]", "SSE Phi Err [deg]", "SSE HEEQ Long [deg]", "SSE HEEQ Lat [deg]",  "SSE Carr Long [deg]","SSE Launch [UTC]"
    #       , "HM Speed [kms-1]", "HM Speed Err [kms-1]", "HM Phi [deg]", "HM Phi Err [deg]", "HM HEEQ Long [deg]", "HM HEEQ Lat [deg]", "HM Carr Long [deg]", "HM Launch [UTC]"
    #  ],

   
    table = parse_single_table('data/HCME_WP3_V06.vot')
    higeocat = table.array
    #higeocat['Date']=parse_time(higeocat['Date'][10]).datetime

    #access data
    #a=table.array['HM HEEQ Long'][10]
    
    return higeocat


def get_mars_position():
    
    ############### Mars position

    planet_kernel=spicedata.get_kernel('planet_trajectories')
    starttime = datetime.datetime(2007, 1, 1)
    endtime = datetime.datetime(2020, 12, 31)
    res_in_hours=1
    mars_time = []
    while starttime < endtime:
        mars_time.append(starttime)
        starttime += datetime.timedelta(hours=res_in_hours)
    mars_time_num=parse_time(mars_time)     
    mars=spice.Trajectory('4')  
    frame='HEEQ'
    mars.generate_positions(mars_time,'Sun',frame)  
    mars.change_units(astropy.units.AU)  
    [mars_r, mars_lat, mars_lon]=hd.cart2sphere(mars.x,mars.y,mars.z)
    print('mars position done') 
    
    mars_time=np.array(mars_time)
    mars_r=np.array(mars_r)
    mars_lat=np.array(mars_lat)
    mars_lon=np.array(mars_lon)

    return [mars_time,mars_r,np.degrees(mars_lat),np.degrees(mars_lon)]




def arrival_catalogue_mars(data):
    
    h=hd.load_higeocat()
    
    
    
    
    
    
    
    return 0






###################################### SIRCAT operations ################################



def load_helio4cast_sircat_master_from_excel(file):
    ''' convert excel master file to pandas dataframe and convert times
        to datetime objects
    '''
    print('load HELCATS SIRCAT from file:', file)
    sc=pd.read_excel(file)
    sc=sc.drop(columns='Unnamed: 0')

    #convert all times to datetime objects
    for i in np.arange(0,sc.shape[0]):    
        
        #remove leading and ending blank spaces if any and write datetime object into dataframe
        sc.at[i,'hss_start_time']= parse_time(str(sc.hss_start_time[i]).strip()).datetime 
        #for STEREO convert sir end time
        if sc.sc_insitu[i] != 'Wind':   sc.at[i,'sir_end_time']=parse_time(str(sc.sir_end_time[i]).strip()).datetime       
        #for STEREO convert hss end time            
        if sc.sc_insitu[i] == 'Wind':   sc.at[i,'hss_end_time']=parse_time(str(sc.hss_end_time[i]).strip()).datetime       
            
    return sc




def get_sircat_parameters(sc, sci, scat, name):
    '''
    get parameters
    sc - spacecraft data recarray
    sci - indscates for this spacecraft in scatmecat
    scat - scatmecat pandas dataframe
    '''
    fileind='sircat/indices_sircat/SIRCAT_indices_'+name+'.p'
    
    

    ################ extract indices of ICMEs in the respective data (time consuming, so do it once and save)
    
    if os.path.isfile(fileind) == False:
    
        print('extract indices of ICMEs in '+ name+ ' data')
        #### get all ICMECAT times for this spacecraft as datenum
        sc_hss_start=scat.hss_start_time[sci]
        sc_sir_end=scat.sir_end_time[sci]
        sc_hss_end=scat.hss_end_time[sci]


    
        ### arrays containing the indices of where the SIRs are in the data
        hss_start_ind=np.zeros(len(sci),dtype=int)
        sir_end_ind=np.zeros(len(sci),dtype=int)
        hss_end_ind=np.zeros(len(sci),dtype=int)

        #check where vt is less 450 km/s
        vt_lt_450=np.where(sc.vt < 450)[0]
   
        #this takes some time, get indices in data for each SIRCAT
        for i in np.arange(sci[0],sci[-1]+1):
        
            print(i-sci[0])

            
            if (name== 'STEREO-A') or (name== 'STEREO-B'):

                hss_start_ind[i-sci[0]]=np.where(sc.time > sc_hss_start[i])[0][0]-1   
                sir_end_ind[i-sci[0]]=np.where(sc.time   > sc_sir_end[i])[0][0]-1 
                
                #here the hss_end_time needs to be extracted - criteria similar to Grandin et al. 2018 
                #where stream goes back to (< 450 km/s) after sir end time
                #check the indices in the 450 array that are greater than the sir_end index and take the first one            
                hss_end_ind[i-sci[0]]=vt_lt_450[np.where(vt_lt_450 > sir_end_ind[i-sci[0]])[0][0]    ]                  
                
                #print(hss_start_ind[i-sci[0]],sir_end_ind[i-sci[0]],hss_end_ind[i-sci[0]]   )               
                                
        
            if name=='Wind':      
                
                #here only sir start and hss end exist
                hss_start_ind[i-sci[0]]=np.where(sc.time > sc_hss_start[i])[0][0]-1   
                hss_end_ind[i-sci[0]]=np.where(sc.time   > sc_hss_end[i])[0][0]-1                 
            
            

        pickle.dump([hss_start_ind,sir_end_ind,hss_end_ind], open(fileind, 'wb'))
    ############################################            
                
    [hss_start_ind,sir_end_ind,hss_end_ind]=pickle.load(open(fileind, 'rb'))           
    
    
    
    #first make hss end time for STEREO-A/B from hss_end_ind index
    
    if (name== 'STEREO-A') or (name== 'STEREO-B'):
        for i in np.arange(len(sci))-1:
            scat.at[sci[i],'hss_end_time']=sc.time[hss_end_ind[i]]


    
    
    print('Get parameters for ',name)
    
    ####### position
    
    print('position')

    #SIR heliodistance
    for i in np.arange(len(sci))-1:
        scat.at[sci[i],'sc_heliodistance']=np.round(sc.r[hss_start_ind[i]],4)
        #SIR longitude
        scat.at[sci[i],'sc_long_heeq']=np.round(sc.lon[hss_start_ind[i]],2)
        ##SIR latitude
        scat.at[sci[i],'sc_lat_heeq']=np.round(sc.lat[hss_start_ind[i]],2)


    print('hss')
    
        
    ############ HSS duration
    sci_istart=mdates.date2num(scat.hss_start_time[sci])       
    sci_hss_iend=mdates.date2num(scat.hss_end_time[sci])   
    scat.at[sci,'hss_duration']=np.round((sci_hss_iend-sci_istart)*24,2)


    for i in np.arange(0,len(sci)):        
        
        #v_max
        scat.at[sci[i],'hss_vtmax']=np.round(np.nanmax(sc.vt[hss_start_ind[i]:hss_end_ind[i]]),1)
        #vtmaxtime -search for index in sliced array and at beginning of array to see the index in the whole dataset
        scat.at[sci[i],'hss_vtmax_time']=sc.time[np.nanargmax(sc.vt[hss_start_ind[i]:hss_end_ind[i]])+hss_start_ind[i]]        
        # v_mean
        scat.at[sci[i],'hss_vtmean']=np.round(np.nanmean(sc.vt[hss_start_ind[i]:hss_end_ind[i]]),1)
        #v_bstd
        scat.at[sci[i],'hss_vtstd']=np.round(np.nanstd(sc.vt[hss_start_ind[i]:hss_end_ind[i]]),1)

        #B_max
        scat.at[sci[i],'hss_btmax']=np.round(np.nanmax(sc.bt[hss_start_ind[i]:hss_end_ind[i]]),1)
        # B_mean
        scat.at[sci[i],'hss_btmean']=np.round(np.nanmean(sc.bt[hss_start_ind[i]:hss_end_ind[i]]),1)
        #bstd
        scat.at[sci[i],'hss_btstd']=np.round(np.nanstd(sc.bt[hss_start_ind[i]:hss_end_ind[i]]),1)
        #bz
        scat.at[sci[i],'hss_bzmin']=np.round(np.nanmin(sc.bz[hss_start_ind[i]:hss_end_ind[i]]),1)
        scat.at[sci[i],'hss_bzmean']=np.round(np.nanmean(sc.bz[hss_start_ind[i]:hss_end_ind[i]]),1)
        scat.at[sci[i],'hss_bzstd']=np.round(np.nanstd(sc.bz[hss_start_ind[i]:hss_end_ind[i]]),1)
 
        
    print('sir')
    ###SIR parameters only for STEREO
    
    ############ SIR duration
    
    if (name== 'STEREO-A') or (name== 'STEREO-B'):

        sci_istart=mdates.date2num(scat.hss_start_time[sci])   
        sci_iend=mdates.date2num(scat.sir_end_time[sci])   
        scat.at[sci,'sir_duration']=np.round((sci_iend-sci_istart)*24,2)


        ########## SIR general parameters

        for i in np.arange(0,len(sci)):

            #v_max
            scat.at[sci[i],'sir_vtmax']=np.round(np.nanmax(sc.vt[hss_start_ind[i]:sir_end_ind[i]]),1)
            # v_mean
            scat.at[sci[i],'sir_vtmean']=np.round(np.nanmean(sc.vt[hss_start_ind[i]:sir_end_ind[i]]),1)
            #v_bstd
            scat.at[sci[i],'sir_vtstd']=np.round(np.nanstd(sc.vt[hss_start_ind[i]:sir_end_ind[i]]),1)

            #B_max
            scat.at[sci[i],'sir_btmax']=np.round(np.nanmax(sc.bt[hss_start_ind[i]:sir_end_ind[i]]),1)
            # B_mean
            scat.at[sci[i],'sir_btmean']=np.round(np.nanmean(sc.bt[hss_start_ind[i]:sir_end_ind[i]]),1)
            #bstd
            scat.at[sci[i],'sir_btstd']=np.round(np.nanstd(sc.bt[hss_start_ind[i]:sir_end_ind[i]]),1)
            #bz
            scat.at[sci[i],'sir_bzmin']=np.round(np.nanmin(sc.bz[hss_start_ind[i]:sir_end_ind[i]]),1)
            scat.at[sci[i],'sir_bzmean']=np.round(np.nanmean(sc.bz[hss_start_ind[i]:sir_end_ind[i]]),1)
            scat.at[sci[i],'sir_bzstd']=np.round(np.nanstd(sc.bz[hss_start_ind[i]:sir_end_ind[i]]),1)
    
    return scat





















###################################### ICMECAT operations ################################







def load_helcats_icmecat_master_from_excel(file):
    ''' convert excel master file to pandas dataframe and convert times
        to datetime objects
    '''

    print('load HELCATS ICMECAT from file:', file)
    ic=pd.read_excel(file)

    #convert all times to datetime objects
    for i in np.arange(0,ic.shape[0]):    
    
        #remove leading and ending blank spaces if any and write datetime object into dataframe
        ic.at[i,'icme_start_time']= parse_time(str(ic.icme_start_time[i]).strip()).datetime 
        ic.at[i,'mo_start_time']=parse_time(str(ic.mo_start_time[i]).strip()).datetime
        ic.at[i,'mo_end_time']=parse_time(str(ic.mo_end_time[i]).strip()).datetime
       
   
    return ic




def pdyn(density, speed):
    '''
    make dynamic pressure from density []# ccm-3] and speed [km/s]
    assume pdyn is only due to protons
    pdyn=np.zeros(len([density])) #in nano Pascals
    '''
    proton_mass=1.6726219*1e-27  #kg
    pdyn=np.multiply(np.square(speed*1e3),density)*1e6*proton_mass*1e9  #in nanoPascal

    return pdyn
    
    
def load_pickle(file):    

    ic=pickle.load( open(file, 'rb'))    
    
    return ic


def get_cat_parameters(sc, sci, ic, name):
    '''
    get parameters
    sc - spacecraft data recarray
    sci - indices for this spacecraft in icmecat
    ic - icmecat pandas dataframe
    '''
    fileind='icmecat/indices_icmecat/ICMECAT_indices_'+name+'.p'

    #### extract indices of ICMEs in the respective data (time consuming, so do it once)
    
    if os.path.isfile(fileind) == False:
    
        print('extract indices of ICMEs in '+ name+ ' data')
        #### get all ICMECAT times for this spacecraft as datenum
        sc_icme_start=ic.icme_start_time[sci]
        sc_mo_start=ic.mo_start_time[sci]
        sc_mo_end=ic.mo_end_time[sci]

    
        ### arrays containing the indices of where the ICMEs are in the data
        icme_start_ind=np.zeros(len(sci),dtype=int) 
        mo_start_ind=np.zeros(len(sci),dtype=int)
        mo_end_ind=np.zeros(len(sci),dtype=int)
   
        #this takes some time, get indices in data for each ICMECAT
        for i in np.arange(sci[0],sci[-1]+1):
        
            print(i-sci[0])

            icme_start_ind[i-sci[0]]=np.where(sc.time  > sc_icme_start[i])[0][0]-1 
            #print(icme_start_ind[i])        
            mo_start_ind[i-sci[0]]=np.where(sc.time > sc_mo_start[i])[0][0]-1   
            mo_end_ind[i-sci[0]]=np.where(sc.time   > sc_mo_end[i])[0][0]-1 

        pickle.dump([icme_start_ind, mo_start_ind,mo_end_ind], open(fileind, 'wb'))
    ############################################            
                
    [icme_start_ind, mo_start_ind,mo_end_ind]=pickle.load(open(fileind, 'rb'))           
    
    
    #plasma available?
    if name=='Wind': plasma=True
    if name=='STEREO-A': plasma=True
    if name=='STEREO-B': plasma=True
    if name=='ULYSSES': plasma=True
    if name=='MAVEN': plasma=True
    if name=='PSP': plasma=True
    if name=='VEX': plasma=False
    if name=='MESSENGER': plasma=False

    print('Get parameters for ',name)
    

    ####### position

    #MO heliodistance
    for i in np.arange(len(sci))-1:
        ic.at[sci[i],'mo_sc_heliodistance']=np.round(sc.r[mo_start_ind[i]],4)

        #MO longitude
        ic.at[sci[i],'mo_sc_long_heeq']=np.round(sc.lon[mo_start_ind[i]],2)

        #MO latitude
        ic.at[sci[i],'mo_sc_lat_heeq']=np.round(sc.lat[mo_start_ind[i]],2)


    ############ ICME    
    # ICME duration
    sci_istart=mdates.date2num(ic.icme_start_time[sci])   
    sci_iend=mdates.date2num(ic.mo_end_time[sci])   
    ic.at[sci,'icme_duration']=np.round((sci_iend-sci_istart)*24,2)
    

    for i in np.arange(0,len(sci)):
        

        #ICME B_max
        ic.at[sci[i],'icme_bmax']=np.round(np.nanmax(sc.bt[icme_start_ind[i]:mo_end_ind[i]]),1)

        #ICME B_mean
        ic.at[sci[i],'icme_bmean']=np.round(np.nanmean(sc.bt[icme_start_ind[i]:mo_end_ind[i]]),1)

        #icme_bstd
        ic.at[sci[i],'icme_bstd']=np.round(np.nanstd(sc.bt[icme_start_ind[i]:mo_end_ind[i]]),1)
        
    if plasma==True:        
        #ICME speed_mean and std
        for i in np.arange(len(sci))-1:
            ic.at[sci[i],'icme_speed_mean']=np.round(np.nanmean(sc.vt[icme_start_ind[i]:mo_end_ind[i]]),1)
            ic.at[sci[i],'icme_speed_std']=np.round(np.nanstd(sc.vt[icme_start_ind[i]:mo_end_ind[i]]),1)
    else: #set nan    
        for i in np.arange(len(sci))-1:
            ic.at[sci[i],'icme_speed_mean']=np.nan
            ic.at[sci[i],'icme_speed_std']=np.nan

        
    ########### MO
    # MO duration
    sci_istart=mdates.date2num(ic.mo_start_time[sci])   
    sci_iend=mdates.date2num(ic.mo_end_time[sci])   
    ic.at[sci,'mo_duration']=np.round((sci_iend-sci_istart)*24,2)        

    for i in np.arange(len(sci))-1:
    
        #MO B_max
        ic.at[sci[i],'mo_bmax']=np.round(np.nanmax(sc.bt[mo_start_ind[i]:mo_end_ind[i]]),1)
    
        #MO B_mean
        ic.at[sci[i],'mo_bmean']=np.round(np.nanmean(sc.bt[mo_start_ind[i]:mo_end_ind[i]]),1)
    
        #MO B_std
        ic.at[sci[i],'mo_bstd']=np.round(np.nanstd(sc.bt[mo_start_ind[i]:mo_end_ind[i]]),1)

        #MO Bz_mean
        ic.at[sci[i],'mo_bzmean']=np.round(np.nanmean(sc.bz[mo_start_ind[i]:mo_end_ind[i]]),1)

        #MO Bz_min
        ic.at[sci[i],'mo_bzmin']=np.round(np.nanmin(sc.bz[mo_start_ind[i]:mo_end_ind[i]]),1)

         #MO Bz_std
        ic.at[sci[i],'mo_bzstd']=np.round(np.nanstd(sc.bz[mo_start_ind[i]:mo_end_ind[i]]),1)

        #MO By_mean
        ic.at[sci[i],'mo_bymean']=np.round(np.nanmean(sc.by[mo_start_ind[i]:mo_end_ind[i]]),1)

        #MO By_std
        ic.at[sci[i],'mo_bystd']=np.round(np.nanstd(sc.by[mo_start_ind[i]:mo_end_ind[i]]),1)

    
    if plasma==True:   
         
        for i in np.arange(len(sci))-1:
        
            #mo speed_mean and std
            ic.at[sci[i],'mo_speed_mean']=np.round(np.nanmean(sc.vt[mo_start_ind[i]:mo_end_ind[i]]),1)
            ic.at[sci[i],'mo_speed_std']=np.round(np.nanstd(sc.vt[mo_start_ind[i]:mo_end_ind[i]]),1)
            
            ic.at[sci[i],'mo_expansion_speed']=np.round( (sc.vt[mo_start_ind[i]]-sc.vt[mo_end_ind[i]])/2 ,1 )

            ic.at[sci[i],'mo_density_mean']=np.round(np.nanmean(sc.np[mo_start_ind[i]:mo_end_ind[i]]),1)
            ic.at[sci[i],'mo_density_std']=np.round(np.nanstd(sc.np[mo_start_ind[i]:mo_end_ind[i]]),1)

            ic.at[sci[i],'mo_temperature_mean']=np.round(np.nanmean(sc.tp[mo_start_ind[i]:mo_end_ind[i]]),1)
            ic.at[sci[i],'mo_temperature_std']=np.round(np.nanstd(sc.tp[mo_start_ind[i]:mo_end_ind[i]]),1)

            pdyn_i=pdyn(sc.np[mo_start_ind[i]:mo_end_ind[i]],sc.vt[mo_start_ind[i]:mo_end_ind[i]])
            
            ic.at[sci[i],'mo_pdyn_mean']=np.round(np.nanmean(pdyn_i),1)
            ic.at[sci[i],'mo_pdyn_std']=np.round(np.nanstd(pdyn_i),1)
            
            
            #icme speed_mean and std
            ic.at[sci[i],'sheath_speed_mean']=np.round(np.nanmean(sc.vt[icme_start_ind[i]:mo_start_ind[i]]),1)
            ic.at[sci[i],'sheath_speed_std']=np.round(np.nanstd(sc.vt[icme_start_ind[i]:mo_start_ind[i]]),1)         

            ic.at[sci[i],'sheath_density_mean']=np.round(np.nanmean(sc.np[icme_start_ind[i]:mo_start_ind[i]]),1)
            ic.at[sci[i],'sheath_density_std']=np.round(np.nanstd(sc.np[icme_start_ind[i]:mo_start_ind[i]]),1)        

            pdyn_i=pdyn(sc.np[icme_start_ind[i]:mo_start_ind[i]],sc.vt[icme_start_ind[i]:mo_start_ind[i]])

            ic.at[sci[i],'sheath_pdyn_mean']=np.round(np.nanmean(pdyn_i),1)
            ic.at[sci[i],'sheath_pdyn_std']=np.round(np.nanstd(pdyn_i),1)

            
            
    else: #set nan    
    
        for i in np.arange(len(sci))-1:
            ic.at[sci[i],'mo_speed_mean']=np.nan
            ic.at[sci[i],'mo_speed_std']=np.nan
            
            ic.at[sci[i],'mo_expansion_speed']=np.nan
    
            ic.at[sci[i],'mo_density_mean']=np.nan
            ic.at[sci[i],'mo_density_std']=np.nan
    
            ic.at[sci[i],'mo_temperature_mean']=np.nan
            ic.at[sci[i],'mo_temperature_std']=np.nan
            
            ic.at[sci[i],'mo_pdyn_mean']=np.nan
            ic.at[sci[i],'mo_pdyn_std']=np.nan

            ic.at[sci[i],'sheath_pdyn_mean']=np.nan
            ic.at[sci[i],'sheath_pdyn_std']=np.nan

    
    return ic


