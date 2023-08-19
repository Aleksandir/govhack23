import json

import streamlit as st
import pandas as pd
import pydeck as pdk


st.set_page_config(layout="wide")

#TODO: Initialise datasets from DuckDB here 
@st.cache_data
def collect_data() -> pd.DataFrame:
    df = pd.read_csv("data/raw/congestion_2020/geometries_2020.csv").set_index('route_name')
    str_to_linstr = lambda linstr: [[cord.split(" ")[1], cord.split(" ")[0]] for cord in linstr.strip('LINESTRING (').strip(')').split(", ")]

    df['path'] = df['route_geom'].apply(str_to_linstr)
    df['name'] = df.index
    df['color'] = [(250, 166, 26)]*len(df.index)

    df = df.reset_index()[['name', 'color', 'path']]
    df["path"] = df["path"].apply(lambda path: [x[::-1] for x in path])
    return df

@st.cache_data
def load_rail_geojson():
    with open('./data/raw/rail_map.geojson') as f:
        return json.load(f)
    
@st.cache_data
def load_nltn_road_data() -> pd.DataFrame:
    with open('./data/raw/nltn_road.geojson') as f:
        return json.load(f)

@st.cache_data
def load_key_rail_freight_route() -> pd.DataFrame:
    with open('./data/raw/key_rail_freight_route.geojson') as f:
        return json.load(f)
    
@st.cache_data
def load_key_road_freight_route() -> pd.DataFrame:
    with open('./data/raw/key_road_freight_route.geojson') as f:
        return json.load(f)
    

df = collect_data()

st.title("🚀 Australia's Shift to H2 Freight")
st.divider()
current_year = st.slider("Year Range", 1990, 2050, (2023))
st.divider()

# Define the initial view state centered on Australia
initial_view = pdk.ViewState(
    latitude=-25.2744,
    longitude=133.7751,
    zoom=3
)

layers = [
    pdk.Layer(
        type="PathLayer",
        data=df,
        pickable=True,
        get_color="color",
        width_scale=20,
        width_min_pixels=2,
        get_path="path",
        get_width=3,
    ),
    pdk.Layer(
        type="GeoJsonLayer",
        data=load_rail_geojson(),
        get_line_color=[125, 140, 0],
        line_width_min_pixels=1,
    ),
    pdk.Layer(
        type="GeoJsonLayer",
        data=load_key_rail_freight_route(),
        get_line_color=[0, 255, 0],
        line_width_min_pixels=1,
    ),
    pdk.Layer(
        type="GeoJsonLayer",
        data=load_key_road_freight_route(),
        get_line_color=[255, 0, 0],
        line_width_min_pixels=1,
    ),
    pdk.Layer(
        type="GeoJsonLayer",
        data=load_nltn_road_data(),
        get_line_color=[0, 0, 255],
        line_width_min_pixels=1,
    ),
]

# Create a Pydeck map
map_layer = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=initial_view,
    layers=layers
)

# Use columns to create layout
col1, col2 = st.columns([3, 2], gap='large')  # Adjust the column widths as needed



# Display the Pydeck map in the first column
layer_options = col1.multiselect(
    label='What layers would you like to show', 
    options=['Air', 'Roads (Local)', 'Roads (Interstate)', 'Rail'], 
    default=['Air', 'Roads (Local)', 'Rail'],
)

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
