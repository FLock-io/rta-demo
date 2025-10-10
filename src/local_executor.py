import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import numpy as np
from .data_loader import DataLoader
from .visualizations import Visualizer


class LocalExecutor:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.visualizer = Visualizer(data_loader)
        self.function_map = {
            # GTFS functions
            "get_route_statistics": self.get_route_statistics,
            "get_stop_information": self.get_stop_information,
            "analyze_route_coverage": self.analyze_route_coverage,
            "get_busiest_stops": self.get_busiest_stops,
            "calculate_route_distances": self.calculate_route_distances,
            "get_stop_accessibility": self.get_stop_accessibility,
            "analyze_service_frequency": self.analyze_service_frequency,
            "generate_route_map": self.generate_route_map,
            "get_transfer_points": self.get_transfer_points,
            "analyze_network_connectivity": self.analyze_network_connectivity,
            # TTSS functions
            "get_otp_analysis": self.get_otp_analysis,
            "get_load_factor_analysis": self.get_load_factor_analysis,
            "get_crr_analysis": self.get_crr_analysis,
            "get_ridership_trends": self.get_ridership_trends,
            "get_revenue_analysis": self.get_revenue_analysis,
            "get_cost_efficiency": self.get_cost_efficiency,
            "get_service_summary": self.get_service_summary,
            "get_top_routes_by_kpi": self.get_top_routes_by_kpi,
            "get_route_performance": self.get_route_performance,
            "analyze_weekend_vs_weekday": self.analyze_weekend_vs_weekday,
            # Visualization functions
            "plot_monthly_kpi_trends": self.visualizer.plot_monthly_kpi_trends,
        }

    def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the generated plan step by step."""
        results = []

        for step in plan.get("steps", []):
            function_name = step.get("function")
            parameters = step.get("parameters", {})
            output_type = step.get("output_type", "text")

            if function_name in self.function_map:
                try:
                    # Filter parameters to only include those accepted by the function
                    import inspect

                    func = self.function_map[function_name]
                    sig = inspect.signature(func)
                    valid_params = {
                        k: v for k, v in parameters.items() if k in sig.parameters
                    }

                    result = func(**valid_params)
                    results.append(
                        {
                            "title": step.get("description", function_name),
                            "type": output_type,
                            "data": result,
                            "function": function_name,
                        }
                    )
                    step["completed"] = True
                except Exception as e:
                    results.append(
                        {
                            "title": f"Error in {function_name}",
                            "type": "text",
                            "content": f"Error: {str(e)}",
                            "function": function_name,
                        }
                    )
                    step["completed"] = False

        return results

    def get_route_statistics(self, route_type: str = None) -> pd.DataFrame:
        """Get basic statistics about routes."""
        routes = self.data_loader.get_routes()

        # Filter by route type if provided
        if route_type and route_type.lower() == "metro":
            routes = routes[routes["route_type"] == 1]
        elif route_type and route_type.lower() == "bus":
            routes = routes[routes["route_type"] == 3]

        return routes[
            ["route_id", "route_short_name", "route_long_name", "route_type_desc"]
        ].head(20)

    def get_stop_information(
        self, stop_name: str = None, limit: int = 50
    ) -> pd.DataFrame:
        """Get information about stops."""
        stops = self.data_loader.get_stops()

        # Filter by stop name if provided
        if stop_name:
            stops = stops[
                stops["stop_name"].str.contains(stop_name, case=False, na=False)
            ]

        return stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].head(limit)

    def analyze_route_coverage(self) -> go.Figure:
        """Show all stops on a map."""
        stops = self.data_loader.get_stops()
        stops = stops.dropna(subset=["stop_lat", "stop_lon"])

        fig = px.scatter_mapbox(
            stops,
            lat="stop_lat",
            lon="stop_lon",
            hover_name="stop_name",
            zoom=10,
            height=600,
            title="RTA Stop Coverage Map",
        )

        fig.update_layout(
            mapbox_style="open-street-map", margin={"r": 0, "t": 50, "l": 0, "b": 0}
        )

        return fig

    def get_busiest_stops(self, limit: int = 20) -> pd.DataFrame:
        """Identify busiest stops based on trip frequency."""
        stop_times = self.data_loader.get_stop_times()
        stops = self.data_loader.get_stops()

        # Count trips per stop
        trip_counts = (
            stop_times.groupby("stop_id").size().reset_index(name="trip_count")
        )

        # Merge with stop information
        result = trip_counts.merge(
            stops[["stop_id", "stop_name"]], on="stop_id", how="left"
        )

        # Sort by trip count
        return result.sort_values("trip_count", ascending=False).head(limit)

    def calculate_route_distances(self) -> pd.DataFrame:
        """Calculate approximate distances for all routes."""
        shapes = self.data_loader.get_shapes()
        distances = []

        for shape_id in shapes["shape_id"].unique()[:20]:  # Limit to first 20
            shape_points = shapes[shapes["shape_id"] == shape_id].sort_values(
                "shape_pt_sequence"
            )

            if len(shape_points) > 1:
                lats = shape_points["shape_pt_lat"].values
                lons = shape_points["shape_pt_lon"].values

                total_distance = 0
                for i in range(1, len(lats)):
                    lat_diff = lats[i] - lats[i - 1]
                    lon_diff = lons[i] - lons[i - 1]
                    distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111
                    total_distance += distance

                distances.append(
                    {"shape_id": shape_id, "distance_km": round(total_distance, 2)}
                )

        return pd.DataFrame(distances)

    def get_stop_accessibility(self) -> pd.DataFrame:
        """Count stops by zone."""
        stops = self.data_loader.get_stops()

        if "zone_id" in stops.columns:
            zone_counts = stops["zone_id"].value_counts()
            return pd.DataFrame(
                {"Zone": zone_counts.index, "Stop Count": zone_counts.values}
            )
        else:
            return pd.DataFrame({"Message": ["No zone information available"]})

    def analyze_service_frequency(self, route_type: str = None) -> pd.DataFrame:
        """Count trips per route."""
        trips = self.data_loader.get_trips()
        routes = self.data_loader.get_routes()

        # Filter by route type if provided
        if route_type and route_type.lower() == "metro":
            routes = routes[routes["route_type"] == 1]
        elif route_type and route_type.lower() == "bus":
            routes = routes[routes["route_type"] == 3]

        # Count trips per route
        trip_counts = trips.groupby("route_id").size().reset_index(name="trip_count")

        # Merge with route information
        result = trip_counts.merge(
            routes[["route_id", "route_short_name", "route_type_desc"]],
            on="route_id",
            how="inner",
        )

        return result.sort_values("trip_count", ascending=False).head(20)

    def generate_route_map(self, max_routes: int = 10) -> go.Figure:
        """Draw route shapes on a map with distinct colors and unique route names."""
        shapes = self.data_loader.get_shapes()
        trips = self.data_loader.get_trips()
        routes = self.data_loader.get_routes()

        # Map shape_id to route_short_name via trips and routes
        shape_to_route = trips.merge(
            routes[["route_id", "route_short_name", "route_long_name"]],
            on="route_id",
            how="left",
        )[["shape_id", "route_short_name", "route_long_name"]].drop_duplicates()

        # Group by route_short_name and select one representative shape per route
        shape_counts = shapes.groupby("shape_id").size().reset_index(name="point_count")
        shape_to_route_with_counts = shape_to_route.merge(
            shape_counts, on="shape_id", how="left"
        )

        # For each unique route_short_name, pick the shape with most points
        representative_shapes = (
            shape_to_route_with_counts.sort_values("point_count", ascending=False)
            .groupby("route_short_name")
            .first()
            .reset_index()
        )

        # Limit to max_routes unique routes
        representative_shapes = representative_shapes.head(max_routes)

        fig = go.Figure()

        # Define color palette
        colors = [
            "#e6194b",
            "#3cb44b",
            "#ffe119",
            "#4363d8",
            "#f58231",
            "#911eb4",
            "#46f0f0",
            "#f032e6",
            "#bcf60c",
            "#fabebe",
            "#008080",
            "#e6beff",
            "#9a6324",
            "#fffac8",
            "#800000",
        ]

        # Plot representative shape for each route
        for idx, row in representative_shapes.iterrows():
            shape_id = row["shape_id"]
            route_name = row["route_short_name"]
            route_long = row["route_long_name"]

            shape_points = shapes[shapes["shape_id"] == shape_id].sort_values(
                "shape_pt_sequence"
            )

            # Skip shapes with no valid data
            if shape_points.empty or len(shape_points) < 2:
                continue

            display_name = f"{route_name}"
            hover_name = f"{route_name} - {route_long}"

            fig.add_trace(
                go.Scattermapbox(
                    lat=shape_points["shape_pt_lat"],
                    lon=shape_points["shape_pt_lon"],
                    mode="lines",
                    name=display_name,
                    line=dict(width=3, color=colors[idx % len(colors)]),
                    hovertemplate=f"<b>{hover_name}</b><br>"
                    + "Lat: %{lat:.5f}<br>"
                    + "Lon: %{lon:.5f}<br>"
                    + "<extra></extra>",
                )
            )

        fig.update_layout(
            mapbox=dict(
                style="open-street-map", center=dict(lat=25.2, lon=55.3), zoom=10
            ),
            height=600,
            title=f"RTA Route Network (Showing {len(fig.data)} unique routes)",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255,255,255,0.8)",
            ),
        )

        return fig

    def get_transfer_points(self) -> pd.DataFrame:
        """Get all transfer points."""
        transfers = self.data_loader.get_transfers()
        stops = self.data_loader.get_stops()

        # Merge with stop names
        result = transfers.merge(
            stops[["stop_id", "stop_name"]],
            left_on="from_stop_id",
            right_on="stop_id",
            how="left",
        ).rename(columns={"stop_name": "from_stop_name"})

        result = result.merge(
            stops[["stop_id", "stop_name"]],
            left_on="to_stop_id",
            right_on="stop_id",
            how="left",
        ).rename(columns={"stop_name": "to_stop_name"})

        return result[
            ["from_stop_name", "to_stop_name", "transfer_type", "min_transfer_time"]
        ].head(50)

    def analyze_network_connectivity(self) -> pd.DataFrame:
        """Get basic network statistics."""
        stops = self.data_loader.get_stops()
        routes = self.data_loader.get_routes()
        transfers = self.data_loader.get_transfers()

        return pd.DataFrame(
            {
                "Metric": ["Total Stops", "Total Routes", "Transfer Points"],
                "Count": [len(stops), len(routes), len(transfers)],
            }
        )

    # ==================== TTSS Analysis Functions ====================

    def get_otp_analysis(
        self,
        route_id: str = None,
        service: str = None,
        month: str = None,
        limit: int = 20,
    ) -> pd.DataFrame:
        """
        Analyze On-Time Performance (OTP%) for routes.

        Args:
            route_id: Optional route ID to filter by
            service: Optional service type (Urban/Intercity/Feeder)
            month: Optional month to filter by (e.g., 'July 2025')
            limit: Maximum number of results to return

        Returns:
            DataFrame with OTP% analysis
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_monthly_data(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by route_id if provided
        if route_id:
            df = df[df["Route"].astype(str) == str(route_id)]

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Select relevant columns
        columns = [
            "Month",
            "Route",
            "Service",
            "OTP%",
            "1stStop1stTrip OTP%",
            "OnTime Stops",
            "Total Stops",
            "Late Stops",
            "Early Stops",
        ]
        available_columns = [col for col in columns if col in df.columns]
        result = df[available_columns].copy()

        # Sort by OTP% descending
        if "OTP%" in result.columns:
            result = result.sort_values("OTP%", ascending=False)

        return result.head(limit)

    def get_load_factor_analysis(
        self,
        route_id: str = None,
        service: str = None,
        month: str = None,
        limit: int = 20,
    ) -> pd.DataFrame:
        """
        Analyze Load Factor (capacity utilization) for routes.

        Args:
            route_id: Optional route ID to filter by
            service: Optional service type
            month: Optional month to filter by
            limit: Maximum number of results

        Returns:
            DataFrame with Load Factor analysis
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_monthly_data(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by route_id if provided
        if route_id:
            df = df[df["Route"].astype(str) == str(route_id)]

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Select relevant columns
        columns = [
            "Month",
            "Route",
            "Service",
            "Load Factor",
            "Passenger Km",
            "Seat Km",
            "Checkins",
            "Operated Rev Trips",
        ]
        available_columns = [col for col in columns if col in df.columns]
        result = df[available_columns].copy()

        # Sort by Load Factor descending
        if "Load Factor" in result.columns:
            result = result.sort_values("Load Factor", ascending=False)

        return result.head(limit)

    def get_crr_analysis(
        self, route_id: str = None, service: str = None, month: str = None, limit: int = 20
    ) -> pd.DataFrame:
        """
        Analyze Cost Recovery Ratio (CRR) - Revenue vs Cost efficiency.

        Args:
            route_id: Optional route ID to filter by
            service: Optional service type
            month: Optional month to filter by
            limit: Maximum number of results

        Returns:
            DataFrame with CRR analysis
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_monthly_data(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by route_id if provided
        if route_id:
            df = df[df["Route"].astype(str) == str(route_id)]

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Select relevant columns
        columns = [
            "Month",
            "Route",
            "Service",
            "CRR",
            "Rev / Rev Km",
            "Cost / Rev Km",
            "Avg Daily Cost",
            "Subsidy / Rev Km",
        ]
        available_columns = [col for col in columns if col in df.columns]
        result = df[available_columns].copy()

        # Sort by CRR descending
        if "CRR" in result.columns:
            result = result.sort_values("CRR", ascending=False)

        return result.head(limit)

    def get_ridership_trends(
        self, route_id: str = None, service: str = None, month: str = None, limit: int = None
    ) -> pd.DataFrame:
        """
        Analyze ridership trends over time (checkins/checkouts).

        Args:
            route_id: Optional route ID to filter by
            service: Optional service type
            month: Optional month to filter by (e.g., 'July 2025')
            limit: Optional maximum number of results (default: no limit for trends)

        Returns:
            DataFrame with ridership trends across months
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_monthly_data(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by route_id if provided
        if route_id:
            df = df[df["Route"].astype(str) == str(route_id)]

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Select relevant columns
        columns = [
            "Month",
            "Route",
            "Service",
            "Checkins",
            "Checkouts",
            "Checkins / Rev Km",
            "Avg Fare",
            "Operated Rev Trips",
        ]
        available_columns = [col for col in columns if col in df.columns]
        result = df[available_columns].copy()

        # Sort by Month
        if "Month" in result.columns:
            result = result.sort_values("Month")

        # Apply limit if specified (usually not for trends, but available if needed)
        if limit:
            result = result.head(limit)

        return result

    def get_revenue_analysis(
        self,
        route_id: str = None,
        service: str = None,
        month: str = None,
        limit: int = 20,
    ) -> pd.DataFrame:
        """
        Analyze revenue performance by route.

        Args:
            route_id: Optional route ID
            service: Optional service type
            month: Optional month to filter by
            limit: Maximum number of results

        Returns:
            DataFrame with revenue analysis
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_monthly_data(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by route_id if provided
        if route_id:
            df = df[df["Route"].astype(str) == str(route_id)]

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Select relevant columns
        columns = [
            "Month",
            "Route",
            "Service",
            "Unsettled Revenue",
            "Rev / Rev Km",
            "Avg Fare",
            "Checkins",
            "Driven Rev Km",
        ]
        available_columns = [col for col in columns if col in df.columns]
        result = df[available_columns].copy()

        # Sort by revenue descending
        if "Unsettled Revenue" in result.columns:
            result = result.sort_values("Unsettled Revenue", ascending=False)

        return result.head(limit)

    def get_cost_efficiency(
        self, route_id: str = None, service: str = None, month: str = None, limit: int = 20
    ) -> pd.DataFrame:
        """
        Analyze cost efficiency metrics.

        Args:
            route_id: Optional route ID to filter by
            service: Optional service type
            month: Optional month to filter by
            limit: Maximum number of results

        Returns:
            DataFrame with cost efficiency analysis
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_monthly_data(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by route_id if provided
        if route_id:
            df = df[df["Route"].astype(str) == str(route_id)]

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Select relevant columns
        columns = [
            "Month",
            "Route",
            "Service",
            "Cost / Rev Km",
            "Avg Daily Cost",
            "Driven Rev Km",
            "Driven Dead Km",
            "Driven Dead %",
        ]
        available_columns = [col for col in columns if col in df.columns]
        result = df[available_columns].copy()

        # Sort by Cost / Rev Km ascending (lower is better)
        if "Cost / Rev Km" in result.columns:
            result = result.sort_values("Cost / Rev Km", ascending=True)

        return result.head(limit)

    def get_service_summary(self, service: str, month: str = None) -> pd.DataFrame:
        """
        Get summary statistics for a service type (Urban/Intercity/Feeder).

        Args:
            service: Service type to analyze
            month: Optional specific month (default: all months)

        Returns:
            DataFrame with service summary from Totals Summary sheet
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_totals_summary(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS totals summary available"]})

        # Filter by service
        df = df[df["Service"].str.lower() == service.lower()]

        if df.empty:
            return pd.DataFrame({"Message": [f"No data found for service {service}"]})

        return df

    def get_top_routes_by_kpi(
        self, kpi: str, service: str = None, limit: int = 10, ascending: bool = False
    ) -> pd.DataFrame:
        """
        Get top routes ranked by a specific KPI.

        Args:
            kpi: KPI column name (e.g., 'OTP%', 'Load Factor', 'CRR', 'Checkins')
            service: Optional service type filter
            limit: Number of top routes to return
            ascending: Sort order (False = descending/highest first)

        Returns:
            DataFrame with top routes by KPI
        """
        df = self.data_loader.get_monthly_data()

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Check if KPI exists
        if kpi not in df.columns:
            available_kpis = [
                col
                for col in df.columns
                if any(
                    k in col
                    for k in ["OTP", "Load", "CRR", "Checkins", "Revenue", "Cost"]
                )
            ]
            return pd.DataFrame(
                {
                    "Message": [f'KPI "{kpi}" not found'],
                    "Available KPIs": [", ".join(available_kpis[:10])],
                }
            )

        # Sort by KPI
        result = df.sort_values(kpi, ascending=ascending)

        # Select relevant columns
        columns = [
            "Route",
            "Service",
            "Month",
            kpi,
            "Operated Rev Trips",
            "Driven Rev Km",
        ]
        available_columns = [col for col in columns if col in result.columns]

        return result[available_columns].head(limit)

    def get_route_performance(self, route_id: str, month: str = None) -> pd.DataFrame:
        """
        Get comprehensive performance metrics for a specific route.

        Args:
            route_id: Route ID to analyze
            month: Optional month filter

        Returns:
            DataFrame with all performance metrics for the route
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_monthly_data(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No TTSS data available"]})

        # Filter by route_id
        df = df[df["Route"].astype(str) == str(route_id)]

        if df.empty:
            return pd.DataFrame({"Message": [f"No data found for route {route_id}"]})

        # Return all columns for comprehensive view
        return df

    def analyze_weekend_vs_weekday(
        self, service: str = None, month: str = None
    ) -> pd.DataFrame:
        """
        Compare weekend vs weekday performance using Daily Summary data.

        Note: Daily data is aggregated by Service only, not by individual routes.

        Args:
            service: Optional service type filter (Urban/Intercity/Feeder/Seasonal)
            month: Optional month filter

        Returns:
            DataFrame comparing weekend vs weekday metrics
        """
        months_filter = [month] if month else None
        df = self.data_loader.get_daily_summary(months=months_filter)

        if df.empty:
            return pd.DataFrame({"Message": ["No daily summary data available"]})

        # Filter by service if provided
        if service:
            df = df[df["Service"].str.lower() == service.lower()]

        # Identify weekends (assuming 'Day' column has day names)
        if "Day" in df.columns:
            df["Is_Weekend"] = (
                df["Day"].str.strip().isin(["Sat", "Sun", "Saturday", "Sunday"])
            )

            # Group by weekend/weekday
            grouped = (
                df.groupby("Is_Weekend")
                .agg(
                    {
                        "Checkins": "sum",
                        "OTP%": "mean",
                        "Load Factor": "mean",
                        "Operated Rev Trips": "sum",
                        "Cancels": "sum",
                    }
                )
                .round(2)
            )

            grouped.index = ["Weekday", "Weekend"]
            return grouped.reset_index().rename(columns={"Is_Weekend": "Period"})
        else:
            return pd.DataFrame(
                {"Message": ["Day column not available for weekend analysis"]}
            )
