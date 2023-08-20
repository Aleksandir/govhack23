
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

LIMITS = {
        'tonne.km/hr': np.log2(1_000_000),
        'gco2/tonne.km': 100,
        'km/h': 1000,
    }

def load_json(filename: str):
    with open(filename) as f:
        return json.load(f)


def calculate_freight_network_score(metric_list: list[float]) -> float:

    if len(metric_list) < 1:
        raise Exception("Empty metric list: no metrics to calculate")

    return np.mean(metric_list)


def get_network_tonne_km(network_type, tonne_scaling_factor):
    baseline = np.log2(float(ASSUMPTIONS['tonne.km/hr'][network_type])) * tonne_scaling_factor
    return (np.clip(baseline, 0, LIMITS['tonne.km/hr'])) / LIMITS['tonne.km/hr']

def get_network_gco2(network_type, hydrogen_uptake_percentage, gco2_scaling_factor):
    baseline = float(ASSUMPTIONS['gco2/tonne.km'][network_type]) * gco2_scaling_factor
    adjusted = baseline * (100 - hydrogen_uptake_percentage)/100
    return 1- (np.clip(adjusted, 0, LIMITS['gco2/tonne.km'])) / LIMITS['gco2/tonne.km']

def get_network_score(network_type: str, hydrogen_uptake_percentage: int, gco2_scaling_factor, tonne_scaling_factor) -> list[int]:
    score_1 = get_network_tonne_km(network_type, tonne_scaling_factor)
    score_2 = get_network_gco2(network_type, hydrogen_uptake_percentage, gco2_scaling_factor)

    return calculate_freight_network_score(metric_list=[score_1, score_2])

def get_network_color(network_type: str, hydrogen_uptake_percentage: int, gco2_scaling_factor, tonne_scaling_factor) -> list[int]:

    normalised_score = get_network_score(network_type, hydrogen_uptake_percentage, gco2_scaling_factor, tonne_scaling_factor)

    red = int((1 - normalised_score) * 255)
    green = int(normalised_score * 255)

    return [red, green, 0]

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

st.title("🚀 Australia's Shift to Hydrogen Powered Freight")
st.divider()

st.subheader("Grams of CO2/tonne.km")
gc1, gc2, gc3, gc4 = st.columns(4)

st.divider()
#%% Section 3 - Maps and Config
# Use columns to create layout
col1, col2 = st.columns([3, 2], gap='medium')  # Adjust the column widths as needed

# Display the Pydeck map in the first column
target_layer_names = col1.multiselect(
    label='What layers would you like to show', 
    options=['Air', 'Roads (Local)', 'Roads (Interstate)', 'Rail', 'Roads (NLTN)'], 
    default=['Air', 'Roads (Local)', 'Rail', 'Roads (Interstate)'],
)

airport_df = airport_data()
selected_airport = col1.selectbox("Select Airport", list(airport_df["from_name"].unique()) + ["None"], index=6)


# Define the initial view state centered on Australia
initial_view = pdk.ViewState(
    latitude=-25.2744,
    longitude=133.7751,
    zoom=3,
    pitch=45,
    bearing=0,
)

gco2_scaling_factor = st.slider("GCO2 Scaling Factor", 0.0, 2.0, step=0.1, value=1.0)
st.caption("Scales GCO2 Production rates across all networks. For example, 0.6 corresponds to a 40% reduction in overall GC02.")
tonne_scaling_factor = st.slider("Tonne KM/H Scaling Factor", 0.0, 2.0, step=0.1, value=1.0)
st.caption("Scales Tonne KM/H efficiency rates across all networks. For example, 1.6 corresponds to a 30% increase in overall Tonnes KM / H.")

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

    hydrogen_mult_dividor = 27  # if all fossil fuels
    hydrogen_mult_numerator = sizes_norm[0] * 27 + sizes_norm[1] * 12 + sizes_norm[2] * 0 + sizes_norm[3] * -2
    hydrogen_mult = hydrogen_mult_numerator / hydrogen_mult_dividor

    t3.write('###### Predicted increase in vehicle demand')
    t3_year = t3.selectbox('Year', ('2016', '2036', '2056'), key='t3_year')
    if t3_year == '2016':
        t3_slider_values = (100, 100, 100, 100, 0, 0)
    if t3_year == '2036':
        t3_slider_values = (100, 100, 100, 100, 0, 0)
    if t3_year == '2056':
        t3_slider_values = (100, 100, 100, 100, 0, 0)
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
        get_source_color=list(np.array(get_network_color('air', t1_air_slider, gco2_scaling_factor, tonne_scaling_factor))*0.6),
        get_target_color=get_network_color('air', t1_air_slider, gco2_scaling_factor, tonne_scaling_factor),
        auto_highlight=True,
    ))

if 'Rail' in target_layer_names:
    layers.append(pdk.Layer(
        type="GeoJsonLayer",
        data=load_key_rail_freight_route(),
        get_line_color=get_network_color('rail', t1_rail_slider, gco2_scaling_factor, tonne_scaling_factor),
        line_width_min_pixels=1,
    ))

if 'Roads (Interstate)' in target_layer_names:
    layers.append(pdk.Layer(
        type="GeoJsonLayer",
        data=load_key_road_freight_route(),
        get_line_color=get_network_color('road_interstate', t1_haul_truck_slider, gco2_scaling_factor, tonne_scaling_factor),
        line_width_min_pixels=1,
    ))

if 'Roads (NLTN)' in target_layer_names:
    layers.append(pdk.Layer(
        type="GeoJsonLayer",
        data=load_nltn_road_data(),
        get_line_color=get_network_color('road_urban', t1_urban_truck_slider, gco2_scaling_factor, tonne_scaling_factor),
        line_width_min_pixels=1,
    ))

# Create a Pydeck map
map_layer = pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v9",
    initial_view_state=initial_view,
    layers=layers
)
col1.pydeck_chart(map_layer)

st.divider()

gco2 = ASSUMPTIONS['gco2/tonne.km']
gco2_baseline_air = int(gco2['air'])
gco2_baseline_rail = int(gco2['rail'])
gco2_baseline_road_interstate = int(gco2['road_interstate'])
gco2_baseline_road_local = int(gco2['road_urban'])

gco2_air = int(((100 - t1_air_slider) * gco2_baseline_air) + (t1_air_slider * gco2_baseline_air * hydrogen_mult))
gco2_rail = int(((100 - t1_rail_slider) * gco2_baseline_rail) + (t1_rail_slider * gco2_baseline_rail * hydrogen_mult))
gco2_road_interstate = int(((100 - t1_haul_truck_slider) * gco2_baseline_road_interstate) + (t1_haul_truck_slider * gco2_baseline_road_interstate * hydrogen_mult))
gco2_road_local = int(((100 - t1_urban_truck_slider) * gco2_baseline_road_local) + (t1_urban_truck_slider * gco2_baseline_road_local * hydrogen_mult))

gc1.metric(label="Air", value=gco2_air, delta=gco2_air-60200, delta_color="inverse")
gc2.metric(label="Rail", value=gco2_rail, delta=gco2_rail-2200, delta_color="inverse")
gc3.metric(label="Roads (Interstate)", value=gco2_road_interstate, delta=gco2_road_interstate-6200, delta_color="inverse")
gc4.metric(label="Roads (Local)", value=gco2_road_local, delta=gco2_road_local-5000, delta_color="inverse")

st.subheader("Score Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric(label="Air", value=int(100*get_network_tonne_km('air', tonne_scaling_factor)), delta=int(100*get_network_gco2('air', t1_air_slider, gco2_scaling_factor)))
c2.metric(label="Rail", value=int(100*get_network_tonne_km('rail', tonne_scaling_factor)), delta=int(100*get_network_gco2('rail', t1_rail_slider, gco2_scaling_factor)))
c3.metric(label="Roads (Interstate)", value=int(100*get_network_tonne_km('road_interstate', tonne_scaling_factor)), delta=int(100*get_network_gco2('road_interstate', t1_haul_truck_slider, gco2_scaling_factor)))
c4.metric(label="Roads (Local)", value=int(100*get_network_tonne_km('road_urban', tonne_scaling_factor)), delta=int(100*get_network_gco2('road_urban', t1_urban_truck_slider, gco2_scaling_factor)))
st.caption("Number in bold refers to score for TonneKM / H. Number below in green refers to GCO2/Tonne Score")



#%% Section 4: Generative AI 
st.divider()
st.write('# Freight-GPT - Ask questions about your data')
st.write("""
Got a question about your desired route? Use our Freight-GPT customised chatbot to take the guesswork out of your planning. 
""")


OPEN_AI_API_LEY = st.secrets["OPEN_AI_API_KEY"]
llm = OpenAI(OPEN_AI_API_LEY)

route_metrics_df = pd.read_csv('data/raw/congestion_2020/route_metrics_2020.csv')
citywide_indices_df = pd.read_csv('data/raw/congestion_2020/citywide_indices_2020.csv')
route_times_df = pd.read_csv('data/raw/congestion_2020/route_times_2020.csv')
segment_summary_df = pd.read_csv(
    'data/raw/congestion_2020/segment_summary_2020.csv',
    names=['road_id', 'hour_of_the_day', 'n_obvs', 'speed_limit', 'UQ', 'median', 'LQ', 'road_distance', 'route_name'],
    skiprows=1
)

t1, t2, t3, t4 = st.tabs(['Route Metrics', 'Citywide Indices', 'Route Times', 'Segment Summary'])

t1.dataframe(route_metrics_df, use_container_width=True)

t2.dataframe(citywide_indices_df, use_container_width=True)

t3.dataframe(route_times_df, use_container_width=True)

t4.dataframe(segment_summary_df, use_container_width=True)

dl = SmartDatalake([
    citywide_indices_df, 
    route_metrics_df,
    route_times_df,
    segment_summary_df,
], config={"llm": llm, "enable_cache": False}, )

prompt = st.chat_input("I'm driving along route 32 - Derrimut to Montrose, what is the max median travel time?")

if prompt:
    st.write(f"### Your question")
    st.write(prompt)
    st.write(f"### Freight-GPT says")
    with st.spinner('Analysing the data...'):
        response = dl.chat(prompt)
        st.write(response)

