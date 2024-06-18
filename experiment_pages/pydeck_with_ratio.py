import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk
from shapely.geometry import Point

# Function to load GeoJSON data with caching
@st.cache_data
def load_geojson(file_path):
    return gpd.read_file(file_path)

# Function to load CSV data with caching
@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path)

# Load the GeoJSON data
geo_data = load_geojson('processed_data.geojson')

# Load the CSV data
# csv_data = load_csv('csv_data.csv')
csv_data = load_csv('filtered_csv.csv')

# Inspect columns of both dataframes
st.write("GeoJSON columns:", geo_data.columns)
st.write("CSV columns:", csv_data.columns)

# Rename columns in CSV to avoid clashes
csv_data.rename(columns={'MEMBER': 'MEMBER_csv'}, inplace=True)

# Merge GeoJSON with CSV on 'ST_LEAID'
geo_data = geo_data.merge(csv_data, on='ST_LEAID', how='left')

# Inspect merged dataframe
st.write("Merged DataFrame columns:", geo_data.columns)
st.write(geo_data.head())

# Reproject to a projected CRS (e.g., EPSG:3857)
geo_data = geo_data.to_crs(epsg=3857)

# Calculate centroid coordinates in the projected CRS
centroid = geo_data.geometry.centroid
mean_latitude = centroid.y.mean()
mean_longitude = centroid.x.mean()

# Convert centroid to a Point and create a GeoDataFrame
centroid_point = Point(mean_longitude, mean_latitude)
centroid_geo = gpd.GeoDataFrame(index=[0], crs="EPSG:3857", geometry=[centroid_point])

# Reproject centroid to geographic CRS
centroid_geo = centroid_geo.to_crs(epsg=4326)
mean_latitude = centroid_geo.geometry.y[0]
mean_longitude = centroid_geo.geometry.x[0]

# Reproject geo_data back to geographic CRS for visualization
geo_data = geo_data.to_crs(epsg=4326)

# Function to map MEMBER to color
def get_color(MEMBER):
    # Example color mapping: higher MEMBER values get darker shades of red
    if pd.isnull(MEMBER):
        return [0, 0, 0, 0]  # Return transparent color for NaN values
    color_intensity = min(255, max(0, int(MEMBER / max_MEMBER * 255)))
    return [color_intensity, 0, 0, 140]  # RGBA: shades of red with partial transparency

# Ensure 'MEMBER_csv' column exists before proceeding
if 'MEMBER_csv' in geo_data.columns:
    # Fill NaN values in 'MEMBER_csv' with 0
    geo_data['MEMBER_csv'] = geo_data['MEMBER_csv'].fillna(0)

    # Find maximum MEMBER value for normalization
    max_MEMBER = geo_data['MEMBER_csv'].max()

    # Apply color mapping function
    geo_data['fill_color'] = geo_data['MEMBER_csv'].apply(get_color)

    # Pydeck visualization
    layer = pdk.Layer(
        'GeoJsonLayer',
        geo_data.__geo_interface__,
        pickable=True,
        stroked=False,
        filled=True,
        extruded=True,
        wireframe=True,
        get_fill_color='[feature.properties.fill_color[0], feature.properties.fill_color[1], feature.properties.fill_color[2], feature.properties.fill_color[3]]',
        get_line_color='[255, 255, 255]'
    )

    view_state = pdk.ViewState(
        latitude=mean_latitude,
        longitude=mean_longitude,
        zoom=3,
        pitch=0,
        bearing=0
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state
    ))
else:
    st.error("The 'MEMBER_csv' column is not found in the merged GeoDataFrame.")
