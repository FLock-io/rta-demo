import pandas as pd
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
from .data_loader import DataLoader

class ContextManager:
    """
    Manages local context extraction and dynamic prompt generation.
    Identifies entities (routes, stops, dates) in user queries without sending data to LLM.
    """
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.routes_cache = None
        self.stops_cache = None
        self.months_cache = None
        
        # Initialize caches
        self._refresh_cache()
        
    def _refresh_cache(self):
        """Load data into memory for quick lookup."""
        # Cache Routes
        routes_df = self.data_loader.get_routes()
        if not routes_df.empty:
            self.routes_cache = {
                'ids': set(routes_df['route_id'].astype(str).str.lower()),
                'short_names': set(routes_df['route_short_name'].astype(str).str.lower()),
                'map': routes_df.set_index('route_short_name')[['route_id', 'route_long_name', 'route_type_desc']].to_dict('index')
            }
            # Also map route_id to details
            self.routes_id_map = routes_df.set_index('route_id')[['route_short_name', 'route_long_name', 'route_type_desc']].to_dict('index')
        else:
            self.routes_cache = {'ids': set(), 'short_names': set(), 'map': {}}
            self.routes_id_map = {}
            
        # Cache Stops (names only for now to save memory)
        stops_df = self.data_loader.get_stops()
        if not stops_df.empty:
            self.stops_cache = set(stops_df['stop_name'].astype(str).str.lower())
        else:
            self.stops_cache = set()
            
        # Cache Available Months
        self.months_cache = self.data_loader.get_available_months()
        
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract known entities from the query.
        
        Returns:
            Dict containing found routes, stops, months, etc.
        """
        query_lower = query.lower()
        entities = {
            'routes': [],
            'stops': [],
            'months': [],
            'services': [],
            'zones': []
        }
        
        # 1. Extract Routes
        # Check for route short names (e.g., "E100", "28")
        # We look for exact word matches to avoid partial matches (e.g. "10" in "100")
        words = set(re.findall(r'\b\w+\b', query_lower))
        
        for route_name in self.routes_cache['short_names']:
            if route_name in words:
                # Get details
                details = self.routes_cache['map'].get(route_name.upper()) # Original case key
                if not details:
                    # Try finding case-insensitive match in map
                    for key, val in self.routes_cache['map'].items():
                        if key.lower() == route_name:
                            details = val
                            details['route_short_name'] = key
                            break
                
                if details:
                    entities['routes'].append({
                        'id': details.get('route_id'),
                        'short_name': details.get('route_short_name', route_name.upper()),
                        'long_name': details.get('route_long_name'),
                        'type': details.get('route_type_desc')
                    })
                    
        # 2. Extract Months
        # Look for month names and years
        for month_str in self.months_cache:
            if month_str.lower() in query_lower:
                entities['months'].append(month_str)
                
        # 3. Extract Services
        services = ['urban', 'intercity', 'feeder', 'seasonal']
        for service in services:
            if service in query_lower:
                entities['services'].append(service.capitalize())
                
        # 4. Extract Zones
        # Look for "zone X" pattern
        zone_matches = re.findall(r'zone\s+(\d+)', query_lower)
        if zone_matches:
            entities['zones'] = [int(z) for z in zone_matches]
            
        return entities

    def get_context_string(self, query: str) -> str:
        """
        Generate a natural language context string to inject into the prompt.
        """
        entities = self.extract_entities(query)
        context_parts = []
        
        # Routes Context
        if entities['routes']:
            route_descs = []
            for r in entities['routes']:
                route_descs.append(f"{r['short_name']} ({r['type']})")
            context_parts.append(f"User mentioned routes: {', '.join(route_descs)}.")
            
        # Months Context
        if entities['months']:
            context_parts.append(f"User mentioned specific months: {', '.join(entities['months'])}.")
        else:
            # If no specific month mentioned, provide range summary
            if self.months_cache:
                context_parts.append(f"Data available from {self.months_cache[0]} to {self.months_cache[-1]}.")
                
        # Services Context
        if entities['services']:
            context_parts.append(f"User mentioned services: {', '.join(entities['services'])}.")
            
        # Zones Context
        if entities['zones']:
            context_parts.append(f"User mentioned zones: {', '.join(map(str, entities['zones']))}.")
            
        if not context_parts:
            return "No specific entities (routes, months, zones) detected in query."
            
        return " ".join(context_parts)

    def get_system_prompt_context(self) -> str:
        """
        Get general metadata for the system prompt (valid ranges, etc).
        """
        if not self.months_cache:
            return "Data availability: Unknown."
            
        return f"""
Data Availability:
- Date Range: {self.months_cache[0]} to {self.months_cache[-1]}
- Total Months: {len(self.months_cache)}
- Service Types: Urban, Intercity, Feeder, Seasonal
"""
