import streamlit as st
import pandas as pd
from shapely.wkt import loads

import streamlit as st
import pydeck as pdk
import geopandas as gpd


st.set_page_config(layout="wide")

#TODO: Initialise datasets from DuckDB here 
@st.cache_data
def collect_data() -> pd.DataFrame:
    df = pd.read_csv("data/raw/congestion_2020/geometries_2020.csv").set_index('route_name')
    return df

df = collect_data()

# Create Shapely linestrings (replace this with your actual data) - example: [(lon1, lat1), (lon2, lat2), ...]
str_to_linstr = lambda linstr: [[cord.split(" ")[1], cord.split(" ")[0]] for cord in linstr.strip('LINESTRING (').strip(')').split(", ")]
linestrings = df['route_geom'].apply(loads)

st.title("🚀 Australia's Shift to H2 Freight")
st.divider()
current_year = st.slider("Year Range", 1990, 2050, (2023))
st.divider()

# Create a GeoDataFrame from the linestrings
# gdf = gpd.GeoDataFrame(geometry=df['route_geom'].apply(str_to_linstr).apply(lambda x: 'LINESTRING (' + ', '.join([' '.join(y) for y in x]) + ')').apply(loads))
gdf = gpd.GeoDataFrame(geometry=linestrings)


# Define the initial view state centered on Australia
initial_view = pdk.ViewState(
    latitude=-25.2744,
    longitude=133.7751,
    zoom=3
)

# Create a Pydeck map
map_layer = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=initial_view,
    layers=[]
)

# Use columns to create layout
col1, col2 = st.columns([3, 2], gap='large')  # Adjust the column widths as needed



# Display the Pydeck map in the first column

col1.pydeck_chart(map_layer)

# Display the slider values in the second column
with col2:
    # Sliders for different modes of transportation
    st.write('## Fleet powered by H2 (%)')
    air_slider = st.slider(" ✈️ Air", 0, 100, 50)
    sea_slider = st.slider("🚢 Sea", 0, 100, 50)
    land_slider = st.slider("🚚 Land", 0, 100, 50)
    rail_slider = st.slider("🚅 Rail", 0, 100, 50)

#%% Section 3: Metrics
st.write("# Cool Metrics")
st.divider()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(label="Metric A", value="12345", delta="5")
c2.metric(label="Metric B", value="12345", delta="-5")
c3.metric(label="Metric C", value="12345", delta="25")
c4.metric(label="Metric D", value="12345", delta="-25")
c5.metric(label="Metric E", value="12345", delta="100")

#%% Section 4: Generative AI 
st.write('# Generative AI: Interrogate the data')
st.divider()
question = st.text_input("Ask a question about the data")
