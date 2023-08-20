
import json
import numpy as np
import pandas as pd
import plotly.express as px
import pydeck as pdk
import streamlit as st
from pandasai import SmartDatalake
from pandasai.llm import OpenAI

st.set_page_config(layout="wide")
from pages.Assumptions import ASSUMPTIONS

def load_json(filename: str):
    with open(filename) as f:
        return json.load(f)


def calculate_metric(score: float, score_type: str, hydrogen_uptake_percentage: int) -> float:
    
    LIMITS = {
        'tonne.km/hr': (0, 1000),
        'gco2/tonne.km': (1, 1000),
        'km/h': (2, 1000),
    }

    if score_type not in LIMITS.keys():
        raise Exception("Invalid score type")    

    # Adjust for hydrogen uptake 
    HYDROGEN_FACTOR = 200
    score += (hydrogen_uptake_percentage * HYDROGEN_FACTOR)

    # Normalise metric between upper and lower limits
    LOWER_LIMIT, UPPER_LIMIT = LIMITS[score_type]
    normalised_score =  np.clip(score - LOWER_LIMIT, 0, UPPER_LIMIT) / (UPPER_LIMIT - LOWER_LIMIT)

    return normalised_score


def calculate_freight_network_score(metric_list: list[float]) -> float:

    if len(metric_list) < 1:
        raise Exception("Empty metric list: no metrics to calculate")

    return np.mean(metric_list)
     

def map_score_to_color(normalised_score: float) -> list[int]:

    red = int((1 - normalised_score) * 255)
    green = int(normalised_score * 255)

    return [red, green, 0]


def get_network_color(network_type: str, hydrogen_uptake_percentage: int) -> list[int]:

    score_1 = calculate_metric(score=float(ASSUMPTIONS['tonne.km/hr'][network_type]), score_type='tonne.km/hr', hydrogen_uptake_percentage=hydrogen_uptake_percentage)
    score_2 = calculate_metric(score=float(ASSUMPTIONS['gco2/tonne.mk'][network_type]), score_type='gco2/tonne.km', hydrogen_uptake_percentage=hydrogen_uptake_percentage)

    network_score = calculate_freight_network_score(metric_list=[score_1, score_2])
    rgb_value_list = map_score_to_color(normalised_score=network_score)

    return rgb_value_list


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

@st.cache_data
def airport_data():
    return pd.read_json("data/raw/airport_coordinates.json")

@st.cache_data
def metric_tonne_km_data():
    return pd.read_json('data/raw/metric_tonnekm.json')

@st.cache_data
def hydrogen_emission_data():
    return pd.read_json("data/raw/hydrogen_emission_pct.json")
    
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
col1, col2 = st.columns([3, 2], gap='medium')  # Adjust the column widths as needed

# Display the Pydeck map in the first column
target_layer_names = col1.multiselect(
    label='What layers would you like to show', 
    options=['Air', 'Roads (Local)', 'Roads (Interstate)', 'Rail', 'Roads (NLTN)'], 
    default=['Air', 'Roads (Local)', 'Rail'],
)

airport_df = airport_data()
selected_airport = col1.selectbox("Select Airport", list(airport_df["from_name"].unique()) + ["None"])


# Define the initial view state centered on Australia
initial_view = pdk.ViewState(
    latitude=-25.2744,
    longitude=133.7751,
    zoom=3,
    pitch=45,
    bearing=0,
)


# Display the slider values in the second column
with col2:
    t1, t2, t3, t4 = st.tabs(['Hydrogen Adoption', 'Hydrogen Generation', 'Fleet Demand', 'Commodity Demand'])
    t1.write('###### The percentage of the fleet that is hydrogen powered')
    t1_year = t1.selectbox('Year', ('2016', '2036', '2056'), key='t1_year')
    if t1_year == '2016':
        t1_slider_values = (0, 0, 0, 0, 0, 0)
    if t1_year == '2036':
        t1_slider_values = (0, 0, 0, 0, 0, 0)
    if t1_year == '2056':
        t1_slider_values = (0, 0, 0, 0, 0, 0)
    t1_air_slider = t1.slider("✈️ Air", 0, 100, t1_slider_values[0], format="%d%%")
    t1_rail_slider = t1.slider("🚅 Rail", 0, 100, t1_slider_values[1], format="%d%%")
    t1_haul_truck_slider = t1.slider("🚚 Long-haul Truck", 0, 100, t1_slider_values[2], format="%d%%")
    t1_urban_truck_slider = t1.slider("🚚 Urban Delivery", 0, 100, t1_slider_values[3], format="%d%%")

    t2.write('###### Hydrogen generated by source')
    t2_year = t2.selectbox('Year', ('2023', '2036', '2056'), key='t2_year')
    if t2_year == '2023':
        t2_slider_values = (23, 76, 2, 0)
    if t2_year == '2036':
        t2_slider_values = (0, 0, 0, 0)
    if t2_year == '2056':
        t2_slider_values = (0, 0, 0, 0)
    t2_a, t2_b = t2.columns([2, 3])
    t2_labels = ('Fossil Fuels', 'Natural Gas', 'Electrolysis', 'Biomass and Capture')
    t2_slider_fossil_fuels = t2_a.slider(t2_labels[0], 0, 100, t2_slider_values[0], format="")
    t2_slider_gas = t2_a.slider(t2_labels[1], 0, 100, t2_slider_values[1], format="")
    t2_slider_electrolysis = t2_a.slider(t2_labels[2], 0, 100, t2_slider_values[2], format="")
    t2_slider_biomass = t2_a.slider(t2_labels[3], 0, 100, t2_slider_values[3], format="")
    sizes = [t2_slider_fossil_fuels, t2_slider_gas, t2_slider_electrolysis, t2_slider_biomass]
    sizes_total = max(sum(sizes), 1)
    sizes_norm = [s/sizes_total for s in sizes]
    fig = px.pie(df, values=sizes_norm, names=t2_labels, hole=0.3)
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=0), showlegend=False)
    t2_b.plotly_chart(fig, use_container_width=True)

    t3.write('###### Predicted increase in vehicle demand')
    t3_year = t3.selectbox('Year', ('2016', '2036', '2056'), key='t3_year')
    if t3_year == '2016':
        t3_slider_values = (0, 0, 0, 0, 0, 0)
    if t3_year == '2036':
        t3_slider_values = (0, 0, 0, 0, 0, 0)
    if t3_year == '2056':
        t3_slider_values = (0, 0, 0, 0, 0, 0)
    t3_air_slider = t3.slider("✈️ Air", 0, 100, t3_slider_values[0], format="%d%%", key='t3_air_slider')
    t3_rail_slider = t3.slider("🚅 Rail", 0, 100, t3_slider_values[1], format="%d%%", key='t3_rail_slider')
    t3_haul_truck_slider = t3.slider("🚚 Long-haul Truck", 0, 100, t3_slider_values[2], format="%d%%", key='t3_haul_truck_slider')
    t3_urban_truck_slider = t3.slider("🚚 Urban Delivery", 0, 100, t3_slider_values[3], format="%d%%", key='t3_urban_truck_slider')

    t4.write('###### Predicted increase in commodity demand')
    t4_option = t4.selectbox('Year', ('2016', '2036', '2056'), key='t4_option')
    if t4_option == '2016':
        t4_slider_values = (0, 0, 0, 0, 0, 0)
    if t4_option == '2036':
        t4_slider_values = (41, 66, 20, 29, 30, 43)
    if t4_option == '2056':
        t4_slider_values = (96, 161, 53, 54, 60, 78)
    t4_manufactures_slider = t4.slider("General manufactures", 0, 200, t4_slider_values[0], format="%d%%")
    t4_consumables_slider = t4.slider("Household consumables", 0, 200, t4_slider_values[1], format="%d%%")
    t4_construction_slider = t4.slider("Construction materials", 0, 200, t4_slider_values[2], format="%d%%")
    t4_fuel_slider = t4.slider("Fuel", 0, 200, t4_slider_values[3], format="%d%%")
    t4_vehicles_slider = t4.slider("Vehicles", 0, 200, t4_slider_values[4], format="%d%%")
    t4_waste_slider = t4.slider("Waste", 0, 200, t4_slider_values[5], format="%d%%")


# Add layers individually, as setting visibility doesn't actually remove data and improve performance.
layers = []
if 'Roads (Local)' in target_layer_names:
    layers.append(pdk.Layer(
        type="PathLayer",
        data=df,
        pickable=True,
        get_color="color",
        width_scale=20,
        width_min_pixels=2,
        get_path="path",
        get_width=3,
    ))

if 'Air' in target_layer_names:
    layers.append(pdk.Layer(
        "ArcLayer",
        airport_df[airport_df["from_name"] == selected_airport],
        pickable=True,
        get_stroke_width=12,
        get_source_position="from",
        get_target_position="to",
        get_source_color=list(np.array(get_network_color('air', hydrogen_uptake_percentage=t1_air_slider))*0.45),
        get_target_color=get_network_color('air', hydrogen_uptake_percentage=t1_air_slider),
        auto_highlight=True,
    ))

if 'Rail' in target_layer_names:
    layers.append(pdk.Layer(
        type="GeoJsonLayer",
        data=load_key_rail_freight_route(),
        get_line_color=get_network_color('rail', hydrogen_uptake_percentage=t1_rail_slider),
        line_width_min_pixels=1,
    ))

if 'Roads (Interstate)' in target_layer_names:
    layers.append(pdk.Layer(
        type="GeoJsonLayer",
        data=load_key_road_freight_route(),
        get_line_color=get_network_color('road_interstate', hydrogen_uptake_percentage=t1_haul_truck_slider),
        line_width_min_pixels=1,
    ))

if 'Roads (NLTN)' in target_layer_names:
    layers.append(pdk.Layer(
        type="GeoJsonLayer",
        data=load_nltn_road_data(),
        get_line_color=get_network_color('road_urban', hydrogen_uptake_percentage=t1_urban_truck_slider),
        line_width_min_pixels=1,
    ))

# Create a Pydeck map
map_layer = pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v9",
    initial_view_state=initial_view,
    layers=layers
)
col1.pydeck_chart(map_layer)


#%% Section 4: Generative AI 
st.divider()
st.write('# Freight-GPT - Ask questions about your data')
st.write("""
Got a question about your desired route? Use our Freight-GPT customised chatbot to take the guesswork out of your planning. 
""")


OPEN_AI_API_LEY = st.secrets["OPEN_AI_API_KEY"]
llm = OpenAI(OPEN_AI_API_LEY)

citywide_indices_df = pd.read_csv('data/raw/congestion_2020/citywide_indices_2020.csv')
route_metrics_df = pd.read_csv('data/raw/congestion_2020/route_metrics_2020.csv')
route_times_df = pd.read_csv('data/raw/congestion_2020/route_times_2020.csv')
segment_summary_df = pd.read_csv(
    'data/raw/congestion_2020/segment_summary_2020.csv',
    names=['road_id', 'hour_of_the_day', 'n_obvs', 'speed_limit', 'UQ', 'median', 'LQ', 'road_distance', 'route_name'],
    skiprows=1
)

t1, t2, t3, t4 = st.tabs(['Citywide Indices', 'Route Metrics', 'Route Times', 'Segment Summary'])
t1.dataframe(citywide_indices_df, use_container_width=True)
t1.write(""" 

""")
t2.dataframe(route_metrics_df, use_container_width=True)

t3.dataframe(route_times_df, use_container_width=True)

t4.dataframe(segment_summary_df, use_container_width=True)

dl = SmartDatalake([
    citywide_indices_df, 
    route_metrics_df,
    route_times_df,
    segment_summary_df,
], config={"llm": llm})

prompt = st.text_input(
    "Ask a question about your proposed route",
    placeholder="I'm driving a truck from Adelaide to Melbourne. How long would it take me if I left at 10am? Will there be much traffic congestion?"
)
if prompt:
    with st.spinner('Analysing the data...'):
        response = dl.chat(prompt)
        st.write(f"Your question: {prompt}")
        st.write(response)

