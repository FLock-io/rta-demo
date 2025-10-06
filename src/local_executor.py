import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import numpy as np
from .data_loader import DataLoader

class LocalExecutor:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.function_map = {
            'get_route_statistics': self.get_route_statistics,
            'get_stop_information': self.get_stop_information,
            'analyze_route_coverage': self.analyze_route_coverage,
            'get_busiest_stops': self.get_busiest_stops,
            'calculate_route_distances': self.calculate_route_distances,
            'get_stop_accessibility': self.get_stop_accessibility,
            'analyze_service_frequency': self.analyze_service_frequency,
            'generate_route_map': self.generate_route_map,
            'get_transfer_points': self.get_transfer_points,
            'analyze_network_connectivity': self.analyze_network_connectivity
        }

    def execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the generated plan step by step."""
        results = []

        for step in plan.get('steps', []):
            function_name = step.get('function')
            parameters = step.get('parameters', {})
            output_type = step.get('output_type', 'text')

            if function_name in self.function_map:
                try:
                    # Filter parameters to only include those accepted by the function
                    import inspect
                    func = self.function_map[function_name]
                    sig = inspect.signature(func)
                    valid_params = {k: v for k, v in parameters.items() if k in sig.parameters}

                    result = func(**valid_params)
                    results.append({
                        'title': step.get('description', function_name),
                        'type': output_type,
                        'data': result,
                        'function': function_name
                    })
                    step['completed'] = True
                except Exception as e:
                    results.append({
                        'title': f"Error in {function_name}",
                        'type': 'text',
                        'content': f"Error: {str(e)}",
                        'function': function_name
                    })
                    step['completed'] = False

        return results

    def get_route_statistics(self, route_type: str = None) -> pd.DataFrame:
        """Get basic statistics about routes."""
        routes = self.data_loader.get_routes()

        # Filter by route type if provided
        if route_type and route_type.lower() == 'metro':
            routes = routes[routes['route_type'] == 1]
        elif route_type and route_type.lower() == 'bus':
            routes = routes[routes['route_type'] == 3]

        return routes[['route_id', 'route_short_name', 'route_long_name', 'route_type_desc']].head(20)

    def get_stop_information(self, stop_name: str = None, limit: int = 50) -> pd.DataFrame:
        """Get information about stops."""
        stops = self.data_loader.get_stops()

        # Filter by stop name if provided
        if stop_name:
            stops = stops[stops['stop_name'].str.contains(stop_name, case=False, na=False)]

        return stops[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].head(limit)

    def analyze_route_coverage(self) -> go.Figure:
        """Show all stops on a map."""
        stops = self.data_loader.get_stops()
        stops = stops.dropna(subset=['stop_lat', 'stop_lon'])

        fig = px.scatter_mapbox(
            stops,
            lat='stop_lat',
            lon='stop_lon',
            hover_name='stop_name',
            zoom=10,
            height=600,
            title="RTA Stop Coverage Map"
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":50,"l":0,"b":0}
        )

        return fig

    def get_busiest_stops(self, limit: int = 20) -> pd.DataFrame:
        """Identify busiest stops based on trip frequency."""
        stop_times = self.data_loader.get_stop_times()
        stops = self.data_loader.get_stops()

        # Count trips per stop
        trip_counts = stop_times.groupby('stop_id').size().reset_index(name='trip_count')

        # Merge with stop information
        result = trip_counts.merge(stops[['stop_id', 'stop_name']], on='stop_id', how='left')

        # Sort by trip count
        return result.sort_values('trip_count', ascending=False).head(limit)

    def calculate_route_distances(self) -> pd.DataFrame:
        """Calculate approximate distances for all routes."""
        shapes = self.data_loader.get_shapes()
        distances = []

        for shape_id in shapes['shape_id'].unique()[:20]:  # Limit to first 20
            shape_points = shapes[shapes['shape_id'] == shape_id].sort_values('shape_pt_sequence')

            if len(shape_points) > 1:
                lats = shape_points['shape_pt_lat'].values
                lons = shape_points['shape_pt_lon'].values

                total_distance = 0
                for i in range(1, len(lats)):
                    lat_diff = lats[i] - lats[i-1]
                    lon_diff = lons[i] - lons[i-1]
                    distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111
                    total_distance += distance

                distances.append({
                    'shape_id': shape_id,
                    'distance_km': round(total_distance, 2)
                })

        return pd.DataFrame(distances)

    def get_stop_accessibility(self) -> pd.DataFrame:
        """Count stops by zone."""
        stops = self.data_loader.get_stops()

        if 'zone_id' in stops.columns:
            zone_counts = stops['zone_id'].value_counts()
            return pd.DataFrame({
                'Zone': zone_counts.index,
                'Stop Count': zone_counts.values
            })
        else:
            return pd.DataFrame({'Message': ['No zone information available']})

    def analyze_service_frequency(self, route_type: str = None) -> pd.DataFrame:
        """Count trips per route."""
        trips = self.data_loader.get_trips()
        routes = self.data_loader.get_routes()

        # Filter by route type if provided
        if route_type and route_type.lower() == 'metro':
            routes = routes[routes['route_type'] == 1]
        elif route_type and route_type.lower() == 'bus':
            routes = routes[routes['route_type'] == 3]

        # Count trips per route
        trip_counts = trips.groupby('route_id').size().reset_index(name='trip_count')

        # Merge with route information
        result = trip_counts.merge(
            routes[['route_id', 'route_short_name', 'route_type_desc']],
            on='route_id',
            how='inner'
        )

        return result.sort_values('trip_count', ascending=False).head(20)

    def generate_route_map(self, max_routes: int = 10) -> go.Figure:
        """Draw route shapes on a map."""
        shapes = self.data_loader.get_shapes()
        fig = go.Figure()

        # Plot first N route shapes
        for shape_id in shapes['shape_id'].unique()[:max_routes]:
            shape_points = shapes[shapes['shape_id'] == shape_id].sort_values('shape_pt_sequence')

            fig.add_trace(go.Scattermapbox(
                lat=shape_points['shape_pt_lat'],
                lon=shape_points['shape_pt_lon'],
                mode='lines',
                name=str(shape_id),
                line=dict(width=3)
            ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=25.2, lon=55.3),
                zoom=10
            ),
            height=600,
            title="RTA Route Network"
        )

        return fig

    def get_transfer_points(self) -> pd.DataFrame:
        """Get all transfer points."""
        transfers = self.data_loader.get_transfers()
        stops = self.data_loader.get_stops()

        # Merge with stop names
        result = transfers.merge(
            stops[['stop_id', 'stop_name']],
            left_on='from_stop_id',
            right_on='stop_id',
            how='left'
        ).rename(columns={'stop_name': 'from_stop_name'})

        result = result.merge(
            stops[['stop_id', 'stop_name']],
            left_on='to_stop_id',
            right_on='stop_id',
            how='left'
        ).rename(columns={'stop_name': 'to_stop_name'})

        return result[['from_stop_name', 'to_stop_name', 'transfer_type', 'min_transfer_time']].head(50)

    def analyze_network_connectivity(self) -> pd.DataFrame:
        """Get basic network statistics."""
        stops = self.data_loader.get_stops()
        routes = self.data_loader.get_routes()
        transfers = self.data_loader.get_transfers()

        return pd.DataFrame({
            'Metric': ['Total Stops', 'Total Routes', 'Transfer Points'],
            'Count': [len(stops), len(routes), len(transfers)]
        })
