import streamlit as st
import geopandas as gpd
import pydeck as pdk
from shapely.geometry import Point

# Function to load GeoJSON data with new caching command
@st.cache_data
def load_data(file_path):
    return gpd.read_file(file_path)

# Load the entire GeoJSON data
geo_data = load_data('processed_data.geojson')

# Choose the property to base the color shading on
property_name = 'MEMBER'

# Ensure the property column exists
if property_name not in geo_data.columns:
    st.error(f"The property '{property_name}' is not found in the GeoDataFrame.")
    st.stop()

# Fill NaN values in the property column with 0 or another default value
geo_data[property_name] = geo_data[property_name].fillna(0)

# Function to map a property value to color (white to yellow gradient)
def get_color(value, max_value):
    color_intensity = min(255, max(0, int(value / max_value * 255)))
    return [255, 255, color_intensity, 140]  # RGBA: white to yellow with partial transparency

# Find the maximum value of the property for normalization
max_value = geo_data[property_name].max()

# Apply color mapping function
geo_data['fill_color'] = geo_data[property_name].apply(lambda x: get_color(x, max_value))

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

# Multiselect for tooltip fields
available_columns = geo_data.columns.tolist()
tooltip_fields = st.multiselect("Select fields for tooltip:", available_columns, default=['STATENAME', 'MEMBER'])

# Construct the tooltip HTML dynamically
tooltip_html = ""
for field in tooltip_fields:
    tooltip_html += f"<b>{field}:</b> {{{{{field}}}}}<br>"

tooltip = {
    "html": tooltip_html,
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# Pydeck visualization
layer = pdk.Layer(
    'GeoJsonLayer',
    geo_data._geo_interface_,
    pickable=True,
    stroked=True,
    filled=True,
    extruded=False,
    wireframe=True,
    get_fill_color='[properties.fill_color[0], properties.fill_color[1], properties.fill_color[2], properties.fill_color[3]]',
    get_line_color=[255, 255, 255],  # Set line color to white for visibility
    line_width_min_pixels=0.5,  # Set minimum line width for reduced thickness
    highlight_color=[255, 255, 255, 150],  # Transparent white for highlighting
    auto_highlight=True  # Enable auto highlighting
)

view_state = pdk.ViewState(
    latitude=mean_latitude,
    longitude=mean_longitude,
    zoom=3,
    pitch=0,
    bearing=0
)

st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))