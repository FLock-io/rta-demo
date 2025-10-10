import json
from typing import Dict, Any
from openai import OpenAI
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from prompts import RTAPrompts


class LLMPlanner:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")

        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        self.available_functions = [
            # GTFS functions
            "get_route_statistics",
            "get_stop_information",
            "analyze_route_coverage",
            "get_busiest_stops",
            "calculate_route_distances",
            "get_stop_accessibility",
            "analyze_service_frequency",
            "generate_route_map",
            "get_transfer_points",
            "analyze_network_connectivity",
            # TTSS KPI functions
            "get_otp_analysis",
            "get_load_factor_analysis",
            "get_crr_analysis",
            "get_ridership_trends",
            "get_revenue_analysis",
            "get_cost_efficiency",
            "get_service_summary",
            "get_top_routes_by_kpi",
            "get_route_performance",
            "analyze_weekend_vs_weekday",
            # Visualization functions
            "plot_monthly_kpi_trends",
        ]

    def generate_plan(self, user_query: str) -> Dict[str, Any]:
        """Generate execution plan based on user query using function calling."""

        # Define function schemas for the LLM
        function_schemas = self._get_function_schemas()

        try:
            # Get system prompt from prompts.py
            system_prompt = RTAPrompts.get_system_planning_prompt(
                self.available_functions
            )

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
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
        query_lower = query.lower()

        # TTSS KPI queries
        if any(
            word in query_lower for word in ["otp", "on-time", "on time", "punctuality"]
        ):
            steps.append(
                {
                    "description": "Analyze On-Time Performance",
                    "function": "get_otp_analysis",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if any(
            word in query_lower for word in ["load factor", "capacity", "utilization"]
        ):
            steps.append(
                {
                    "description": "Analyze Load Factor",
                    "function": "get_load_factor_analysis",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if any(
            word in query_lower
            for word in ["crr", "cost recovery", "subsidy", "profitability"]
        ):
            steps.append(
                {
                    "description": "Analyze Cost Recovery Ratio",
                    "function": "get_crr_analysis",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if any(
            word in query_lower
            for word in ["ridership", "passenger", "checkin", "trend"]
        ):
            steps.append(
                {
                    "description": "Analyze ridership trends",
                    "function": "get_ridership_trends",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if any(word in query_lower for word in ["revenue", "income", "fare"]):
            steps.append(
                {
                    "description": "Analyze revenue",
                    "function": "get_revenue_analysis",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if any(word in query_lower for word in ["cost", "expense", "efficiency"]):
            steps.append(
                {
                    "description": "Analyze cost efficiency",
                    "function": "get_cost_efficiency",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        # GTFS queries
        if any(word in query_lower for word in ["busy", "popular", "most used"]):
            steps.append(
                {
                    "description": "Identify busiest stops/stations",
                    "function": "get_busiest_stops",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        if any(word in query_lower for word in ["map", "coverage", "location"]):
            steps.append(
                {
                    "description": "Analyze route coverage",
                    "function": "analyze_route_coverage",
                    "parameters": {},
                    "output_type": "chart",
                }
            )

        if any(
            word in query_lower
            for word in ["route", "statistic", "summary", "overview"]
        ):
            steps.append(
                {
                    "description": "Get route statistics",
                    "function": "get_route_statistics",
                    "parameters": {},
                    "output_type": "dataframe",
                }
            )

        # Default fallback
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
                            "description": "Type of route to filter by ('metro', 'bus', or specific route type)",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "get_stop_information",
                "description": "Get information about transit stops, optionally search by name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stop_name": {
                            "type": "string",
                            "description": "Name or partial name of stop to search for",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of stops to return (default: 50)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "analyze_route_coverage",
                "description": "Show all transit stops on a map",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_busiest_stops",
                "description": "Get the busiest stops based on trip frequency",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of top stops to return (default: 20)",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "calculate_route_distances",
                "description": "Calculate approximate distances for all routes",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "get_stop_accessibility",
                "description": "Get count of stops per zone",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "analyze_service_frequency",
                "description": "Count trips per route, optionally filter by route type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_type": {
                            "type": "string",
                            "description": "Type of route to filter by ('metro' or 'bus')",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_route_map",
                "description": "Draw route shapes on an interactive map",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_routes": {
                            "type": "integer",
                            "description": "Maximum number of routes to display (default: 10)",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "get_transfer_points",
                "description": "Get all transfer points between routes",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            {
                "name": "analyze_network_connectivity",
                "description": "Analyze overall network connectivity statistics",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            # TTSS KPI Functions
            {
                "name": "get_otp_analysis",
                "description": "Analyze On-Time Performance (OTP%) for routes from TTSS data. Shows percentage of on-time stops, late stops, early stops.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Specific route ID to analyze (e.g., '10', 'E100')",
                        },
                        "service": {
                            "type": "string",
                            "description": "Service type: 'Urban', 'Intercity', 'Feeder', or 'Seasonal'",
                        },
                        "month": {
                            "type": "string",
                            "description": "Month to filter by (e.g., 'July 2025', 'December 2024')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_load_factor_analysis",
                "description": "Analyze Load Factor (capacity utilization) for routes from TTSS data. Shows passenger-km vs seat-km ratio.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Specific route ID to analyze",
                        },
                        "service": {
                            "type": "string",
                            "description": "Service type: 'Urban', 'Intercity', 'Feeder', or 'Seasonal'",
                        },
                        "month": {
                            "type": "string",
                            "description": "Month to filter by",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_crr_analysis",
                "description": "Analyze Cost Recovery Ratio (CRR) - revenue vs cost efficiency from TTSS data. Shows revenue per km, cost per km, and subsidy requirements.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Specific route ID to analyze (e.g., '10', 'E100')",
                        },
                        "service": {
                            "type": "string",
                            "description": "Service type to filter by: 'Urban', 'Intercity', 'Feeder', or 'Seasonal'",
                        },
                        "month": {
                            "type": "string",
                            "description": "Month to filter by (e.g., 'July 2025', 'December 2024')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_ridership_trends",
                "description": "Analyze ridership trends over time (checkins/checkouts) from TTSS data across multiple months. Shows monthly progression of passenger volume.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Specific route ID to analyze (e.g., '10', 'E100')",
                        },
                        "service": {
                            "type": "string",
                            "description": "Service type to filter by: 'Urban', 'Intercity', 'Feeder', or 'Seasonal'",
                        },
                        "month": {
                            "type": "string",
                            "description": "Optional month to filter by (e.g., 'July 2025')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Optional limit on number of results (usually not used for trends to show full timeline)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_revenue_analysis",
                "description": "Analyze revenue performance by route from TTSS data. Shows total revenue, revenue per km, average fare.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Specific route ID",
                        },
                        "service": {"type": "string", "description": "Service type"},
                        "month": {
                            "type": "string",
                            "description": "Month to filter by",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_cost_efficiency",
                "description": "Analyze cost efficiency metrics from TTSS data. Shows cost per km, dead km percentage, daily costs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Specific route ID to analyze (e.g., '10', 'E100')",
                        },
                        "service": {
                            "type": "string",
                            "description": "Service type: 'Urban', 'Intercity', 'Feeder', or 'Seasonal'",
                        },
                        "month": {
                            "type": "string",
                            "description": "Month to filter by (e.g., 'July 2025')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 20)",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "get_service_summary",
                "description": "Get summary statistics for a service type (Urban/Intercity/Feeder) from TTSS totals summary.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Service type to analyze: 'Urban', 'Intercity', 'Feeder', or 'Seasonal' (required)",
                        },
                        "month": {
                            "type": "string",
                            "description": "Optional specific month",
                        },
                    },
                    "required": ["service"],
                },
            },
            {
                "name": "get_top_routes_by_kpi",
                "description": "Get top routes ranked by a specific KPI from TTSS data (e.g., OTP%, Load Factor, CRR, Checkins, Revenue).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "kpi": {
                            "type": "string",
                            "description": "KPI column name (required): 'OTP%', 'Load Factor', 'CRR', 'Checkins', 'Unsettled Revenue', 'Cost / Rev Km'",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top routes (default: 10)",
                        },
                        "ascending": {
                            "type": "boolean",
                            "description": "Sort order: false=highest first (default), true=lowest first",
                        },
                    },
                    "required": ["kpi"],
                },
            },
            {
                "name": "get_route_performance",
                "description": "Get comprehensive performance metrics for a specific route from TTSS data. Returns all 33 KPI columns.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Route ID to analyze (required)",
                        },
                        "month": {
                            "type": "string",
                            "description": "Optional month filter",
                        },
                    },
                    "required": ["route_id"],
                },
            },
            {
                "name": "analyze_weekend_vs_weekday",
                "description": "Compare weekend vs weekday performance from TTSS daily summary data. Note: Daily data is aggregated by Service only, not by individual routes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Service type filter: 'Urban', 'Intercity', 'Feeder', or 'Seasonal'",
                        },
                        "month": {
                            "type": "string",
                            "description": "Month filter (e.g., 'July 2025')",
                        },
                    },
                    "required": [],
                },
            },
            {
                "name": "plot_monthly_kpi_trends",
                "description": "Plot monthly KPI trends as interactive line charts. Use this when user asks for charts, graphs, plots, or visualizations of monthly trends.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter",
                        },
                        "kpis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific KPIs to plot. Available: 'OTP%', 'Load Factor', 'CRR', 'Checkins', 'Checkouts', 'Cancels', 'Curtails', 'Operated Rev Trips', 'Driven Rev Km', 'Unsettled Revenue', 'Cost / Rev Km', 'Avg Fare', etc. If not specified, plots default KPIs.",
                        }
                    },
                    "required": [],
                },
            },
        ]

        return function_schemas

    def _extract_plan_from_function_calls(
        self, response, user_query: str
    ) -> Dict[str, Any]:
        """Extract execution plan from OpenAI function calling response."""

        steps = []
        message = response.choices[0].message

        # Handle single function call
        if hasattr(message, "function_call") and message.function_call:
            function_call = message.function_call
            step = {
                "description": f"Execute {function_call.name}",
                "function": function_call.name,
                "parameters": (
                    json.loads(function_call.arguments)
                    if function_call.arguments
                    else {}
                ),
                "output_type": self._determine_output_type(function_call.name),
                "completed": False,
            }
            steps.append(step)

        # Handle multiple function calls (if supported in future)
        elif hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.type == "function":
                    function_call = tool_call.function
                    step = {
                        "description": f"Execute {function_call.name}",
                        "function": function_call.name,
                        "parameters": (
                            json.loads(function_call.arguments)
                            if function_call.arguments
                            else {}
                        ),
                        "output_type": self._determine_output_type(function_call.name),
                        "completed": False,
                    }
                    steps.append(step)

        # If no function calls, create fallback
        if not steps:
            return self._create_fallback_plan(user_query)

        return {
            "query": user_query,
            "interpretation": f"LLM generated {len(steps)} step(s) for analysis",
            "steps": steps,
        }

    def _determine_output_type(self, function_name: str) -> str:
        """Determine the output type based on function name."""

        chart_functions = ["analyze_route_coverage", "generate_route_map", "plot_monthly_kpi_trends"]
        dataframe_functions = [
            # GTFS functions
            "get_route_statistics",
            "get_stop_information",
            "get_busiest_stops",
            "calculate_route_distances",
            "get_stop_accessibility",
            "analyze_service_frequency",
            "get_transfer_points",
            "analyze_network_connectivity",
            # TTSS functions
            "get_otp_analysis",
            "get_load_factor_analysis",
            "get_crr_analysis",
            "get_ridership_trends",
            "get_revenue_analysis",
            "get_cost_efficiency",
            "get_service_summary",
            "get_top_routes_by_kpi",
            "get_route_performance",
            "analyze_weekend_vs_weekday",
        ]

        if function_name in chart_functions:
            return "chart"
        elif function_name in dataframe_functions:
            return "dataframe"
        else:
            return "text"
