# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 00:39:05 2022


@author: User
"""


import streamlit as st
import pandas as pd
import requests
import json
import os 
import time
import plotly.graph_objects as go
import plotly.io as pio



st.set_page_config(
    page_title="NFL All Day - Preseason",
    page_icon=":football:",
    layout="wide",
    menu_items=dict(About="It's a work of Kurama"),
)


st.image(
    "https://wwwimage-us.pplusstatic.com/base/files/blog/nflquizheaderimage.jpeg",
    use_column_width=True,
)
st.title(":football: NFL All Day :football:")


st.success("This app only contains a chart! Please select a start date and end date for the slider to configure, and then select the day you want to check :) ")
st.markdown('Hi there, the template used here is by joker#2418, cheers to him!' )   

st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        max-width: 90%;
        padding-top: 5rem;
        padding-right: 5rem;
        padding-left: 5rem;
        padding-bottom: 5rem;
    }}
    img{{
    	max-width:40%;
    	margin-bottom:40px;
    }}
</style>
""",
        unsafe_allow_html=True,
    ) 
pio.renderers.default = 'browser'

  
API_KEY = "3b5afbf4-3004-433c-9b04-2e867026718b"

 
 
teams = ['Green Bay Packers','Indianapolis Colts','Cleveland Browns','Arizona Cardinals','Philadelphia Eagles','Phoenix Cardinals','Los Angeles Raiders','Houston Texans','New York Giants','Minnesota Vikings','Dallas Cowboys','New Orleans Saints','New England Patriots','Oakland Raiders','Denver Broncos','Jacksonville Jaguars','Los Angeles Chargers','Seattle Seahawks','Las Vegas Raiders','New York Jets','Tennessee Oilers','Detroit Lions','Los Angeles Rams','Miami Dolphins','Buffalo Bills','Washington Football Team','Cincinnati Bengals','Kansas City Chiefs','San Francisco 49ers','Tennessee Titans','Atlanta Falcons','Baltimore Ravens','St. Louis Rams','Tampa Bay Buccaneers','Chicago Bears','Pittsburgh Steelers','Carolina Panthers']       
latitude = [44.513332,39.791000,41.505493,33.448376,39.952583,33.448376,34.052235,29.749907,40.73061,44.986656,32.779167,29.951065,42.361145,36.114647,39.742043,30.332184,34.052235,47.608013,36.114647,40.73061,36.174465,42.331429,34.052235,25.761681,42.88023,38.900497,39.103119,39.099724,37.773972,36.174465,33.753746,39.299236,38.627003,27.964157,41.881832,40.440624,35.227085]
longitude = [-88.015831,-86.148003,-81.68129,-112.074036,-75.165222,-112.074036,-118.243683,-95.358421,-73.935242,-93.258133,-96.808891,-90.071533,-71.057083,-115.172813,-104.991531,-81.655647,-118.243683,-122.335167,-115.172813,-73.935242,-86.76796,-83.045753,-118.243683,-80.191788,-78.878738,-77.007507,-84.512016,-94.578331,-122.431297,-86.76796,-84.38633,-76.609383,-90.199402,-82.452606,-87.623177,-79.995888,-80.843124]

data = {'TEAM':teams, 'Lat':latitude, 'Lon':longitude}
df = pd.DataFrame(data)
 
  
TTL_MINUTES = 15
PAGE_SIZE = 100000
PAGE_NUMBER = 1

def create_query():
    r = requests.post(
        'https://node-api.flipsidecrypto.com/queries', 
        data=json.dumps({
            "sql": SQL_QUERY,
            "ttlMinutes": TTL_MINUTES
        }),
        headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
    )
    if r.status_code != 200:
        raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))
    
    return json.loads(r.text)    
 


def get_query_results(token):
    r = requests.get(
        'https://node-api.flipsidecrypto.com/queries/{token}?pageNumber={page_number}&pageSize={page_size}'.format(
          token=token,
          page_number=PAGE_NUMBER,
          page_size=PAGE_SIZE
        ),
        headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY}
    )
    if r.status_code != 200:
        raise Exception("Error getting query results, got response: " + r.text + "with status code: " + str(r.status_code))
    
    data = json.loads(r.text)
    if data['status'] == 'running':
        time.sleep(10)
        return get_query_results(token)

    return data



with st.container():

    
    start_date = st.date_input("Enter the starting date")
    end_date = st.date_input("Enter the ending date")
    select_day = st.slider("Select date",value = start_date, min_value=start_date, max_value=end_date, format="YYYY/MM/DD")
 

    
    SQL_QUERY_AUX = "select to_date(A.block_timestamp) as date, b.team, sum(a.price) as amount_team from flow.core.ez_nft_sales a left join flow.core.dim_allday_metadata b on a.nft_id = b.nft_id where A.nft_collection = 'A.e4cf4bdc1751c65d.AllDay' and to_date(A.block_timestamp) = '"

    
    SQL_QUERY = SQL_QUERY_AUX+ str(select_day)[:10] + "' and b.team is not null group by date, b.team" 
    
  
    query = create_query()
    token = query.get('token')
    data1 = get_query_results(token)
    df1 = pd.DataFrame(data1['results'], columns = ['DATE','TEAM','AMOUNT_TEAM'])
        
    df2 = df.merge(df1, on='TEAM', how='left')
    
     
    df2['text'] = df2['TEAM'] + '<br>Amount ' + (df2['AMOUNT_TEAM']).astype(str)
    limits = [(0,1000),(1000,5000),(5000,10000),(10000,30000),(30000,100000),(100000,300000)]
    colors = ["#F5B10C","#EDCABE","#E9B666","#BFD0CA","#A5B2B5","#0F4C81"]
    df2 = df2.fillna(0)
    
    fig = go.Figure()
         
    for i in range(len(limits)):  
        lim = limits[i] 
        df_sub = df2[lim[0]:lim[1]]   
        df_sub2 = df2[(df2['AMOUNT_TEAM'] >= lim[0]) &(df2['AMOUNT_TEAM'] <= lim[1]) ]  
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lon = df_sub2['Lon'],
            lat = df_sub2['Lat'],
            text = df_sub2['text'], 
            marker = dict(
                    size = df_sub2['AMOUNT_TEAM'],
                    color = colors[i],
                    line_color='rgb(40,40,40)',
                    line_width=0.5,
                    sizemode = 'area'
                ),
                name = '{0} - {1}'.format(lim[0],lim[1])
                ))
         
    fig.update_layout(
                title_text = '2022.09.01 - Total Sales in a single day by City',
                showlegend = True,
                geo = dict(
                    scope = 'usa',
                    landcolor = 'rgb(160, 160, 160)',
                ),width=1000, height=1000
            )
        
    st.plotly_chart(fig, use_container_width=True) 
 