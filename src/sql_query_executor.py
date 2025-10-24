"""
SQL Query Executor for RTA Transit Analytics
Executes SQL queries on pandas DataFrames using pandasql
"""

import pandas as pd
import pandasql as psql
from typing import Dict, Any, Optional
import logging
from .data_loader import DataLoader


class SQLQueryExecutor:
    """Execute SQL queries on transit data using pandas DataFrames as tables."""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.logger = logging.getLogger(__name__)
        
    def execute_query(self, sql_query: str, months: Optional[list] = None) -> pd.DataFrame:
        """
        Execute SQL query on transit data.
        
        Args:
            sql_query: SQL query to execute
            months: Optional list of months to filter data
            
        Returns:
            DataFrame with query results
        """
        try:
            # Load data and create virtual tables
            tables = self._prepare_tables(months)
            
            # Execute SQL query using pandasql
            result = psql.sqldf(sql_query, tables)
            
            self.logger.info(f"SQL Query executed successfully: {sql_query[:100]}...")
            return result
            
        except Exception as e:
            error_msg = f"SQL Error: {str(e)}\n\nQuery attempted:\n{sql_query}\n\nPlease check:\n- Table names are correct\n- Column names with spaces use double quotes\n- Month format matches table (see schema)\n- Required JOINs are included for cross-table queries"
            self.logger.error(error_msg)
            # Return error as DataFrame so it displays nicely to user
            return pd.DataFrame({
                "Error": ["SQL Query Failed"],
                "Details": [str(e)],
                "Query": [sql_query[:200] + "..." if len(sql_query) > 200 else sql_query]
            })
    
    def _prepare_tables(self, months: Optional[list] = None) -> Dict[str, pd.DataFrame]:
        """
        Prepare virtual tables for SQL queries.
        
        Args:
            months: Optional list of months to filter
            
        Returns:
            Dictionary of table names to DataFrames
        """
        tables = {}
        
        # Load totals summary (service-level aggregates)
        totals_summary = self.data_loader.get_totals_summary(months=months)
        if not totals_summary.empty:
            tables['totals_summary'] = totals_summary
            tables['service_data'] = totals_summary  # Alias for clarity
        
        # Load monthly data (route-level data)
        monthly_data = self.data_loader.get_monthly_data(months=months)
        if not monthly_data.empty:
            tables['monthly_data'] = monthly_data
            tables['route_data'] = monthly_data  # Alias for clarity
        
        # Load daily summary (service-level daily aggregates)
        daily_summary = self.data_loader.get_daily_summary(months=months)
        if not daily_summary.empty:
            tables['daily_summary'] = daily_summary
        
        # Load daily data (route-level daily data)
        daily_data = self.data_loader.get_daily_data(months=months)
        if not daily_data.empty:
            tables['daily_data'] = daily_data
        
        # Load GTFS data (all tables)
        gtfs_data = self.data_loader.load_gtfs_data()
        if gtfs_data:
            tables['routes'] = gtfs_data.get('routes', pd.DataFrame())
            tables['stops'] = gtfs_data.get('stops', pd.DataFrame())
            tables['trips'] = gtfs_data.get('trips', pd.DataFrame())
            tables['stop_times'] = gtfs_data.get('stop_times', pd.DataFrame())
            tables['calendar'] = gtfs_data.get('calendar', pd.DataFrame())
            tables['calendar_dates'] = gtfs_data.get('calendar_dates', pd.DataFrame())
            tables['shapes'] = gtfs_data.get('shapes', pd.DataFrame())
            tables['transfers'] = gtfs_data.get('transfers', pd.DataFrame())
            tables['agency'] = gtfs_data.get('agency', pd.DataFrame())
        
        self.logger.info(f"Prepared {len(tables)} virtual tables for SQL queries")
        return tables
    
    def get_schema_info(self) -> str:
        """
        Get schema information for all available tables.
        
        Returns:
            String describing available tables and columns
        """
        schema_info = """
Available Tables and Columns:

1. totals_summary / service_data (Service-level aggregates):
   - Month, Service, Checkins, Checkouts, Unsettled Revenue, 
   - Driven Rev Km, Driven Dead Km, Load Factor, OTP%, CRR, 
   - Avg Fare, Cost / Rev Km, and more

2. monthly_data / route_data (Route-level data):
   - Month, Route, Service, Checkins, Checkouts, Unsettled Revenue,
   - OTP%, Load Factor, CRR, Avg Fare, and more

3. routes (GTFS Routes):
   - route_id, route_short_name, route_long_name, route_type, route_color

4. stops (GTFS Stops):
   - stop_id, stop_name, stop_lat, stop_lon, zone_id

5. trips (GTFS Trips):
   - trip_id, route_id, service_id, trip_headsign, direction_id

6. stop_times (GTFS Stop Times):
   - trip_id, stop_id, arrival_time, departure_time, stop_sequence

Example Queries:
- Percentage change: SELECT service, ((MAX(CASE WHEN month='Dec 2024' THEN "Unsettled Revenue" END) - MAX(CASE WHEN month='Sep 2024' THEN "Unsettled Revenue" END)) / MAX(CASE WHEN month='Sep 2024' THEN "Unsettled Revenue" END) * 100) as pct_change FROM totals_summary WHERE service='Urban' GROUP BY service
- Month comparison: SELECT month, service, "Unsettled Revenue" FROM totals_summary WHERE month IN ('July 2025', 'August 2025') AND service='Urban'
- Aggregation: SELECT service, SUM("Unsettled Revenue") as total FROM totals_summary WHERE month IN ('July 2025', 'August 2025') GROUP BY service
"""
        return schema_info

