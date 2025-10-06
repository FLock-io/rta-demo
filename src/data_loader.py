import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional
import logging


class DataLoader:
    def __init__(self, data_path: str = "Talk_to_your_Data"):
        self.data_path = Path(data_path)
        self.gtfs_path = self.data_path / "Ops_GTFS_29-Aug-2025"
        self.cache = {}

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_gtfs_data(self) -> Dict[str, pd.DataFrame]:
        """Load all GTFS files into pandas DataFrames."""

        if "gtfs" in self.cache:
            return self.cache["gtfs"]

        gtfs_files = [
            "agency.txt",
            "routes.txt",
            "stops.txt",
            "trips.txt",
            "stop_times.txt",
            "calendar.txt",
            "shapes.txt",
            "transfers.txt",
        ]

        gtfs_data = {}

        for file in gtfs_files:
            file_path = self.gtfs_path / file
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    gtfs_data[file.replace(".txt", "")] = df
                    self.logger.info(f"Loaded {file}: {len(df)} rows")
                except Exception as e:
                    self.logger.error(f"Error loading {file}: {e}")
            else:
                self.logger.warning(f"File not found: {file}")

        self.cache["gtfs"] = gtfs_data
        return gtfs_data

    def load_route_summary(self) -> Optional[pd.DataFrame]:
        """Load Route Summary Excel file."""

        if "route_summary" in self.cache:
            return self.cache["route_summary"]

        route_file = self.data_path / "Route Summary for PBD Dashboard July 2025.xlsx"

        if route_file.exists():
            try:
                df = pd.read_excel(route_file)
                self.cache["route_summary"] = df
                self.logger.info(f"Loaded route summary: {len(df)} rows")
                return df
            except Exception as e:
                self.logger.error(f"Error loading route summary: {e}")
                return None
        else:
            self.logger.warning("Route summary file not found")
            return None

    def get_routes(self) -> pd.DataFrame:
        """Get routes data with enhanced information."""
        gtfs_data = self.load_gtfs_data()
        routes = gtfs_data.get("routes", pd.DataFrame())

        if not routes.empty:
            # Add route type descriptions
            route_type_map = {
                0: "Tram/Light Rail",
                1: "Metro",
                2: "Rail",
                3: "Bus",
                4: "Ferry",
            }
            routes["route_type_desc"] = routes["route_type"].map(route_type_map)

            # Separate metro and bus routes
            routes["is_metro"] = routes["route_type"] == 1
            routes["is_bus"] = routes["route_type"] == 3

        return routes

    def get_stops(self) -> pd.DataFrame:
        """Get stops data with geographic information."""
        gtfs_data = self.load_gtfs_data()
        stops = gtfs_data.get("stops", pd.DataFrame())

        if not stops.empty:
            # Convert coordinates to numeric
            stops["stop_lat"] = pd.to_numeric(stops["stop_lat"], errors="coerce")
            stops["stop_lon"] = pd.to_numeric(stops["stop_lon"], errors="coerce")

            # Add geographic bounds for Dubai
            dubai_bounds = {
                "lat_min": 24.8,
                "lat_max": 25.4,
                "lon_min": 54.8,
                "lon_max": 55.6,
            }

            # Flag stops within Dubai bounds
            stops["in_dubai"] = (
                (stops["stop_lat"] >= dubai_bounds["lat_min"])
                & (stops["stop_lat"] <= dubai_bounds["lat_max"])
                & (stops["stop_lon"] >= dubai_bounds["lon_min"])
                & (stops["stop_lon"] <= dubai_bounds["lon_max"])
            )

        return stops

    def get_stop_times(self) -> pd.DataFrame:
        """Get stop times data with time parsing."""
        gtfs_data = self.load_gtfs_data()
        stop_times = gtfs_data.get("stop_times", pd.DataFrame())

        if not stop_times.empty:
            # Parse time columns
            for col in ["arrival_time", "departure_time"]:
                if col in stop_times.columns:
                    stop_times[col] = pd.to_datetime(
                        stop_times[col], format="%H:%M:%S", errors="coerce"
                    )

        return stop_times

    def get_trips(self) -> pd.DataFrame:
        """Get trips data."""
        gtfs_data = self.load_gtfs_data()
        return gtfs_data.get("trips", pd.DataFrame())

    def get_shapes(self) -> pd.DataFrame:
        """Get shapes data for route visualization."""
        gtfs_data = self.load_gtfs_data()
        shapes = gtfs_data.get("shapes", pd.DataFrame())

        if not shapes.empty:
            # Convert coordinates to numeric
            shapes["shape_pt_lat"] = pd.to_numeric(
                shapes["shape_pt_lat"], errors="coerce"
            )
            shapes["shape_pt_lon"] = pd.to_numeric(
                shapes["shape_pt_lon"], errors="coerce"
            )

        return shapes

    def get_calendar(self) -> pd.DataFrame:
        """Get calendar/schedule data."""
        gtfs_data = self.load_gtfs_data()
        return gtfs_data.get("calendar", pd.DataFrame())

    def get_transfers(self) -> pd.DataFrame:
        """Get transfer points data."""
        gtfs_data = self.load_gtfs_data()
        return gtfs_data.get("transfers", pd.DataFrame())

    def get_agency_info(self) -> pd.DataFrame:
        """Get agency information."""
        gtfs_data = self.load_gtfs_data()
        return gtfs_data.get("agency", pd.DataFrame())

    def clear_cache(self):
        """Clear cached data."""
        self.cache.clear()
        self.logger.info("Data cache cleared")
