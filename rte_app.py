from typing import Any, Dict
import time
from datetime import datetime, timedelta
import requests
import streamlit as st
import pandas as pd
from pandas.io.json import json_normalize
import plotly.express as px

# URL pour get le token OAuth2
OAUTH_URL = "https://digital.iservices.rte-france.com/token/oauth"

# Cliend ID et secret en base 64
OAUTH_B64 = "ZjM0ODI4ZmItOTJlYS00NzgzLTg1NGEtZDJiY2QzMjgyMDBhOjBhMTk1Y2RhLTQ2OTAtNGY4OS05NDk0LTQ5NDgxNGFlMzk0ZA=="


# constant of C02 emmisions T/MWh
COAL = 0.986
OIL = 0.777
GAS = 0.429
WASTE = 0.494
NUCLEAR = 0.012
WIND = 0.011
SOLAR = 0.041

# function to adapt the date to the rte api
def roundTime(dt=None, roundTo=60):
   """Round a datetime object to any time lapse in seconds
   dt : datetime.datetime object, default now.
   roundTo : Closest number of seconds to round to, default 1 minute.
   Author: Thierry Husson 2012 - Use it as you want but don't blame me.
   """
   if dt == None : dt = datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + timedelta(0,rounding-seconds,-dt.microsecond)

# get the identification token
def get_token() -> Dict[str, str]:
    """Get an Oauth token"""
    response = requests.post(OAUTH_URL, headers={"Authorization": f"Basic {OAUTH_B64}"})
    return response.json()

# get the data from the api for the last 7 days 
def get_data(url: str, token: str) -> Dict[str, Any]:
    now = roundTime()
    delta = timedelta(days=-7)
    seven_days_ago = (now + delta).isoformat() + "%2B02:00"
    now = now.isoformat() + "%2B02:00"
    url = url + "?start_date="+seven_days_ago+"&end_date="+now
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    return response.json()

# consume api
def consume_api():

    token_data = get_token()
    token = token_data["access_token"]
    data = get_data(
        "https://digital.iservices.rte-france.com/open_api/actual_generation/v1/actual_generations_per_production_type",
        token,
    )
    return data

# build the dataframe from the json file download from rte API
def build_dataframe(body):
    biomass = json_normalize(body["actual_generations_per_production_type"][0]["values"])["value"]
    fossil_gas = json_normalize(body["actual_generations_per_production_type"][1]["values"])["value"]
    fossil_hard_coal = json_normalize(body["actual_generations_per_production_type"][2]["values"])["value"]
    fossil_oil = json_normalize(body["actual_generations_per_production_type"][3]["values"])["value"]
    nuclear = json_normalize(body["actual_generations_per_production_type"][7]["values"])["value"]
    solar = json_normalize(body["actual_generations_per_production_type"][8]["values"])["value"]
    waste = json_normalize(body["actual_generations_per_production_type"][9]["values"])["value"]
    wind_onshore = json_normalize(body["actual_generations_per_production_type"][10]["values"])
    dates = wind_onshore["updated_date"]
    wind_onshore = wind_onshore["value"]
    
    # convert json into dataframe
    df = pd.DataFrame([biomass, fossil_gas, fossil_hard_coal, fossil_oil, nuclear, solar, waste, wind_onshore]).T
    df.columns = ["biomass", "fossil_gas", "fossil_hard_coal", "fossil_oil", "nuclear", "solar", "waste", "wind_onshore"]
    df.index = dates
    # calculate the intensity carbon of production (we do not take into account building emmissions)
    intensite_carbone = (df["biomass"]*WASTE*(10**6) + df["fossil_gas"]*GAS*(10**6) + df["fossil_hard_coal"]*COAL*(10**6) + df["fossil_oil"]*OIL*(10**6) 
                    + df["waste"]*WASTE*(10**6))
    return intensite_carbone, df


# here we loop every 5 minutes to reload the data (rte change its data every hours, 15 minutes just in case
# the user is between the end and the beginning of the new hour
while True:     
    
    # choose "paysage" format for the single web page
    st.set_page_config(layout="wide")  
    
    # get the data and build a clear dataframe
    body = consume_api()
    intensite_carbone, df = build_dataframe(body)
    average = intensite_carbone.mean()
    last = intensite_carbone[-1]
    
    # build figure for the carbon intensity
    fig1 = px.line(intensite_carbone, width = 1000, height=400, title="Grams of CO2 per MWh", 
                  labels={"updated_date":"date", "value":"Cabon intensity"})
    
    # build figures for the split of production
    fig2 = px.line(df, width = 1000, height=400, title="Levels of Production in KWh", 
                  labels={"updated_date":"date", "value":"Production"})
    
    # make the charts
    chart1 = st.write(fig1)
    chart2 = st.write(fig2)
    st.metric(label="carbon intensity in Grams/CO2", value=str(last), delta=str(last-average))
    time.sleep(300)





