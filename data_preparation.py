import geopandas as gpd
import json

# Load the GeoJSON file
gdf = gpd.read_file('large_data.geojson')

# Optional: Simplify geometry to reduce file size
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01)

# Save the processed GeoJSON
gdf.to_file('processed_data.geojson', driver='GeoJSON')
