import streamlit as st
import geopandas as gpd
import pydeck as pdk
from shapely.geometry import Point

# Function to load GeoJSON data with new caching command
@st.cache_data
def load_data(file_path):
    return gpd.read_file(file_path)

# Load the data
geo_data = load_data('processed_data.geojson')

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

# Streamlit app layout
st.title("GeoJSON Data Analytics Pydeck")

# Pydeck visualization
layer = pdk.Layer(
    'GeoJsonLayer',
    geo_data.__geo_interface__,
    pickable=True,
    stroked=False,
    filled=True,
    extruded=True,
    wireframe=True,
    get_fill_color='[180, 0, 200, 140]',
    get_line_color='[255, 255, 255]'
)

view_state = pdk.ViewState(
    latitude=38,
    longitude=-96.5,
    zoom=3,
    # camera angle
    pitch=0,
    # movement towards north
    bearing=0
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))
