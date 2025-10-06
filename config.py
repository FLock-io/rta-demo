import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Talk to your Data"
GTFS_DIR = DATA_DIR / "Ops_GTFS_29-Aug-2025"

# API Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# App Configuration
APP_TITLE = "RTA Transit Analytics"
APP_ICON = "🚇"

# Data files
ROUTE_SUMMARY_FILE = DATA_DIR / "Route Summary for PBD Dashboard July 2025.xlsx"
DATA_DICTIONARY_FILE = DATA_DIR / "Data-Dictionary.xlsx"

# Map configuration for Dubai
DUBAI_CENTER = {
    'lat': 25.2048,
    'lon': 55.2708
}

DUBAI_BOUNDS = {
    'lat_min': 24.8, 'lat_max': 25.4,
    'lon_min': 54.8, 'lon_max': 55.6
}