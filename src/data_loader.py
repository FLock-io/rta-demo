import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List
import logging
from glob import glob
import re


class DataLoader:
    def __init__(self, data_path: str = "Talk_to_your_Data", route_summary_folder: str = "RouteSummary-OneYear"):
        self.data_path = Path(data_path)
        self.gtfs_path = self.data_path / "Ops_GTFS_29-Aug-2025"
        self.route_summary_folder = Path(route_summary_folder)
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

    # ==================== TTSS Route Summary Methods ====================

    def _parse_month_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract month identifier from Route Summary filename.

        Examples:
            'Route Summary for PBD Dashboard July 2025.xlsx' -> 'July 2025'
            'Route Summary for PBD Dashboard December 2024.xlsx' -> 'December 2024'

        Returns:
            Month string in format 'MonthName YYYY' or None if not found
        """
        pattern = r'Route Summary for PBD Dashboard (.+)\.xlsx'
        match = re.search(pattern, filename)
        return match.group(1) if match else None

    def _get_all_route_summary_files(self) -> List[Path]:
        """
        Get all Route Summary Excel files from the folder.

        Returns:
            List of Path objects for all xlsx files
        """
        if not self.route_summary_folder.exists():
            self.logger.warning(f"Route summary folder not found: {self.route_summary_folder}")
            return []

        files = sorted(glob(str(self.route_summary_folder / "*.xlsx")))
        return [Path(f) for f in files if not Path(f).name.startswith('~')]

    def load_all_route_summaries(self, sheet_name: str = 'Monthly Data') -> Dict[str, pd.DataFrame]:
        """
        Load all Route Summary Excel files from the folder.

        Args:
            sheet_name: Name of the sheet to load from each file
                       Options: 'Totals Summary', 'Monthly Data', 'Daily Summary', 'Daily Data'

        Returns:
            Dictionary mapping month strings to DataFrames
            Example: {'July 2025': DataFrame, 'August 2025': DataFrame, ...}
        """
        cache_key = f"all_route_summaries_{sheet_name}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        files = self._get_all_route_summary_files()
        if not files:
            self.logger.warning("No Route Summary files found")
            return {}

        all_data = {}
        for file_path in files:
            month = self._parse_month_from_filename(file_path.name)
            if not month:
                self.logger.warning(f"Could not parse month from filename: {file_path.name}")
                continue

            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                all_data[month] = df
                self.logger.info(f"Loaded {month} {sheet_name}: {len(df)} rows")
            except Exception as e:
                self.logger.error(f"Error loading {file_path.name} sheet '{sheet_name}': {e}")

        self.cache[cache_key] = all_data
        self.logger.info(f"Loaded {len(all_data)} months of {sheet_name} data")
        return all_data

    def load_route_summary_by_month(self, month: str, sheet_name: str = 'Monthly Data') -> Optional[pd.DataFrame]:
        """
        Load Route Summary for a specific month.

        Args:
            month: Month identifier (e.g., 'July 2025', 'December 2024')
            sheet_name: Sheet to load from the Excel file

        Returns:
            DataFrame or None if not found
        """
        all_data = self.load_all_route_summaries(sheet_name=sheet_name)

        if month in all_data:
            return all_data[month]

        # Try case-insensitive match
        for key in all_data.keys():
            if key.lower() == month.lower():
                return all_data[key]

        self.logger.warning(f"Month '{month}' not found in Route Summary data")
        return None

    def get_monthly_data(self, months: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get Monthly Data from Route Summary files, optionally filtered by months.
        Combines all months into a single DataFrame with 'Month' column.

        Args:
            months: Optional list of month strings to filter
                   If None, returns all available months

        Returns:
            Combined DataFrame with all monthly route data
        """
        cache_key = f"monthly_data_combined_{months}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        all_data = self.load_all_route_summaries(sheet_name='Monthly Data')

        if not all_data:
            return pd.DataFrame()

        # Filter by months if specified
        if months:
            all_data = {k: v for k, v in all_data.items() if k in months or k.lower() in [m.lower() for m in months]}

        # Combine all DataFrames
        dfs = []
        for month, df in all_data.items():
            df_copy = df.copy()
            # Ensure Month column exists
            if 'Month' not in df_copy.columns:
                df_copy.insert(0, 'Month', month)
            dfs.append(df_copy)

        combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        self.cache[cache_key] = combined
        self.logger.info(f"Combined monthly data: {len(combined)} rows from {len(dfs)} months")
        return combined

    def get_daily_data(self, months: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get Daily Data from Route Summary files, optionally filtered by months.
        Combines all months into a single DataFrame.

        Args:
            months: Optional list of month strings to filter

        Returns:
            Combined DataFrame with all daily route data
        """
        cache_key = f"daily_data_combined_{months}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        all_data = self.load_all_route_summaries(sheet_name='Daily Data')

        if not all_data:
            return pd.DataFrame()

        # Filter by months if specified
        if months:
            all_data = {k: v for k, v in all_data.items() if k in months or k.lower() in [m.lower() for m in months]}

        # Combine all DataFrames
        dfs = []
        for month, df in all_data.items():
            df_copy = df.copy()
            # Parse Date column if it exists
            if 'Date' in df_copy.columns:
                df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce', format='%d-%b-%Y')
            dfs.append(df_copy)

        combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        self.cache[cache_key] = combined
        self.logger.info(f"Combined daily data: {len(combined)} rows from {len(dfs)} months")
        return combined

    def get_daily_summary(self, months: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get Daily Summary from Route Summary files, optionally filtered by months.
        Combines all months into a single DataFrame.

        Args:
            months: Optional list of month strings to filter

        Returns:
            Combined DataFrame with daily summary (aggregated by Date + Service)
        """
        cache_key = f"daily_summary_combined_{months}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        all_data = self.load_all_route_summaries(sheet_name='Daily Summary')

        if not all_data:
            return pd.DataFrame()

        # Filter by months if specified
        if months:
            all_data = {k: v for k, v in all_data.items() if k in months or k.lower() in [m.lower() for m in months]}

        # Combine all DataFrames
        dfs = []
        for month, df in all_data.items():
            df_copy = df.copy()
            # Parse Date column if it exists
            if 'Date' in df_copy.columns:
                df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce', format='%d-%b-%Y')
            dfs.append(df_copy)

        combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        self.cache[cache_key] = combined
        self.logger.info(f"Combined daily summary: {len(combined)} rows from {len(dfs)} months")
        return combined

    def get_totals_summary(self, months: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get Totals Summary from Route Summary files, optionally filtered by months.
        Combines all months into a single DataFrame with 'Month' column.

        Args:
            months: Optional list of month strings to filter

        Returns:
            Combined DataFrame with totals summary (Urban/Intercity/Feeder aggregates)
        """
        cache_key = f"totals_summary_combined_{months}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        all_data = self.load_all_route_summaries(sheet_name='Totals Summary')

        if not all_data:
            return pd.DataFrame()

        # Filter by months if specified
        if months:
            all_data = {k: v for k, v in all_data.items() if k in months or k.lower() in [m.lower() for m in months]}

        # Combine all DataFrames
        dfs = []
        for month, df in all_data.items():
            df_copy = df.copy()
            df_copy.insert(0, 'Month', month)
            dfs.append(df_copy)

        combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        self.cache[cache_key] = combined
        self.logger.info(f"Combined totals summary: {len(combined)} rows from {len(dfs)} months")
        return combined

    def get_available_months(self) -> List[str]:
        """
        Get list of all available months in Route Summary data.

        Returns:
            List of month strings (e.g., ['July 2025', 'August 2025', ...])
        """
        files = self._get_all_route_summary_files()
        months = []
        for file_path in files:
            month = self._parse_month_from_filename(file_path.name)
            if month:
                months.append(month)
        return sorted(months)

    def get_route_summary_info(self) -> Dict[str, any]:
        """
        Get summary information about available Route Summary data.

        Returns:
            Dictionary with metadata about the Route Summary files
        """
        files = self._get_all_route_summary_files()
        months = self.get_available_months()

        info = {
            'total_files': len(files),
            'available_months': months,
            'month_count': len(months),
            'folder_path': str(self.route_summary_folder),
            'sheets': ['Totals Summary', 'Monthly Data', 'Daily Summary', 'Daily Data']
        }

        return info
