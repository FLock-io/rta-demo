import json
from typing import Dict, Any
from openai import OpenAI
import os


class LLMPlanner:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        self.available_functions = [
            "get_route_statistics",
            "get_stop_information",
            "analyze_route_coverage",
            "get_busiest_stops",
            "calculate_route_distances",
            "get_stop_accessibility",
            "analyze_service_frequency",
            "generate_route_map",
            "get_transfer_points",
            "analyze_network_connectivity"
        ]

    def generate_plan(self, user_query: str) -> Dict[str, Any]:
        """Generate execution plan based on user query using function calling."""

        # Define function schemas for the LLM
        function_schemas = self._get_function_schemas()

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert RTA transit data analyst. Analyze user queries and determine which functions to call to provide comprehensive analysis. You can call multiple functions in sequence to build a complete analysis plan."
                    },
                    {"role": "user", "content": user_query}
                ],
                functions=function_schemas,
                function_call="auto",
                temperature=0.1,
            )

            # Extract function calls from response
            plan = self._extract_plan_from_function_calls(response, user_query)
            return plan

        except Exception as e:
            # Fallback plan in case of API errors
            return self._create_fallback_plan(user_query, error=str(e))

    def _create_fallback_plan(self, query: str, error: str = None) -> Dict[str, Any]:
        """Create a basic fallback plan when LLM is unavailable."""

        steps = []

        # Basic heuristics for common queries
        if any(word in query.lower() for word in ["busy", "popular", "most used"]):
            steps.append(
                {
                    "description": "Identify busiest stops/stations",
                    "function": "get_busiest_stops",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if any(word in query.lower() for word in ["route", "coverage", "network"]):
            steps.append(
                {
                    "description": "Analyze route coverage",
                    "function": "analyze_route_coverage",
                    "parameters": {},
                    "output_type": "chart",
                }
            )

        if any(word in query.lower() for word in ["statistic", "summary", "overview"]):
            steps.append(
                {
                    "description": "Get route statistics",
                    "function": "get_route_statistics",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if not steps:
            steps.append(
                {
                    "description": "Get general route statistics",
                    "function": "get_route_statistics",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        return {
            "query": query,
            "interpretation": f"Basic analysis requested{' (LLM unavailable: ' + error + ')' if error else ''}",
            "steps": steps,
        }

    def _get_function_schemas(self) -> list:
        """Generate OpenAI function schemas for all available functions."""

        function_schemas = [
            {
                "name": "get_route_statistics",
                "description": "Get basic statistics about routes, optionally filtered by route type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_type": {
                            "type": "string",
                            "description": "Type of route to filter by ('metro', 'bus', or specific route type)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_stop_information",
                "description": "Get information about transit stops, optionally search by name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stop_name": {
                            "type": "string",
                            "description": "Name or partial name of stop to search for"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of stops to return (default: 50)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "analyze_route_coverage",
                "description": "Show all transit stops on a map",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_busiest_stops",
                "description": "Get the busiest stops based on trip frequency",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of top stops to return (default: 20)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "calculate_route_distances",
                "description": "Calculate approximate distances for all routes",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_stop_accessibility",
                "description": "Get count of stops per zone",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "analyze_service_frequency",
                "description": "Count trips per route, optionally filter by route type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_type": {
                            "type": "string",
                            "description": "Type of route to filter by ('metro' or 'bus')"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "generate_route_map",
                "description": "Draw route shapes on an interactive map",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_routes": {
                            "type": "integer",
                            "description": "Maximum number of routes to display (default: 10)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_transfer_points",
                "description": "Get all transfer points between routes",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "analyze_network_connectivity",
                "description": "Analyze overall network connectivity statistics",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

        return function_schemas

    def _extract_plan_from_function_calls(self, response, user_query: str) -> Dict[str, Any]:
        """Extract execution plan from OpenAI function calling response."""

        steps = []
        message = response.choices[0].message

        # Handle single function call
        if hasattr(message, 'function_call') and message.function_call:
            function_call = message.function_call
            step = {
                "description": f"Execute {function_call.name}",
                "function": function_call.name,
                "parameters": json.loads(function_call.arguments) if function_call.arguments else {},
                "output_type": self._determine_output_type(function_call.name),
                "completed": False
            }
            steps.append(step)

        # Handle multiple function calls (if supported in future)
        elif hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.type == 'function':
                    function_call = tool_call.function
                    step = {
                        "description": f"Execute {function_call.name}",
                        "function": function_call.name,
                        "parameters": json.loads(function_call.arguments) if function_call.arguments else {},
                        "output_type": self._determine_output_type(function_call.name),
                        "completed": False
                    }
                    steps.append(step)

        # If no function calls, create fallback
        if not steps:
            return self._create_fallback_plan(user_query)

        return {
            "query": user_query,
            "interpretation": f"LLM generated {len(steps)} step(s) for analysis",
            "steps": steps
        }

    def _determine_output_type(self, function_name: str) -> str:
        """Determine the output type based on function name."""

        chart_functions = ["analyze_route_coverage", "generate_route_map"]
        dataframe_functions = [
            "get_route_statistics", "get_stop_information", "get_busiest_stops",
            "calculate_route_distances", "get_stop_accessibility", "analyze_service_frequency",
            "get_transfer_points", "analyze_network_connectivity"
        ]

        if function_name in chart_functions:
            return "chart"
        elif function_name in dataframe_functions:
            return "dataframe"
        else:
            return "text"
