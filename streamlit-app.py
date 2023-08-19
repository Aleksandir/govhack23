import streamlit as st
import pandas as pd
from shapely.wkt import loads

import streamlit as st
import pydeck as pdk


def main():
    # Create Shapely linestrings (replace this with your actual data)
    # Example: [(lon1, lat1), (lon2, lat2), ...]
    df = pd.read_csv("data/raw/congestion_2020/geometries_2020.csv").set_index('route_name')
    str_to_linstr = lambda linstr: [[cord.split(" ")[1], cord.split(" ")[0]] for cord in linstr.strip('LINESTRING (').strip(')').split(", ")]
    linestrings = df['route_geom'].apply(loads)

    # Create a GeoDataFrame from the linestrings
    # gdf = gpd.GeoDataFrame(geometry=df['route_geom'].apply(str_to_linstr).apply(lambda x: 'LINESTRING (' + ', '.join([' '.join(y) for y in x]) + ')').apply(loads))
    gdf = gdp.GeoDataFrame(geometry=linestrings)

    st.set_page_config(layout="wide")
    st.title("Interactive Map of Australia")
    
    # Sliders for different modes of transportation
    air_slider = st.slider("✈️ Air", 0, 100, 50)
    sea_slider = st.slider("🚢 Sea", 0, 100, 50)
    land_slider = st.slider("🚚 Land", 0, 100, 50)
    rail_slider = st.slider("🚅 Rail", 0, 100, 50)

    # Year range for the data
    year_range = st.slider("Year Range", 1990, 2050, (2023))
    
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
    col1, col2 = st.columns([3, 2])  # Adjust the column widths as needed
    
    # Display the Pydeck map in the first column
    with col1:
        st.pydeck_chart(map_layer)
    
    # Display the slider values in the second column
    with col2:
        st.markdown("## Slider Values")
        col2_1, col2_2 = st.columns([1, 1])
        with col2_1:
            st.markdown(f"### ✈️ Air: {air_slider}")
            st.markdown(f"### 🚢 Sea: {sea_slider}")
        with col2_2:
            st.markdown(f"### 🚚 Land: {land_slider}")
            st.markdown(f"### 🚅 Rail: {rail_slider}")

    question = st.text_input("Ask a question about the data")

if __name__ == "__main__":
    main()


st.title('GovHack 2023')