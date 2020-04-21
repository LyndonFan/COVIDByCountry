import folium
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from folium.plugins import *
from folium.features import *

import requests

BASE_URL = "https://data.humdata.org/hxlproxy/api/data-preview.csv?url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2F"

def preprocess(df):
    print("> Preprocessing...")
    df_temp = df[(df["Lat"]!=0) & (df["Long"]!=0)]
    df_temp.sort_values(by="4/15/20",axis=0,ascending = False,inplace=True)
    return df_temp

def create_geojson_features(df,term,clr):
    features = []
    print('> Creating GeoJSON features...')
    dates = list(df.columns)[4:]
    for i in range(df.shape[0]):
        name = (df.iloc[i,0] + ", ") if type(df.iloc[i,0])==str else ""
        name += df.iloc[i,1]
        for j in range(4,df.shape[1]):
            newcases = df.iloc[i,j] - df.iloc[i,j-1] if j>4 else df.iloc[i,j]
            if df.iloc[i,j]>0:
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type':'Point', 
                        'coordinates':[float(df.iloc[i,3]),float(df.iloc[i,2])]
                    },
                    'properties': {
                        'time': dates[j-4],
                        'style': {"opacity":0},
                        'icon': 'circle',
                        #"opacity": 0.2,
                        'iconstyle':{
                            'fillColor': clr,
                            #'fillOpacity': 0.2,
                            'stroke': 'false',
                            'radius': int(np.power(df.iloc[i,j],0.25)*2)
                        },
                        "popup": name+":<br>"+str(newcases)+" new "+term+"<br>"+str(df.iloc[i,j])+" culmulative",
                        "highlight": True 
                    },
                }
                features.append(feature)
    return features

def add_to_map(features,mp):   
    TimestampedGeoJson(
        {'type': 'FeatureCollection',
        'features': features}
        , period='P1D'
        , add_last_point=True
        , auto_play=False
        , loop=False
        , max_speed=24
        , transition_time = 1000/12
        , loop_button=True
        , date_options='DD/MM/YYYY'
        , time_slider_drag_update=True
        , duration = "P0D"
    ).add_to(mp)
    folium.TileLayer(opacity=0.2).add_to(mp)
    return mp

def get_map(df,term,clr):
    
    df_processed = preprocess(df)
    '''
    df_deaths_processed = preprocess(df_deaths)
    #df_recovered_processed = preprocess(df_recovered)
    '''
    features = create_geojson_features(df_processed,term,clr)
    print('> Making map...')
    cases_map = folium.Map(location=[0,0], control_scale=True, zoom_start=1.5)
    print(type(cases_map))
    add_to_map(features,cases_map)
    print(type(cases_map))
    print('> Done.')
    return cases_map

if __name__ == "__main__":
    df_cases_raw = pd.read_csv(BASE_URL+"{0}&filename={0}".format("time_series_covid19_confirmed_global.csv"))
    df_deaths_raw = pd.read_csv(BASE_URL+"{0}&filename={0}".format("time_series_covid19_deaths_global.csv"))
    df_recovered_raw = pd.read_csv(BASE_URL+"{0}&filename={0}".format("time_series_covid19_recovered_global.csv"))
    res = get_map(df_cases_raw,"cases","#ff0000")
    res.save("COVID-19_cases_over_time.html")
    res_deaths = get_map(df_deaths_raw,"deaths","#000000")
    res_deaths.save("COVID-19_deaths_over_time.html")
    res_recovered = get_map(df_recovered_raw,"recovered","#008800")
    res_recovered.save("COVID-19_recovered_over_time.html")
