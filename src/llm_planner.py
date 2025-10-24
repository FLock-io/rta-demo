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
        # Load API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file or environment.")
        
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
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
            "generate_stops_map",
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
            "plot_daily_kpi_trends",
            "plot_month_comparison",
            "plot_quarterly_comparison",
            # Advanced querying functions
            "query_multi_month_data",
            "aggregate_monthly_data",
            "calculate_percentage_change",
            # SQL-based querying
            "execute_sql_query",
        ]

    def generate_plan(self, user_query: str) -> Dict[str, Any]:
        """Generate execution plan based on user query using function calling."""

        # First, ask LLM to identify assumptions and ambiguities
        assumptions_prompt = f"""Analyze this user query for SIGNIFICANT assumptions or ambiguities that could lead to different results:

Query: "{user_query}"

ONLY flag assumptions if they are:
1. Ambiguous metrics (e.g., "efficient" could mean cost-efficient, revenue-efficient, time-efficient)
2. Unclear ranking/ordering criteria (e.g., "best", "worst", "top" without specifying the metric)
3. Missing critical filters that could drastically change results
4. Multiple valid interpretations that would produce different answers

DO NOT flag minor contextual details or standard assumptions that don't change the answer significantly.

Examples:
- "Which route is most efficient?" → HAS ASSUMPTIONS (efficiency metric unclear)
- "What is route name for 1004?" → NO ASSUMPTIONS (straightforward lookup)
- "Show stops in zone 5" → NO ASSUMPTIONS (clear request)
- "Which routes are performing poorly?" → HAS ASSUMPTIONS (performance metric unclear)

Format your response as a JSON object:
{{
  "has_assumptions": true/false,
  "assumptions": ["only significant assumptions that affect the answer"],
  "interpretation": "brief explanation of how ambiguous terms will be interpreted (only if has_assumptions is true)"
}}"""

        try:
            assumptions_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": assumptions_prompt}],
                temperature=0.3,
            )
            
            assumptions_text = assumptions_response.choices[0].message.content
            # Try to parse as JSON
            import json
            import re
            try:
                # Extract JSON from markdown code blocks if present
                json_match = re.search(r'```json\s*(.*?)\s*```', assumptions_text, re.DOTALL)
                if json_match:
                    assumptions_text = json_match.group(1)
                
                assumptions_data = json.loads(assumptions_text)
            except:
                # Fallback if not valid JSON
                assumptions_data = {
                    "has_assumptions": False,
                    "assumptions": [],
                    "interpretation": assumptions_text
                }
        except Exception as e:
            # Silently fallback if assumption analysis fails
            assumptions_data = {
                "has_assumptions": False,
                "assumptions": [],
                "interpretation": "Standard interpretation"
            }

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
            
            # Add assumptions to the plan
            plan["assumptions"] = assumptions_data
            
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
                "description": "Get stops by zone - either all zones (counts) or specific zone (stop details). Use zone_id to filter for specific zone.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zone_id": {
                            "type": "string",
                            "description": "Specific zone ID to filter stops (e.g., '005', '001'). If not provided, returns counts for all zones.",
                        }
                    },
                    "required": [],
                },
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
                "description": "Draw route shapes on an interactive map. Use this for ANY query asking to show, draw, map, visualize, or display routes geographically.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific route IDs to display (e.g., ['E100', '28']). If provided, shows only these routes.",
                        },
                        "max_routes": {
                            "type": "integer",
                            "description": "Maximum number of routes to display when route_ids not specified (default: 10)",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "generate_stops_map",
                "description": "Plot stops on an interactive map, optionally filtered by zone(s). Use this for queries asking to show/map/plot stops, or to visualize zones geographically. CRITICAL: Use this for 'show stops in zone X', 'map zone 5', 'plot all stops in zone 2', etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "zone_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Optional list of zone IDs to filter (e.g., [5], [2, 3]). If provided, shows only stops in these zones.",
                        },
                        "max_stops": {
                            "type": "integer",
                            "description": "Maximum number of stops to display when zone_ids not specified (default: 100)",
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
                "description": "Analyze On-Time Performance (OTP%) for routes from TTSS data. Shows percentage of on-time stops, late stops, early stops. ALWAYS use month parameter for specific month queries.",
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
                            "description": "Specific month to filter by (e.g., 'June 2025', 'July 2025', 'December 2024'). Use this for month-specific queries.",
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
                "description": "Analyze revenue performance by route from TTSS data. Shows total revenue, revenue per km, average fare. ALWAYS use month parameter for specific month queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "route_id": {
                            "type": "string",
                            "description": "Specific route ID (e.g., 'E100', '10')",
                        },
                        "service": {
                            "type": "string", 
                            "description": "Service type: 'Urban', 'Intercity', 'Feeder', 'Seasonal'"
                        },
                        "month": {
                            "type": "string",
                            "description": "Specific month to filter by (e.g., 'June 2025', 'July 2025', 'December 2024'). Use this for month-specific queries.",
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
                "description": "Get top routes ranked by a specific KPI from TTSS data (e.g., OTP%, Load Factor, CRR, Checkins, Revenue). IMPORTANT: If user specifies month(s), you MUST include them!",
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
                        "months": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional month(s) filter - single month ['August 2025'] or multiple months ['July 2025', 'August 2025']. CRITICAL: If user mentions specific month(s), you MUST include this parameter!",
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
                "description": "Plot MONTHLY KPI trends as interactive line charts. Use this for monthly aggregated data over multiple months. ALWAYS use months parameter for date range queries.",
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
                        },
                        "months": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific months to filter (e.g., ['May 2025', 'June 2025', 'July 2025', 'August 2025']). Use this for date range queries like 'from May to August'.",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "plot_daily_kpi_trends",
                "description": "Plot DAILY KPI trends within a single month. Use this when user asks for 'daily' data or day-by-day trends within a month. CRITICAL: Use this for queries like 'daily revenue in August', 'day by day performance', 'plot daily unsettled revenue for August'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "month": {
                            "type": "string",
                            "description": "Month to plot daily trends for (e.g., 'August 2025'). REQUIRED.",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter (e.g., 'Urban', 'Intercity', 'Express')",
                        },
                        "kpis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific KPIs to plot. Available: 'Unsettled Revenue', 'OTP%', 'Load Factor', 'Checkins', 'Checkouts', 'CRR', etc.",
                        }
                    },
                    "required": ["month"],
                },
            },
            {
                "name": "plot_month_comparison",
                "description": "Plot comparison between two specific months (e.g., July vs August). Use this for month-to-month comparisons.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "month1": {
                            "type": "string",
                            "description": "First month for comparison (e.g., 'July 2025', 'August 2025')",
                        },
                        "month2": {
                            "type": "string",
                            "description": "Second month for comparison (e.g., 'July 2025', 'August 2025')",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter",
                        },
                        "kpis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific KPIs to compare. If not specified, compares default KPIs.",
                        }
                    },
                    "required": ["month1", "month2"],
                },
            },
            {
                "name": "plot_quarterly_comparison",
                "description": "Plot comparison between two quarters (e.g., Q1 vs Q2). Use this for quarterly comparisons.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "quarter1": {
                            "type": "string",
                            "description": "First quarter for comparison (e.g., 'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2024')",
                        },
                        "quarter2": {
                            "type": "string",
                            "description": "Second quarter for comparison (e.g., 'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2024')",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter",
                        },
                        "kpis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific KPIs to compare. If not specified, compares default KPIs.",
                        }
                    },
                    "required": ["quarter1", "quarter2"],
                },
            },
            {
                "name": "query_multi_month_data",
                "description": "Query multiple months of data with SQL-like operations. Use this for flexible data querying across specific months with filtering, grouping, and aggregation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "months": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of months to query (e.g., ['July 2025', 'September 2024'])",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter (Urban, Intercity, Feeder, Seasonal)",
                        },
                        "route_id": {
                            "type": "string",
                            "description": "Optional route ID filter",
                        },
                        "kpis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of KPIs to include (e.g., ['Unsettled Revenue', 'OTP%', 'Load Factor'])",
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional dictionary of additional filters",
                        },
                        "group_by": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of columns to group by (e.g., ['Month', 'Service'])",
                        },
                        "aggregation": {
                            "type": "string",
                            "description": "Aggregation method: 'sum', 'mean', 'max', 'min', 'count' (default: 'sum')",
                        },
                    },
                    "required": ["months"],
                },
            },
            {
                "name": "aggregate_monthly_data",
                "description": "Aggregate data across multiple months. Use this for getting totals, averages, or other aggregations across specific months.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "months": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of months to aggregate (e.g., ['July 2025', 'September 2024'])",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter (Urban, Intercity, Feeder, Seasonal)",
                        },
                        "kpis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of KPIs to aggregate (e.g., ['Unsettled Revenue', 'OTP%'])",
                        },
                        "aggregation": {
                            "type": "string",
                            "description": "Aggregation method: 'sum', 'mean', 'max', 'min' (default: 'sum')",
                        },
                    },
                    "required": ["months"],
                },
            },
            {
                "name": "calculate_percentage_change",
                "description": "Calculate percentage change between two months for specified KPIs. Use this for queries asking for percentage change, growth rate, or change analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "month1": {
                            "type": "string",
                            "description": "First month (baseline) for comparison (e.g., 'September 2024')",
                        },
                        "month2": {
                            "type": "string",
                            "description": "Second month (comparison) for comparison (e.g., 'December 2024')",
                        },
                        "service": {
                            "type": "string",
                            "description": "Optional service type filter (Urban, Intercity, Feeder, Seasonal)",
                        },
                        "kpis": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of KPIs to calculate change for (e.g., ['Unsettled Revenue', 'OTP%'])",
                        },
                        "route_id": {
                            "type": "string",
                            "description": "Optional route ID filter",
                        },
                    },
                    "required": ["month1", "month2"],
                },
            },
            {
                "name": "execute_sql_query",
                "description": """Execute SQL query on transit data for DATA ANALYSIS ONLY. 

⚠️ DO NOT USE THIS FOR PLOTTING! This returns a data table, not a chart. For plotting, use plot_monthly_kpi_trends, plot_month_comparison, or plot_quarterly_comparison.

Use this for: percentage changes, aggregations, data comparisons, calculating totals/sums.

Available Tables:
- totals_summary/service_data: Service-level aggregates (Month, Service, 'Unsettled Revenue', 'OTP%', 'Load Factor', 'CRR', 'Checkins', etc.)
  * Month format: "July 2025" (space between month and year)
- monthly_data/route_data: Route-level data (Month, Route, Service, 'Unsettled Revenue', 'OTP%', 'Load Factor', 'Plan Rev Trips', 'Operated Rev Trips', etc.)
  * Month format: "July-2025" (hyphen between month and year)
- daily_summary: Service-level DAILY aggregates (Date, Day, Service, 'Unsettled Revenue', 'OTP%', 'Load Factor', 'CRR', 'Checkins', etc.)
  * Date format: datetime (e.g., '2025-08-15')
- daily_data: Route-level DAILY data (Date, Day, Route, Service, 'Unsettled Revenue', 'OTP%', 'Load Factor', etc.)
  * Date format: datetime (e.g., '2025-08-15')
- routes: GTFS routes (route_id, route_short_name, route_long_name, route_type)
- stops: GTFS stops (stop_id, stop_name, stop_lat, stop_lon, zone_id)
- trips: GTFS trips (trip_id, route_id, service_id, trip_headsign, direction_id, shape_id)
- stop_times: GTFS stop times (trip_id, stop_id, arrival_time, departure_time, stop_sequence)
- calendar: GTFS service calendar (service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date)
- calendar_dates: GTFS calendar exceptions (service_id, date, exception_type)
- shapes: GTFS route shapes (shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence)
- transfers: GTFS transfer rules (from_stop_id, to_stop_id, transfer_type, min_transfer_time)
- agency: GTFS agency info (agency_id, agency_name, agency_url, agency_timezone)

CRITICAL: Month format differs between tables!
- totals_summary uses: "July 2025" (WITH SPACE)
- monthly_data uses: "July-2025" (WITH HYPHEN)
- daily_summary/daily_data use: Date column (datetime)

Note: Column names with spaces must be quoted with double quotes in SQL (e.g., "Unsettled Revenue", "OTP%", "Plan Rev Trips")

Example Queries:

SINGLE TABLE Queries:
- Percentage change: SELECT Service, ((MAX(CASE WHEN Month='December 2024' THEN "Unsettled Revenue" END) - MAX(CASE WHEN Month='September 2024' THEN "Unsettled Revenue" END)) / MAX(CASE WHEN Month='September 2024' THEN "Unsettled Revenue" END) * 100) as pct_change FROM totals_summary WHERE Service='Urban' GROUP BY Service
- Month comparison: SELECT Month, Service, "Unsettled Revenue" FROM totals_summary WHERE Month IN ('July 2025', 'August 2025')
- Aggregation: SELECT Service, SUM("Unsettled Revenue") as total FROM totals_summary WHERE Month IN ('July 2025', 'August 2025') GROUP BY Service
- Daily data: SELECT Date, Day, SUM("Unsettled Revenue") as revenue FROM daily_summary WHERE strftime('%Y-%m', Date) = '2025-08' GROUP BY Date ORDER BY revenue DESC LIMIT 1

HYBRID (GTFS + TTSS) Queries - REQUIRES JOINS:
- Revenue by zone (MUST JOIN stops): SELECT s.zone_id, COUNT(DISTINCT m.Route) as routes, SUM(m."Unsettled Revenue") as revenue FROM monthly_data m JOIN routes r ON m.Route = r.route_short_name JOIN trips t ON r.route_id = t.route_id JOIN stop_times st ON t.trip_id = st.trip_id JOIN stops s ON st.stop_id = s.stop_id WHERE m.Month='July-2025' GROUP BY s.zone_id ORDER BY revenue DESC
- Performance by route type (MUST JOIN routes): SELECT CASE WHEN r.route_type=1 THEN 'Metro' WHEN r.route_type=3 THEN 'Bus' ELSE 'Other' END as type, AVG(m."OTP%") as avg_otp FROM monthly_data m JOIN routes r ON m.Route = r.route_short_name WHERE m.Month='August-2025' GROUP BY type
- Weekday vs weekend (MUST JOIN calendar): SELECT CASE WHEN c.saturday=1 OR c.sunday=1 THEN 'Weekend' ELSE 'Weekday' END as pattern, AVG(m."OTP%") as avg_otp FROM monthly_data m JOIN routes r ON m.Route = r.route_short_name JOIN trips t ON r.route_id = t.route_id JOIN calendar c ON t.service_id = c.service_id WHERE m.Month='August-2025' GROUP BY pattern

CRITICAL: zone_id is ONLY in stops table, route_type is ONLY in routes table, service schedules are ONLY in calendar table. You MUST JOIN these tables to access these columns!""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {
                            "type": "string",
                            "description": "SQL query to execute. Use double quotes for column names with spaces.",
                        },
                        "months": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of months to load data for (improves performance). Example: ['September 2024', 'December 2024']",
                        },
                    },
                    "required": ["sql_query"],
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

        chart_functions = ["analyze_route_coverage", "generate_route_map", "generate_stops_map", "plot_monthly_kpi_trends", "plot_daily_kpi_trends", "plot_month_comparison", "plot_quarterly_comparison"]
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
            # Advanced querying functions
            "query_multi_month_data",
            "aggregate_monthly_data",
            "calculate_percentage_change",
            # SQL-based querying
            "execute_sql_query",
        ]

        if function_name in chart_functions:
            return "chart"
        elif function_name in dataframe_functions:
            return "dataframe"
        else:
            return "text"
