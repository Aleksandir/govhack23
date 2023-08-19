import streamlit as st
import pandas as pd
from shapely.wkt import loads

st.title('GovHack 2023')

df = pd.read_csv('data/raw/congestion_2020/geometries_2020.csv')
ls = loads(df.route_geom[0])

st.dataframe(df, use_container_width=True)
st.map(ls)