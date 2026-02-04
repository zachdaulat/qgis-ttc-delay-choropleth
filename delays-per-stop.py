# TTC Delay Rate by Neighbourhood - QGIS Python Script
# Calculates delays per transit stop for each Toronto neighbourhood

from qgis.core import (
    QgsProject, 
    QgsVectorLayer, 
    QgsField,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils
)
from PyQt5.QtCore import QVariant
import os
import processing

# === Configurating Paths ===
# Getting project path
project_file = QgsProject.instance().fileName()
# Getting directory path
project_dir = os.path.dirname(project_file)

# Constructing each dataset path
NEIGHBOURHOODS_PATH = os.path.join(project_dir, "data", "Neighbourhoods - 2952.gpkg")
DELAYS_PATH = os.path.join(project_dir, "data", "delays_qgis.gpkg|layername=delays")
STOPS_PATH = os.path.join(project_dir, "data", "stops.txt")
OUTPUT_PATH = os.path.join(project_dir, "data", "delay_rate_by_neighbourhood.gpkg")

# === Loading Layers ===
neighbourhoods = QgsVectorLayer(NEIGHBOURHOODS_PATH, "neighbourhoods", "ogr")
delays = QgsVectorLayer(DELAYS_PATH, "delays", "ogr")

# Loading GTFS stops (CSV with coordinates)
stops_uri = f"file:///{STOPS_PATH}?delimiter=,&xField=stop_lon&yField=stop_lat&crs=EPSG:4326"
stops = QgsVectorLayer(stops_uri, "stops", "delimitedtext")

# === Counting delays per hood ===
result_delays = processing.run("native:countpointsinpolygon", {
    'POLYGONS': neighbourhoods,
    'POINTS': delays,
    'FIELD': 'delay_count',
    'OUTPUT': 'memory:'
})
neighbourhoods_with_delays = result_delays['OUTPUT']

# === Counting stops per hood ===
result_stops = processing.run("native:countpointsinpolygon", {
    'POLYGONS': neighbourhoods_with_delays,
    'POINTS': stops,
    'FIELD': 'stop_count',
    'OUTPUT': 'memory:'
})
neighbourhoods_with_counts = result_stops['OUTPUT']

# === Calculating delays per stop for each hood ===
# Add the delay_rate field
neighbourhoods_with_counts.startEditing()
neighbourhoods_with_counts.addAttribute(QgsField('delay_rate', QVariant.Double))
neighbourhoods_with_counts.updateFields()

# Get field indices
delay_idx = neighbourhoods_with_counts.fields().indexOf('delay_count')
stop_idx = neighbourhoods_with_counts.fields().indexOf('stop_count')
rate_idx = neighbourhoods_with_counts.fields().indexOf('delay_rate')

# Calculate rate for each feature
for feature in neighbourhoods_with_counts.getFeatures():
    delay_count = feature[delay_idx] or 0
    stop_count = feature[stop_idx] or 0
    
    if stop_count > 0:
        rate = delay_count / stop_count
    else:
        rate = 0
    
    neighbourhoods_with_counts.changeAttributeValue(feature.id(), rate_idx, rate)

neighbourhoods_with_counts.commitChanges()

# === Saving output ===
print(f"Saving to {OUTPUT_PATH}...")
processing.run("native:savefeatures", {
    'INPUT': neighbourhoods_with_counts,
    'OUTPUT': OUTPUT_PATH
})
