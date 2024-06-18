import json
import pandas as pd
import plotly.express as px
import streamlit as st

# Load GeoJSON data from a local file
with open('processed_data.geojson', 'r') as f:
    geojson_data = json.load(f)

# Load unemployment data
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv", dtype={"fips": str})

# Create choropleth map using Plotly Express
fig = px.choropleth_mapbox(df, geojson=geojson_data, locations='fips', color='unemp',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                           opacity=0.5,
                           labels={'unemp': 'unemployment rate'},
                           featureidkey="properties.FIPS"
                           )

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Display Plotly figure inline within Streamlit
st.plotly_chart(fig)
