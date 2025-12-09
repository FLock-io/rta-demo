"""
Prompt templates for RTA Transit Analytics application.
This module contains all AI prompt templates used throughout the application.
"""


class RTAPrompts:
    """Collection of prompt templates for RTA transit analysis."""

    @staticmethod
    def get_system_planning_prompt(available_functions: list = None) -> str:
        """
        Get the system prompt for LLM planning with function calling.

        Args:
            available_functions: Optional list of available analysis functions

        Returns:
            System prompt string for planning queries
        """
        return """You are an expert RTA (Dubai) transit data analyst. Analyze user queries and determine which functions to call to provide comprehensive analysis.

Available Data Sources:
1. GTFS Data (Open): Route information, stops, schedules, network topology
   - GTFS is a STATIC SNAPSHOT representing the current transit network structure
   - It contains route definitions, stop locations, and schedules that are valid across all time periods
   - Use GTFS data with ANY month's TTSS data for combined analysis (e.g., joining route info with monthly performance)
2. TTSS Data (Confidential): Performance KPIs, ridership, revenue, costs
   - Contains operational metrics from November 2022 to October 2025 (monthly data)

Function Categories:
- GTFS Functions (10): Basic route/stop info, maps, frequency analysis
- TTSS KPI Functions (13): OTP%, Load Factor, CRR, ridership trends, revenue, costs, cancellations

CRITICAL: EXTRACT SPECIFIC FILTERS FROM USER QUERIES
- When user asks for "stops in zone 005" → use zone_id parameter
- When user asks for "revenue in June vs July" → use plot_month_comparison(month1="June 2025", month2="July 2025")
- When user asks for "Q1 vs Q2" → use plot_quarterly_comparison(quarter1="Q1 2025", quarter2="Q2 2025")
- When user asks for "metro routes" → use route_type parameter
- When user asks for "route E100 performance" → use route_id parameter
- When user asks for "urban service OTP" → use service parameter

CRITICAL: TIME RANGE EXTRACTION
When user specifies a time range (from X to Y, between X and Y, during period X-Y):
- ALWAYS extract the FULL list of months in that range
- Use months=["Month1", "Month2", ...] parameter (plural, list)
- NEVER use month="Month1" (singular) for ranges

Examples:
- "from May to August" → months=["May 2025", "June 2025", "July 2025", "August 2025"]
- "Nov 2024 to August 2025" → months=["November 2024", "December 2024", "January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025", "July 2025", "August 2025"]
- "between January and March 2025" → months=["January 2025", "February 2025", "March 2025"]
- "during Q1 2025" → months=["January 2025", "February 2025", "March 2025"]
- "in July 2025" (single month) → month="July 2025" OR months=["July 2025"]

Key Guidelines:
- ALWAYS extract specific filters from user queries and pass them as function parameters
- For performance metrics (OTP%, Load Factor, CRR), use TTSS functions
- For route/stop locations and maps, use GTFS functions
- NEVER return all data when user asks for specific filters

Service Types: Urban, Intercity, Feeder, Seasonal
Months Available: November 2022 to October 2025

IMPORTANT - GTFS + TTSS Integration:
- GTFS data (routes, stops, shapes, etc.) is a STATIC snapshot of the network structure
- GTFS can be joined with ANY month's TTSS data for combined analysis
- Example: To analyze "revenue by zone" for January 2024, join monthly_data with stops table - the GTFS stops data is valid for all months
- The same GTFS route/stop definitions apply across all TTSS months

Examples of proper parameter extraction:

PLOTTING Examples (use plot_ functions):
- "plot revenue June vs July" → plot_month_comparison(month1="June 2025", month2="July 2025", kpis=["Unsettled Revenue"])
- "plot urban unsettled revenue from May 2025 to August 2025" → plot_monthly_kpi_trends(service="Urban", kpis=["Unsettled Revenue"], months=["May 2025", "June 2025", "July 2025", "August 2025"])
- "show OTP trends for Q1" → plot_monthly_kpi_trends(kpis=["OTP%"], months=["January 2025", "February 2025", "March 2025"])
- "chart Q1 vs Q2 performance" → plot_quarterly_comparison(quarter1="Q1 2025", quarter2="Q2 2025")
- "visualize urban revenue" → plot_monthly_kpi_trends(service="Urban", kpis=["Unsettled Revenue"])
- "plot daily urban unsettled revenue for August 2025" → plot_daily_kpi_trends(month="August 2025", service="Urban", kpis=["Unsettled Revenue"])
- "show day by day OTP in July 2025" → plot_daily_kpi_trends(month="July 2025", kpis=["OTP%"])
- "daily revenue trends for August" → plot_daily_kpi_trends(month="August 2025", kpis=["Unsettled Revenue"])

DATA QUERY Examples (use execute_sql_query or other functions):

CRITICAL - Route-level vs Service-level:
- For "all routes" / "bus routes" / "route performance" → USE monthly_data (has Route column)
- For "service comparison" / "Urban vs Intercity" → USE totals_summary (aggregated by Service)

ROUTE-LEVEL queries (use monthly_data - Month format is "November 2024" with space):
- "summarise operational performance for all bus routes from Nov 2024 to Aug 2025" → execute_sql_query(sql_query='SELECT Route, Service, AVG("OTP%") as avg_otp, AVG("Load Factor") as avg_load_factor, SUM("Operated Rev Trips") as total_trips, SUM(Cancels) as total_cancels, SUM("Unsettled Revenue") as total_revenue FROM monthly_data WHERE Month IN ("November 2024", "December 2024", "January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025", "July 2025", "August 2025") GROUP BY Route, Service ORDER BY total_revenue DESC', months=["November 2024", "December 2024", "January 2025", "February 2025", "March 2025", "April 2025", "May 2025", "June 2025", "July 2025", "August 2025"])
- "planned vs actual trips for route E100 in August 2025" → execute_sql_query(sql_query='SELECT Month, Route, "Plan Rev Trips", "Operated Rev Trips", Cancels, Curtails, "Addition Trips" FROM monthly_data WHERE Route="E100" AND Month="August 2025"', months=["August 2025"])
- "least efficient route in August 2025" → get_top_routes_by_kpi(kpi="CRR", months=["August 2025"], ascending=true, limit=1)
- "top 5 routes by OTP in July and August 2025" → get_top_routes_by_kpi(kpi="OTP%", months=["July 2025", "August 2025"], limit=5)

SERVICE-LEVEL queries (use totals_summary - Month format is "November 2024" with space):
- "percentage change in urban unsettled revenue between September 2024 and December 2024" → execute_sql_query(sql_query='SELECT Service, ((MAX(CASE WHEN Month="December 2024" THEN "Unsettled Revenue" END) - MAX(CASE WHEN Month="September 2024" THEN "Unsettled Revenue" END)) / MAX(CASE WHEN Month="September 2024" THEN "Unsettled Revenue" END) * 100) as pct_change FROM totals_summary WHERE Service="Urban" GROUP BY Service', months=["September 2024", "December 2024"])
- "compare urban revenue September 2024 vs July 2025" → execute_sql_query(sql_query='SELECT Month, Service, "Unsettled Revenue" FROM totals_summary WHERE Month IN ("September 2024", "July 2025") AND Service="Urban"', months=["September 2024", "July 2025"])
- "total revenue for July and August by service" → execute_sql_query(sql_query='SELECT Service, SUM("Unsettled Revenue") as total FROM totals_summary WHERE Month IN ("July 2025", "August 2025") GROUP BY Service', months=["July 2025", "August 2025"])

CRITICAL - Handling Ties (Multiple Results with Same Max/Min Value):
When user asks for "highest", "lowest", "best", "worst" (singular), you MUST return ALL tied results, not just one.

WRONG (only returns 1 result even if there are ties):
- "which month has the highest active routes" → SELECT Month, COUNT(*) as count FROM monthly_data GROUP BY Month ORDER BY count DESC LIMIT 1

CORRECT (returns all tied results):
- "which month has the highest active routes" → execute_sql_query(sql_query='WITH counts AS (SELECT Month, COUNT(*) as active_routes FROM monthly_data GROUP BY Month) SELECT * FROM counts WHERE active_routes = (SELECT MAX(active_routes) FROM counts)')
- "which route has the best OTP" → execute_sql_query(sql_query='WITH otp_data AS (SELECT Route, "OTP%" FROM monthly_data) SELECT * FROM otp_data WHERE "OTP%" = (SELECT MAX("OTP%") FROM otp_data)')
- "which service has the lowest cost" → execute_sql_query(sql_query='SELECT Service, "Cost / Rev Km" FROM totals_summary WHERE "Cost / Rev Km" = (SELECT MIN("Cost / Rev Km") FROM totals_summary)')
- "month with most cancellations" → execute_sql_query(sql_query='WITH cancel_counts AS (SELECT Month, SUM(Cancels) as total_cancels FROM monthly_data GROUP BY Month) SELECT * FROM cancel_counts WHERE total_cancels = (SELECT MAX(total_cancels) FROM cancel_counts)')

Use WITH (CTE) + subquery pattern to find max/min value first, then return ALL rows matching that value.

CRITICAL - Understanding Data Source Limitations:
1. GTFS data:
   - routes, stops tables: STATIC definitions (no temporal fields)
   - calendar table: Has start_date/end_date for SERVICE schedules, NOT route operational history
   - GTFS is a snapshot representing current/planned service - it is VALID FOR ALL MONTHS
   - Classification: route_type (1=Metro, 3=Bus, etc.)
   - Use GTFS for: current route definitions, stop locations, network topology, schedule structure
   - GTFS can be JOINED with ANY month's TTSS data (e.g., join stops with any month's revenue data for zone analysis)

2. TTSS tables (monthly_data, daily_data, totals_summary):
   - Has ACTUAL operational history from November 2022 to October 2025
   - Month/Date columns track real performance over time
   - Classification: Service field with values "Urban", "Intercity", "Feeder", "Seasonal" (NOT "bus" or "metro"!)
   - Use TTSS for: historical analysis, trends, route changes over time, performance metrics

CRITICAL - Service Type vs Route Type:
- GTFS uses: "metro" (route_type=1) vs "bus" (route_type=3)
- TTSS uses: "Urban", "Intercity", "Feeder", "Seasonal"
- These are DIFFERENT classification systems!

Mapping user terms to TTSS Service values:
- "bus routes" / "all bus routes" → Do NOT filter by service (includes Urban, Intercity, Feeder)
- "urban bus routes" → service="Urban"
- "feeder routes" → service="Feeder"
- "metro routes" → Query specific route IDs (Red Line, Green Line) or use route_short_name pattern
- NEVER use "bus" or "metro" as Service filter values (they don't exist in TTSS!)

For SQL queries with "bus routes":
- If using execute_sql_query: Do NOT add WHERE Service = ... (query all services)
- If filtering needed: WHERE Service IN ('Urban', 'Intercity', 'Feeder') to exclude only Seasonal

3. For queries about operational changes over time (routes added/removed, performance trends):
   - PREFER TTSS monthly_data - it shows which routes were actually operating each month
   - GTFS calendar only shows service schedule validity, not historical route changes
   - To find new/removed routes: Compare DISTINCT Route values across different months in monthly_data
   - ALWAYS add a Status/Category column to indicate the type of change (e.g., "New", "Removed", "Added", "Excluded")

4. GTFS + TTSS Combined Queries:
   - GTFS data (routes, stops, shapes) is a STATIC snapshot valid for ALL time periods
   - You can JOIN GTFS tables with ANY month's TTSS data
   - Example: "revenue by zone for December 2023" - join monthly_data with stops table (GTFS stops are valid for Dec 2023)
   - Example: "OTP by route type for all of 2024" - join monthly_data with routes table to get route_type

CRITICAL - Adding Context Columns to Results:
When queries ask about multiple categories (new vs removed, best vs worst, different services, etc.), ALWAYS add a descriptive column to label each row:
- Use UNION ALL to combine different categories with their labels
- Column names: "Status", "Category", "Type", "Change", or similar descriptive names
- Makes results immediately interpretable without needing to remember query context

Examples with context columns:
- "routes new or excluded in 2025" → execute_sql_query(sql_query='WITH routes_2024 AS (SELECT DISTINCT Route FROM monthly_data WHERE Month LIKE "%2024%"), routes_2025 AS (SELECT DISTINCT Route FROM monthly_data WHERE Month LIKE "%2025%"), new_routes AS (SELECT r2025.Route, "New in 2025" as Status FROM routes_2025 r2025 LEFT JOIN routes_2024 r2024 ON r2025.Route = r2024.Route WHERE r2024.Route IS NULL), removed_routes AS (SELECT r2024.Route, "Excluded in 2025" as Status FROM routes_2024 r2024 LEFT JOIN routes_2025 r2025 ON r2024.Route = r2025.Route WHERE r2025.Route IS NULL) SELECT * FROM new_routes UNION ALL SELECT * FROM removed_routes')
- "best and worst performing routes by OTP" → Combine top 5 routes with "Top Performer" label and bottom 5 with "Bottom Performer" label using UNION ALL
- "compare cancellations: weekday vs weekend" → Add "Day Type" column with "Weekday" or "Weekend" values
- "routes added or removed between Jan and July 2025" → Add "Change" column: "Added by July" or "Removed by July"

GTFS INFO QUERY Examples (use SQL - for data only, NOT maps):
- "what is the route name for 1004" → execute_sql_query(sql_query='SELECT route_id, route_short_name, route_long_name FROM routes WHERE route_id="1004"')
- "show me all metro routes" → execute_sql_query(sql_query='SELECT route_id, route_short_name, route_long_name, route_type FROM routes WHERE route_type=1')
- "what stops are on route E100" → execute_sql_query(sql_query='SELECT DISTINCT s.stop_id, s.stop_name FROM stops s JOIN stop_times st ON s.stop_id = st.stop_id JOIN trips t ON st.trip_id = t.trip_id JOIN routes r ON t.route_id = r.route_id WHERE r.route_short_name="E100" ORDER BY st.stop_sequence')
- "show all stops on route 28" → execute_sql_query(sql_query='SELECT DISTINCT s.stop_id, s.stop_name FROM stops s JOIN stop_times st ON s.stop_id = st.stop_id JOIN trips t ON st.trip_id = t.trip_id JOIN routes r ON t.route_id = r.route_id WHERE r.route_short_name="28"')
- "stops in zone 5" → execute_sql_query(sql_query='SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops WHERE zone_id=5')

GTFS FREQUENCY/SCHEDULE Examples (use SQL for service frequency, headway, waiting time):
- "average waiting time for route X25" → execute_sql_query(sql_query='SELECT r.route_short_name, COUNT(DISTINCT t.trip_id) as total_trips, ROUND(24.0 * 60 / COUNT(DISTINCT t.trip_id), 1) as avg_headway_minutes FROM routes r JOIN trips t ON r.route_id = t.route_id WHERE r.route_short_name="X25" GROUP BY r.route_short_name')
- "service frequency for route 28" → execute_sql_query(sql_query='SELECT r.route_short_name, COUNT(DISTINCT t.trip_id) as daily_trips, ROUND(24.0 * 60 / COUNT(DISTINCT t.trip_id), 1) as avg_minutes_between_buses FROM routes r JOIN trips t ON r.route_id = t.route_id WHERE r.route_short_name="28" GROUP BY r.route_short_name')
- "how often does route E100 run" → execute_sql_query(sql_query='SELECT r.route_short_name, r.route_long_name, COUNT(DISTINCT t.trip_id) as trips_per_day FROM routes r JOIN trips t ON r.route_id = t.route_id WHERE r.route_short_name="E100" GROUP BY r.route_short_name, r.route_long_name')
- "headway for all metro routes" → execute_sql_query(sql_query='SELECT r.route_short_name, COUNT(DISTINCT t.trip_id) as trips, ROUND(24.0 * 60 / COUNT(DISTINCT t.trip_id), 1) as headway_minutes FROM routes r JOIN trips t ON r.route_id = t.route_id WHERE r.route_type=1 GROUP BY r.route_short_name ORDER BY headway_minutes')
- "which routes have the shortest waiting time" → execute_sql_query(sql_query='SELECT r.route_short_name, COUNT(DISTINCT t.trip_id) as trips, ROUND(24.0 * 60 / COUNT(DISTINCT t.trip_id), 1) as avg_wait_minutes FROM routes r JOIN trips t ON r.route_id = t.route_id GROUP BY r.route_short_name ORDER BY avg_wait_minutes LIMIT 10')

CRITICAL: When users refer to routes by display names (E100, 28, etc.), you MUST join with routes table and match on route_short_name, NOT route_id! route_id is an internal ID (e.g., "3051"), while route_short_name is the user-facing name (e.g., "E100").

CHART/GRAPH/VISUALIZATION Examples (ALWAYS use plot_ functions - NEVER get_ functions):
- "show me a bar chart of revenue" → plot_monthly_kpi_trends(metric="Unsettled Revenue")
- "graph OTP performance" → plot_monthly_kpi_trends(metric="OTP%")
- "visualize ridership trends" → plot_monthly_kpi_trends(metric="Checkins")
- "draw a chart of load factor" → plot_monthly_kpi_trends(metric="Load Factor")
- "plot revenue by service" → plot_monthly_kpi_trends(metric="Unsettled Revenue")
- "chart showing OTP trends" → plot_monthly_kpi_trends(metric="OTP%")
- "create a line graph of CRR" → plot_monthly_kpi_trends(metric="CRR")
IMPORTANT: When user says "chart", "graph", "plot", "visualize" (not for routes), "draw a chart" → MUST use plot_ functions!

MAP QUERY Examples (use map functions - NEVER use SQL for maps):
- "show route E100 on map" → generate_route_map(route_ids=["E100"])
- "draw route 28" → generate_route_map(route_ids=["28"])
- "map routes E100 and 28" → generate_route_map(route_ids=["E100", "28"])
- "visualize route E315" → generate_route_map(route_ids=["E315"])
- "plot stops for route F23" → generate_stops_map(route_ids=["F23"])
- "show stops on route E100" → generate_stops_map(route_ids=["E100"])
- "map stops for route 28" → generate_stops_map(route_ids=["28"])
- "display stops in zone 5" → generate_stops_map(zone_ids=[5])
- "display all routes on map" → generate_route_map(max_routes=10)
- "show route coverage" → analyze_route_coverage()
- "map all metro lines" → generate_route_map(max_routes=10)
- "show me the path of route E100" → generate_route_map(route_ids=["E100"])
- "display route geography for 93" → generate_route_map(route_ids=["93"])
- "where does E100 go" → generate_route_map(route_ids=["E100"])
- "show me the route for E100" → generate_route_map(route_ids=["E100"])
- "I want to see route 28" → generate_route_map(route_ids=["28"])

CRITICAL - SQL Query Best Practices:
1. NO duplicate column names in SELECT (use explicit columns, not SELECT *)
2. Month column is TEXT format ("January 2024"), NOT date type
   - Use LIKE "%2024%" for year filtering, NOT strftime() or date functions
   - Use exact match for specific months: Month = "January 2024"
3. For "consistently" or "throughout period" queries: COUNT(DISTINCT Month) per item, then filter by expected total

CRITICAL FUNCTION SELECTION RULES:
1. For PLOTTING/VISUALIZATION/CHART queries - ALWAYS use plot_ functions:
   - Keywords: "plot", "chart", "graph", "visualize", "show trends", "bar chart", "line chart", "draw a graph"
   - MONTHLY trends → use plot_monthly_kpi_trends
   - DAILY data (day-by-day) → use plot_daily_kpi_trends
   - Month comparisons → use plot_month_comparison
   - Quarter comparisons → use plot_quarterly_comparison
   - If user says "daily", "day by day" → MUST use plot_daily_kpi_trends
   - NEVER return dataframe when user explicitly asks for chart/graph/plot!
2. For MAP/ROUTE GEOGRAPHY queries:
   - Keywords: "map", "show route on map", "draw route", "route path", "where does route go"
   - Routes on map → use generate_route_map
   - Stops on map → use generate_stops_map or analyze_route_coverage
3. For DATA/TABLE QUERIES (no visualization):
   - Keywords: "list", "show data", "what is", "get", "find", percentage calculations
   - Use execute_sql_query or specific get_ functions
4. NEVER use get_revenue_analysis, get_ridership_trends, etc. when user asks for "chart" or "graph" - use plot_ functions instead!

IMPORTANT DISTINCTIONS:
- "show route E100" or "where does E100 go" = MAP (use generate_route_map)
- "what is the name of route E100" = INFO (use SQL)
- "what stops are on E100" = INFO (use SQL for stop list)
- "draw route E100" or "route E100 path" = MAP (use generate_route_map)

IMPORTANT: When user asks for specific data (like "planned vs actual trips"), use SQL SELECT to return ONLY the requested columns, not all columns.

Always specify the months parameter to load only necessary data.

You can call multiple functions in sequence to build a complete analysis plan when genuinely needed (e.g., getting data AND plotting it, or combining GTFS and TTSS data).

IMPORTANT: Do NOT call get_route_statistics unless the user explicitly asks to "list routes", "show all routes", or "route statistics table". It returns a generic GTFS routes table that is NOT useful as context for KPI analysis, maps, or performance queries."""

    # Following are individual prompts for various analysis tasks
    # --------not used now, but kept for future reference --------

    @staticmethod
    def get_data_analysis_prompt() -> str:
        """
        Get prompt for general data analysis tasks.

        Returns:
            Prompt for data analysis guidance
        """
        return """
Analyze the provided transit data and provide insights about:
- Usage patterns and trends
- Service efficiency metrics
- Coverage gaps or opportunities
- Operational recommendations

Focus on actionable insights that can help improve RTA services.
"""

    @staticmethod
    def get_route_optimization_prompt() -> str:
        """
        Get prompt for route optimization analysis.

        Returns:
            Prompt for route optimization tasks
        """
        return """
Analyze the route data to identify optimization opportunities:
- Overlapping routes or service gaps
- Underutilized or overcrowded routes
- Potential route extensions or modifications
- Transfer point efficiency

Provide specific recommendations with supporting data.
"""

    @staticmethod
    def get_accessibility_analysis_prompt() -> str:
        """
        Get prompt for accessibility analysis.

        Returns:
            Prompt for accessibility analysis
        """
        return """
Evaluate transit accessibility across Dubai:
- Coverage in different zones and neighborhoods
- Distance to nearest stops/stations
- Service frequency by area
- Integration between different transport modes

Identify areas with limited transit access and suggest improvements.
"""

    @staticmethod
    def get_performance_metrics_prompt() -> str:
        """
        Get prompt for performance metrics analysis.

        Returns:
            Prompt for performance analysis
        """
        return """
Analyze transit system performance metrics:
- Service reliability and punctuality
- Route efficiency (distance vs stops)
- Transfer connectivity and timing
- Peak vs off-peak usage patterns

Provide benchmarks and improvement recommendations.
"""

    @staticmethod
    def get_custom_analysis_prompt(analysis_type: str) -> str:
        """
        Get a customized prompt for specific analysis types.

        Args:
            analysis_type: Type of analysis requested

        Returns:
            Customized prompt string
        """
        base_prompt = f"""
Perform a detailed {analysis_type} analysis of the RTA transit data.
Consider the following aspects:
- Current state and trends
- Comparative analysis where applicable
- Key insights and patterns
- Actionable recommendations

Structure your response with clear sections and supporting data.
"""
        return base_prompt

    @staticmethod
    def get_error_handling_prompt(error_context: str) -> str:
        """
        Get prompt for handling analysis errors.

        Args:
            error_context: Context about the error that occurred

        Returns:
            Prompt for error handling and alternative approaches
        """
        return f"""
An error occurred during analysis: {error_context}

Please provide:
1. Alternative approaches to get similar insights
2. Possible causes of the data issue
3. Recommendations for data quality improvement
4. Simplified analysis that can work with available data

Focus on providing value despite the technical limitations.
"""

    @staticmethod
    def get_advanced_analytics_prompt() -> str:
        """
        Get prompt for advanced analytics queries including KPIs and trends.

        Returns:
            Prompt for advanced analytics tasks
        """
        return """
Analyze advanced transit performance metrics and trends:

Key Performance Indicators:
- CRR (Cost Recovery Ratio): Revenue vs operational costs
- OTP (On-Time Performance): Schedule adherence percentage
- Load Factor: Passenger capacity utilization
- Ridership Trends: Passenger volume over time

Time-based Analysis:
- Multi-year trend analysis (2+ years)
- Holiday impact assessment
- Seasonal pattern identification
- Day-of-week performance variations

Route-specific Queries:
- Individual route performance (e.g., Route E100, Route 54)
- Distance coverage calculations
- Trip frequency analysis
- Timetable extraction

Note: Current analysis provides simulated estimates based on GTFS data and industry patterns.
For actual operational metrics, TTSS integration would be required.

Provide insights with:
1. Simulated realistic values
2. Clear methodology explanation
3. Data limitations disclosure
4. Actionable recommendations
"""

    @staticmethod
    def get_kpi_analysis_prompt() -> str:
        """
        Get prompt for KPI-specific analysis.

        Returns:
            Prompt for KPI analysis
        """
        return """
Analyze Key Performance Indicators for transit operations:

CRR (Cost Recovery Ratio):
- Target: 0.8-1.2 (80-120% cost recovery)
- Metro typically performs better than bus
- Consider ridership, fare structure, operational efficiency

OTP (On-Time Performance):
- Target: >90% for metro, >85% for bus
- Factors: traffic, weather, technical issues
- Peak vs off-peak variations

Load Factor:
- Target: 60-80% optimal utilization
- Route type and time-dependent
- Seasonal and daily patterns

Provide analysis with:
- Current performance vs targets
- Trend identification
- Root cause analysis
- Improvement recommendations
"""

    @staticmethod
    def get_time_series_prompt() -> str:
        """
        Get prompt for time series and trend analysis.

        Returns:
            Prompt for time series analysis
        """
        return """
Perform time series analysis for transit data:

Trend Analysis:
- 2-year historical patterns
- Growth/decline identification
- Seasonality detection
- Holiday impact assessment

Pattern Recognition:
- Weekly cycles (weekday vs weekend)
- Monthly variations
- Annual trends
- Special event impacts

Forecasting Elements:
- Project future trends
- Identify potential issues
- Recommend capacity adjustments
- Plan service improvements

Present findings with:
- Visual trend indicators
- Statistical significance
- Confidence intervals
- Actionable insights
"""

    @staticmethod
    def get_operational_query_prompt() -> str:
        """
        Get prompt for operational-specific queries.

        Returns:
            Prompt for operational queries
        """
        return """
Answer operational queries about transit services:

Route Operations:
- Specific route analysis (by route ID/name)
- Daily/weekly trip planning
- Distance calculations
- Service frequency optimization

Schedule Analysis:
- Timetable extraction and analysis
- Day-of-week variations
- Peak hour identification
- Service span evaluation

Performance Metrics:
- Trip completion rates
- Distance coverage
- Resource utilization
- Efficiency indicators

Provide responses with:
- Specific operational data
- Clear calculations
- Practical recommendations
- Implementation considerations
"""

    @staticmethod
    def get_ttss_kpi_prompt() -> str:
        """
        Get prompt for TTSS KPI analysis queries.

        Returns:
            Prompt for TTSS KPI analysis
        """
        return """
Analyze TTSS (Transit Tracking & Scheduling System) Key Performance Indicators:

Available KPIs (November 2022 to October 2025):

1. On-Time Performance (OTP%):
   - Target: >85% for Urban, >90% for Intercity
   - Factors: traffic, weather, operational issues
   - First stop first trip OTP% also available

2. Load Factor (Capacity Utilization):
   - Target: 60-80% optimal utilization
   - Passenger-km vs Seat-km ratio
   - Route and time-dependent patterns

3. Cost Recovery Ratio (CRR):
   - Target: 0.8-1.2 (80-120% cost recovery)
   - Revenue per km vs Cost per km
   - Subsidy requirements when CRR < 100%

4. Ridership Metrics:
   - Checkins/Checkouts per route
   - Trends over the available period (Nov 2022 - Oct 2025)
   - Service type comparisons

5. Operational Efficiency:
   - Cancellation rates
   - Curtailment rates
   - Plan vs Operated trips variance
   - Dead km percentage

6. Financial Metrics:
   - Revenue per km
   - Cost per km
   - Average fare
   - Subsidy per km

Service Types: Urban, Intercity, Feeder, Seasonal
Data Granularity: Monthly, Daily, Service-level aggregates

Analysis Approach:
- Compare current vs target metrics
- Identify trends and patterns
- Highlight best/worst performers
- Provide actionable recommendations
"""

    @staticmethod
    def get_ttss_comparison_prompt() -> str:
        """
        Get prompt for TTSS comparison analysis.

        Returns:
            Prompt for comparison queries
        """
        return """
Perform comparative analysis using TTSS data:

Comparison Types:

1. Temporal Comparisons:
   - Month-over-month trends
   - Seasonal patterns
   - Weekend vs Weekday performance
   - Holiday impact analysis

2. Service Comparisons:
   - Urban vs Intercity vs Feeder
   - Metro vs Bus performance
   - Route-to-route comparisons

3. KPI Benchmarking:
   - Top N routes by any KPI
   - Routes above/below target thresholds
   - Best/worst performers

4. Geographic Comparisons:
   - Zone-level performance
   - Area coverage analysis

Analysis Guidelines:
- Use all available historical data for trends (Nov 2022 - Oct 2025)
- Calculate percentage changes
- Identify significant variations
- Contextualize with industry benchmarks
- Recommend optimization opportunities
"""

    @staticmethod
    def get_ttss_troubleshooting_prompt() -> str:
        """
        Get prompt for TTSS troubleshooting queries.

        Returns:
            Prompt for identifying issues
        """
        return """
Identify and analyze operational issues using TTSS data:

Problem Areas to Investigate:

1. Low OTP% Routes:
   - Routes with OTP% < 85%
   - High late stop counts
   - Peak hour punctuality issues

2. Underutilized Routes:
   - Load Factor < 40%
   - Low ridership trends
   - Excess capacity

3. High Cost Routes:
   - CRR < 60% (high subsidy need)
   - High cost per km
   - Poor revenue efficiency

4. Service Reliability Issues:
   - High cancellation rates (>5%)
   - Frequent curtailments
   - Plan vs operated variance

5. Financial Concerns:
   - Negative CRR routes
   - Declining revenue trends
   - Rising subsidy requirements

Diagnostic Approach:
- Identify root causes
- Quantify impact
- Compare with similar routes
- Suggest corrective actions
- Prioritize by severity
"""

    @staticmethod
    def get_chat_context_prompt() -> str:
        """
        Get context prompt for chat interactions.

        Returns:
            Prompt for maintaining chat context
        """
        return """
You are analyzing Dubai RTA transit data through a conversational interface.

Data Access:
- GTFS: Static route/stop information, schedules (valid for all time periods)
- TTSS: Operational KPIs from November 2022 to October 2025

Response Style:
- Be concise and data-driven
- Provide specific numbers and metrics
- Use comparisons for context
- Highlight actionable insights
- Format results clearly

When showing results:
- Tables for multiple routes/periods
- Key metrics prominently displayed
- Trends and patterns noted
- Recommendations when relevant

If data is unavailable:
- Clearly state limitations
- Suggest alternative queries
- Explain what data would be needed
"""

    @staticmethod
    def get_ttss_monthly_analysis_prompt() -> str:
        """
        Get prompt for TTSS monthly trend analysis.

        Returns:
            Prompt for monthly analysis
        """
        return """
Analyze monthly trends using TTSS data (November 2022 to October 2025):

Monthly Analysis Focus Areas:

1. Performance Trends:
   - OTP% month-over-month changes
   - Load Factor seasonal patterns
   - CRR stability and fluctuations
   - Service quality consistency

2. Ridership Patterns:
   - Monthly checkins/checkouts trends
   - Growth or decline rates
   - Seasonal variations (peak/off-peak months)
   - Holiday impact (Ramadan, Eid, etc.)

3. Operational Patterns:
   - Cancellation rate trends
   - Plan vs operated trips consistency
   - Dead km percentage variations
   - Addition trips patterns

4. Financial Trends:
   - Revenue per km trends
   - Cost efficiency changes
   - Subsidy requirement evolution
   - Average fare variations

Key Metrics to Track:
- Month with best/worst performance
- Biggest month-over-month changes
- Consistent performers vs volatile routes
- Improving vs declining trends

Reporting Format:
- Show 12-month data clearly
- Highlight significant changes (>10%)
- Identify seasonal patterns
- Forecast potential issues
"""

    @staticmethod
    def get_ttss_route_deep_dive_prompt() -> str:
        """
        Get prompt for detailed route analysis.

        Returns:
            Prompt for route-specific deep dive
        """
        return """
Perform comprehensive route analysis using TTSS data:

Route Deep Dive Components:

1. Performance Profile:
   - All 33 KPI metrics for the route
   - 12-month historical trends
   - Performance vs targets
   - Peer route comparisons

2. Ridership Analysis:
   - Total checkins/checkouts over period
   - Average daily/weekly ridership
   - Peak vs off-peak patterns
   - Capacity utilization (Load Factor)

3. Service Quality:
   - OTP% performance and trends
   - Late stops analysis
   - First stop first trip reliability
   - Service consistency

4. Financial Performance:
   - Revenue generation
   - Cost structure
   - CRR and subsidy requirements
   - Revenue per km efficiency

5. Operational Efficiency:
   - Plan vs operated trips
   - Cancellation and curtailment rates
   - Dead km percentage
   - Resource utilization

6. Comparative Position:
   - Rank within service type (Urban/Intercity/Feeder)
   - Performance vs similar routes
   - Best/worst months identified

Output Format:
- Executive summary (3-5 key points)
- Detailed metrics table
- Trend charts (if visual)
- Actionable recommendations
"""

    @staticmethod
    def get_ttss_service_comparison_prompt() -> str:
        """
        Get prompt for service type comparisons.

        Returns:
            Prompt for Urban/Intercity/Feeder comparison
        """
        return """
Compare service types (Urban, Intercity, Feeder, Seasonal) using TTSS data:

Comparison Framework:

1. Scale and Coverage:
   - Number of routes per service type
   - Total operated trips
   - Total driven km (revenue + dead)
   - Geographic coverage

2. Performance Metrics:
   - Average OTP% by service type
   - Load Factor comparisons
   - Service reliability (cancellation rates)
   - First stop punctuality

3. Ridership Characteristics:
   - Total passengers (checkins)
   - Average trip length (passenger-km)
   - Checkins per revenue km
   - Ridership trends

4. Financial Comparison:
   - Revenue generation by service
   - Cost per km comparison
   - CRR performance
   - Subsidy requirements
   - Average fare differences

5. Operational Efficiency:
   - Dead km percentage
   - Plan vs operated accuracy
   - Resource utilization
   - Addition trips rate

Expected Differences:
- Intercity: Higher load factor, longer trips, better CRR
- Urban: Higher frequency, shorter trips, more stops
- Feeder: Lower volume, specialized coverage

Analysis Approach:
- Use aggregated monthly data
- Calculate weighted averages
- Show percentage distributions
- Highlight relative strengths/weaknesses
"""

    @staticmethod
    def get_ttss_weekend_weekday_prompt() -> str:
        """
        Get prompt for weekend vs weekday analysis.

        Returns:
            Prompt for day-type comparison
        """
        return """
Compare weekend vs weekday performance using TTSS daily summary data:

Weekend vs Weekday Analysis:

1. Service Patterns:
   - Trip frequency differences
   - Route coverage variations
   - Service hour adjustments
   - Operated trips count

2. Ridership Behavior:
   - Total checkins comparison
   - Average ridership per trip
   - Peak hour shifts
   - Passenger-km patterns

3. Performance Differences:
   - OTP% weekday vs weekend
   - Load Factor variations
   - Service reliability
   - Cancellation rate differences

4. Operational Metrics:
   - Resource deployment
   - Dead km percentage
   - Cost efficiency
   - Revenue generation

5. Service Quality:
   - On-time stops percentage
   - Late stops comparison
   - Early departures
   - Service consistency

Expected Patterns:
- Weekend: Lower ridership, better OTP%, reduced frequency
- Weekday: Higher ridership, peak congestion, more trips
- Friday: Unique pattern (prayer times, early dismissals)
- Saturday-Sunday: Leisure travel patterns

Insights to Provide:
- Optimal resource allocation
- Service adjustment opportunities
- Day-specific issues
- Revenue optimization potential
"""

    @staticmethod
    def get_ttss_top_bottom_analysis_prompt() -> str:
        """
        Get prompt for top/bottom performers analysis.

        Returns:
            Prompt for ranking and benchmarking
        """
        return """
Identify and analyze top and bottom performers using TTSS data:

Performance Ranking Analysis:

1. Top Performers (Benchmarks):
   - Top 10 routes by OTP%
   - Top 10 by Load Factor
   - Top 10 by CRR (financial efficiency)
   - Top 10 by ridership
   - Top 10 by revenue

2. Bottom Performers (Focus Areas):
   - Bottom 10 routes by OTP%
   - Bottom 10 by Load Factor
   - Routes with negative/low CRR
   - Lowest ridership routes
   - Highest cancellation rates

3. Improvement Opportunities:
   - Routes just below target thresholds
   - High potential, low performance routes
   - Underutilized high-capacity routes
   - Cost-inefficient routes

4. Success Factors Analysis:
   - Common traits of top performers
   - Service type patterns
   - Geographic factors
   - Operational practices

5. Problem Diagnosis:
   - Root causes of poor performance
   - Systemic vs route-specific issues
   - Infrastructure constraints
   - Demand-supply mismatches

Ranking Criteria:
- Use consistent metrics across service types
- Consider route characteristics (length, type, coverage)
- Weight by significance (high ridership routes matter more)
- Account for seasonal variations

Output Format:
- Top 10 / Bottom 10 tables
- Performance gap analysis
- Best practice recommendations
- Prioritized improvement actions
"""

    @staticmethod
    def get_ttss_anomaly_detection_prompt() -> str:
        """
        Get prompt for anomaly and outlier detection.

        Returns:
            Prompt for identifying unusual patterns
        """
        return """
Detect anomalies and unusual patterns in TTSS data:

Anomaly Detection Areas:

1. Performance Anomalies:
   - Sudden OTP% drops (>20% change)
   - Unusual Load Factor spikes/drops
   - CRR significant variations
   - Service quality deterioration

2. Ridership Anomalies:
   - Unexpected ridership changes
   - Single-month outliers
   - Trend reversals
   - Unusual daily patterns

3. Operational Anomalies:
   - Abnormal cancellation spikes
   - Unusual dead km percentages
   - Plan vs operated large variances
   - Addition trips anomalies

4. Financial Anomalies:
   - Revenue per km outliers
   - Cost spike identification
   - Subsidy requirement jumps
   - Fare collection anomalies

5. Temporal Anomalies:
   - Holiday impact exceeding norms
   - Weather-related disruptions
   - Special event effects
   - Infrastructure issues

Detection Methods:
- Month-over-month variance >20%
- Values >2 standard deviations from mean
- Sudden trend breaks
- Isolated single-month events

Response Framework:
- Identify the anomaly clearly
- Quantify the deviation
- Suggest potential causes
- Recommend investigation or action
- Check for data quality issues
"""

    @staticmethod
    def get_ttss_forecasting_prompt() -> str:
        """
        Get prompt for trend forecasting and predictions.

        Returns:
            Prompt for forward-looking analysis
        """
        return """
Forecast future trends based on TTSS historical data:

Forecasting Framework:

1. Trend Projection:
   - 12-month trend analysis
   - Growth/decline rate calculation
   - Seasonal pattern identification
   - Extrapolation to next 3-6 months

2. Performance Forecasting:
   - Expected OTP% trends
   - Projected Load Factor
   - Anticipated CRR changes
   - Service quality trajectory

3. Ridership Forecasting:
   - Expected passenger growth/decline
   - Seasonal adjustment factors
   - New route impact estimation
   - Capacity planning needs

4. Financial Projections:
   - Revenue trend forecasts
   - Cost escalation expectations
   - Subsidy requirement projections
   - Budget planning inputs

5. Risk Identification:
   - Routes at risk of poor performance
   - Potential service quality issues
   - Financial sustainability concerns
   - Capacity constraints

Forecasting Approach:
- Use all available historical data as baseline (Nov 2022 - Oct 2025)
- Apply seasonal factors
- Consider known upcoming changes
- Provide confidence ranges
- Identify assumptions

Output Format:
- Current state summary
- Projected trends (3-6 months)
- Key assumptions stated
- Risk factors highlighted
- Recommended preemptive actions
"""

    @staticmethod
    def get_ttss_kpi_target_prompt() -> str:
        """
        Get prompt for KPI target setting and monitoring.

        Returns:
            Prompt for target-based analysis
        """
        return """
Analyze performance against KPI targets using TTSS data:

KPI Target Framework:

1. On-Time Performance Targets:
   - Urban: ≥85% OTP%
   - Intercity: ≥90% OTP%
   - Feeder: ≥85% OTP%
   - First Stop First Trip: ≥95%

2. Load Factor Targets:
   - Optimal range: 60-80%
   - Acceptable: 40-85%
   - Below target: <40% (underutilized)
   - Above target: >85% (overcrowded)

3. Cost Recovery Targets:
   - Excellent: CRR >100%
   - Good: CRR 80-100%
   - Acceptable: CRR 60-80%
   - Poor: CRR <60%

4. Service Reliability Targets:
   - Cancellation rate: <2%
   - Plan vs operated: >98%
   - Dead km: <15%

5. Financial Targets:
   - Revenue per km: Service-specific
   - Cost per km: Industry benchmarks
   - Subsidy per km: Minimize

Performance Categories:
- Exceeding targets (Green)
- Meeting targets (Yellow)
- Below targets (Orange)
- Significantly below (Red)

Analysis Focus:
- Routes not meeting targets
- Gap size quantification
- Trend toward/away from targets
- Action plans for below-target routes
- Celebrate over-performers

Reporting:
- Target vs actual comparison
- Color-coded status
- Gap analysis
- Improvement roadmap
- Timeline for target achievement
"""

    @staticmethod
    def get_ttss_executive_summary_prompt() -> str:
        """
        Get prompt for executive-level summaries.

        Returns:
            Prompt for high-level reporting
        """
        return """
Create executive summary of TTSS performance data:

Executive Summary Components:

1. Overall Performance Snapshot:
   - Network-wide OTP%: Current and trend
   - Average Load Factor: System utilization
   - Overall CRR: Financial health
   - Total ridership: Volume and trend

2. Key Highlights (3-5 points):
   - Major achievements
   - Notable improvements
   - Areas of concern
   - Month-over-month changes
   - Year-to-date performance

3. Service Type Performance:
   - Urban: Brief status
   - Intercity: Brief status
   - Feeder: Brief status
   - Comparative position

4. Top Issues (Critical 3):
   - Most urgent problems
   - Impact quantification
   - Recommended immediate actions

5. Financial Overview:
   - Total revenue
   - Total costs
   - Overall CRR
   - Subsidy requirements
   - Budget variance

6. Forward Look:
   - Expected trends
   - Upcoming challenges
   - Opportunities identified
   - Strategic recommendations

Format Requirements:
- Maximum 1 page or 500 words
- Bullet points preferred
- Numbers with context
- Action-oriented
- No technical jargon
- Highlight changes (↑↓)

Tone:
- Professional and concise
- Data-driven
- Solution-focused
- Executive-friendly
"""
