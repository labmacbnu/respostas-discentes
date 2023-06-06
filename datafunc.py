import streamlit as st 
import requests
import pandas as pd
import json

# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

@st.cache_data
def dados_df()-> pd.DataFrame:
    return load_data(st.secrets["respostas_url"])


@st.cache_data
def escolas_df()-> pd.DataFrame:
    df = load_data(st.secrets["escolas_geoloc"]) 
    t2num = lambda x: float(x.replace(',','.'))
    df.dropna(subset="lat", inplace=True)
    df.loc[:,['lat', 'long']] = df[['lat', 'long']].applymap(t2num)
    return df


@st.cache_data
def cidades_df()-> pd.DataFrame:
    return load_data(st.secrets["cidades"])

@st.cache_data
def geojson() -> dict:
    pedido = requests.get('https://raw.githubusercontent.com/LFBossa/MapaSaudeSC/main/data/geoloc/boundaries-simplified.json')
    BOUNDARIES = pedido.json()
    return BOUNDARIES

 