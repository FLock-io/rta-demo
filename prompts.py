"""
Prompt templates for RTA Transit Analytics application.
This module contains all AI prompt templates used throughout the application.
"""


class RTAPrompts:
    """Collection of prompt templates for RTA transit analysis."""

    @staticmethod
    def get_system_planning_prompt(available_functions: list) -> str:
        """
        Get the system prompt for LLM planning.

        Args:
            available_functions: List of available analysis functions

        Returns:
            System prompt string for planning queries
        """
        return f"""
You are an AI planner for RTA (Road and Transport Authority) transit data analysis.

Available functions:
{', '.join(available_functions)}

The user will ask questions about Dubai's transit system including:
- Metro routes (Red and Green lines)
- Bus routes and stops
- Station locations and accessibility
- Route coverage and connectivity
- Service frequency and performance

Generate a step-by-step execution plan to answer their question using available functions.
Return a JSON object with this structure:
{{
    "query": "original user query",
    "interpretation": "your understanding of what they want",
    "steps": [
        {{
            "description": "human readable step description",
            "function": "function_name_to_call",
            "parameters": {{"param1": "value1"}},
            "output_type": "dataframe|chart|metric|text"
        }}
    ]
}}
"""

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
