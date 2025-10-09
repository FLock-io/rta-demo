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
2. TTSS Data (Confidential, 12 months Sep 2024-Aug 2025): Performance KPIs, ridership, revenue, costs

Function Categories:
- GTFS Functions (10): Basic route/stop info, maps, frequency analysis
- TTSS KPI Functions (13): OTP%, Load Factor, CRR, ridership trends, revenue, costs, cancellations

Key Guidelines:
- For performance metrics (OTP%, Load Factor, CRR), use TTSS functions
- For route/stop locations and maps, use GTFS functions


Service Types: Urban, Intercity, Feeder, Seasonal
Months Available: September 2024 through August 2025

You can call multiple functions in sequence to build a complete analysis plan."""

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

Available KPIs (12 months data: Sep 2024 - Aug 2025):

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
   - Trends over 12 months
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
- Use 12 months data for trends (Sep 2024 - Aug 2025)
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
- GTFS: Static route/stop information, schedules
- TTSS: 12 months operational KPIs (Sep 2024 - Aug 2025)

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
Analyze monthly trends using TTSS data (12 months: Sep 2024 - Aug 2025):

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
- Use 12-month historical baseline
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
