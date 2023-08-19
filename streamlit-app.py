import json

import streamlit as st
import pandas as pd
import pydeck as pdk

ASSUMPTIONS = {
    'kg/co2': [100],
    'kg/km': [100],
}

st.set_page_config(layout="wide")

def load_json(filename: str):
    with open(filename) as f:
        return json.load(f)
    
def map_score_to_line_thickness(score: float, score_type: str) -> int:

    limits_dict = {
        'tonne.km/hr': (0, 1000),
        'gco2/tonne.km': (2, 1000),
        'n_stopovers': (3, 1000),
        'km/h': (0, 2000),
    }

    if score_type not in limits_dict.keys():
        raise Exception("Invalid score type")    

    LOWER_LIMIT, UPPER_LIMIT = limits_dict[score_type]

    return score / (UPPER_LIMIT - LOWER_LIMIT)

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
    return load_json('./data/simplified/rail_map_simplified.geojson')
    
@st.cache_data
def load_nltn_road_data():
    return load_json('./data/simplified/nltn_road_simplified.geojson')

@st.cache_data
def load_key_rail_freight_route():
    return load_json('./data/simplified/key_rail_freight_route_simplified.geojson')
    
@st.cache_data
def load_key_road_freight_route():
    return load_json('./data/simplified/key_road_freight_route_simplified.geojson')
    
df = collect_data()

st.title("🚀 Australia's Shift to H2 Freight")
st.divider()

#%% Section 2: Metrics

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(label="Metric A", value="12345", delta="5")
c2.metric(label="Metric B", value="12345", delta="-5")
c3.metric(label="Metric C", value="12345", delta="25")
c4.metric(label="Metric D", value="12345", delta="-25")
c5.metric(label="Metric E", value="12345", delta="100")
st.divider()

#%% Section 3 - Maps and Config
# Use columns to create layout
col1, col2 = st.columns([3, 2], gap='large')  # Adjust the column widths as needed

# Display the Pydeck map in the first column
target_layer_names = col1.multiselect(
    label='What layers would you like to show', 
    options=['Air', 'Roads (Local)', 'Roads (Interstate)', 'Rail'], 
    default=['Air', 'Roads (Local)', 'Rail'],
)

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
        visible='Rail' in target_layer_names,
    ),
    pdk.Layer(
        type="GeoJsonLayer",
        data=load_key_road_freight_route(),
        get_line_color=[255, 0, 0],
        line_width_min_pixels=1,
        visible='Roads (Interstate)' in target_layer_names,
    ),
    pdk.Layer(
        type="GeoJsonLayer",
        data=load_nltn_road_data(),
        get_line_color=[0, 0, 255],
        line_width_min_pixels=1,
        visible='Roads (Local)' in target_layer_names,
    ),
]

# Create a Pydeck map
map_layer = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=initial_view,
    layers=layers
)

col1.pydeck_chart(map_layer)

# Display the slider values in the second column
with col2:
    st.write("# Config.")
    t1, t2, t3 = st.tabs(['Hydrogen Power', 'Freight Network Distribution', 'Commodity Demand'])
    t1.write('#### What proportion of our fleet is H2 powered?')
    air_slider = t1.slider(" ✈️ Air", 0, 100, 50)
    land_slider = t1.slider("🚚 Land", 0, 100, 50)
    rail_slider = t1.slider("🚅 Rail", 0, 100, 50)

#%% Section 4: Generative AI 
st.write('# Generative AI: Interrogate the data')
st.divider()
question = st.text_input("Ask a question about the data")

#%% Assumptions
with st.expander("ASSUMPTIONS"):
    st.write(ASSUMPTIONS)