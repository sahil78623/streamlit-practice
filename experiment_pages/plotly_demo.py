import ssl
import urllib.request
import json
import pandas as pd
import plotly.express as px
import streamlit as st

# Bypass SSL verification (not recommended for production)
context = ssl._create_unverified_context()
response = urllib.request.urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json', context=context)

# Read and decode GeoJSON data
geojson_data = response.read().decode('utf-8')
geojson_data = json.loads(geojson_data)

# Load unemployment data
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv", dtype={"fips": str})
print(df.head(1))
# df = """fips,unemp
# 01001,5.3
# 01003,5.4
# 01005,8.6
# 01007,6.6"""

# Create choropleth map using Plotly Express
fig = px.choropleth(df, geojson=geojson_data, locations='fips', color='unemp',
                    color_continuous_scale="Viridis",
                    range_color=(0, 12),
                    scope="usa",
                    labels={'unemp': 'unemployment rate'}
                    )
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Display Plotly figure inline within Streamlit
st.plotly_chart(fig)
