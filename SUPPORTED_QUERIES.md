# RTA Demo - Supported Queries

## Overview

The RTA Demo now supports query variations across **23 analysis functions**:
- **10 GTFS-based functions** (routes, stops, coverage, frequency)
- **10 TTSS-based functions** (KPIs, performance, trends)

## Data Sources

### GTFS Data (Open)
- Routes: 201
- Stops: 2,819
- Trips: 66,562
- Stop Times: 1,436,290

### TTSS Data (Confidential - 12 Months)
- Monthly Data: 2,209 route-month records
- Daily Data: 64,735 route-day records
- Date Range: Sep 2024 - Aug 2025
- Services: Urban, Intercity, Feeder, Seasonal

---

## GTFS-Based Queries (10 Functions)

### 1. Route Statistics (`get_route_statistics`)

**Supported Queries:**
```
"Show all metro routes"
"List bus routes"
"What tram routes exist?"
"Display route names and IDs"
"Show routes by type"
"How many routes does RTA operate?"
```

**Parameters:**
- `route_type`: 'metro', 'bus', 'tram' (optional)

**Sample Output:**
| route_id | route_short_name | route_long_name | route_type_desc |
|----------|------------------|-----------------|-----------------|
| 11-MRe-1-y08-1 | MRed1 | Red Line 1 | Metro |

---

### 2. Stop Information (`get_stop_information`)

**Supported Queries:**
```
"Find stations with 'Mall' in name"
"Search for stops near 'Airport'"
"Show Metro Station stops"
"Get coordinates for BurJuman"
"List stops in zone 0005"
```

**Parameters:**
- `stop_name`: Search term (optional)
- `limit`: Max results (default: 50)

**Sample Output:**
| stop_id | stop_name | stop_lat | stop_lon |
|---------|-----------|----------|----------|
| 13601 | BurJuman Metro Station 1 | 25.2550 | 55.3044 |

---

### 3. Route Coverage Map (`analyze_route_coverage`)

**Supported Queries:**
```
"Show coverage map"
"Display all stops on a map"
"Where are all the stations?"
"Visualize stop distribution"
"Map transit network"
```

**Output:** Interactive Plotly map with all stops

---

### 4. Busiest Stops (`get_busiest_stops`)

**Supported Queries:**
```
"What are the busiest stops?"
"Show top 20 most used stations"
"Which stops have most trips?"
"Rank stations by traffic"
```

**Parameters:**
- `limit`: Number of top stops (default: 20)

---

### 5. Route Distances (`calculate_route_distances`)

**Supported Queries:**
```
"Calculate route distances"
"How long are the routes?"
"Show route lengths in km"
```

---

### 6. Stop Accessibility (`get_stop_accessibility`)

**Supported Queries:**
```
"Show stop count by zone"
"How many stops per zone?"
"Zone-wise distribution"
```

---

### 7. Service Frequency (`analyze_service_frequency`)

**Supported Queries:**
```
"Which routes have most trips?"
"Analyze service frequency"
"Show metro trip counts"
"Compare bus frequencies"
```

**Parameters:**
- `route_type`: 'metro' or 'bus' (optional)

---

### 8. Route Map (`generate_route_map`)

It supports to click the route name (right upper corner) to display the route shape on the map.

**Supported Queries:**
```
"Generate route map"
"Show route shapes"
"Visualize route network"
"Display route paths"
```

**Parameters:**
- `max_routes`: Number of routes to display (default: 10)

---

### 9. Transfer Points (`get_transfer_points`)

**Supported Queries:**
```
"Show all transfer points"
"Where can I transfer?"
"List interchange stations"
"Display transfer times"
```

---

### 10. Network Connectivity (`analyze_network_connectivity`)

**Supported Queries:**
```
"Network statistics"
"How many routes and stops total?"
```

---

## TTSS-Based Queries (13 Functions)

### 1. OTP Analysis (`get_otp_analysis`)

**On-Time Performance Analysis**

**Supported Queries:**
```
"Show OTP% for all routes"
"What's the OTP% for route E100?"
"Display urban service OTP%"
"Routes with OTP% > 90%"
"Best performing routes by OTP%"
"OTP% in July 2025"
```

**Parameters:**
- `route_id`: Specific route (optional)
- `service`: Urban/Intercity/Feeder (optional)
- `month`: e.g., 'July 2025' (optional)
- `limit`: Max results (default: 20)


---

### 2. Load Factor Analysis (`get_load_factor_analysis`)

**Capacity Utilization Analysis**

**Supported Queries:**
```
"Show Load Factor for all routes"
"What's the Load Factor for metro?"
"Routes with highest Load Factor"
"Intercity capacity utilization"
"Load Factor by service type"
```

**Parameters:**
- `route_id`: Specific route (optional)
- `service`: Service type (optional)
- `month`: Month filter (optional)
- `limit`: Max results (default: 20)


---

### 3. CRR Analysis (`get_crr_analysis`)

**Cost Recovery Ratio (Revenue vs Cost Efficiency)**

**Supported Queries:**
```
"Show CRR for all routes"
"What's the CRR for Urban service?"
"Routes with positive CRR"
"Cost recovery analysis"
"Subsidy requirements by route"
```

**Parameters:**
- `route_id`: Specific route (optional)
- `service`: Service type (optional)
- `month`: Month filter (optional)
- `limit`: Max results (default: 20)

---

### 4. Ridership Trends (`get_ridership_trends`)

**Passenger Volume Trends Over Time**

**Supported Queries:**
```
"Show ridership trends for route 10"
"Passenger trends by urban service in April 2025"
```

**Parameters:**
- `route_id`: Specific route (optional)
- `service`: Service type (optional)
- `month`: Month filter (optional)
- `limit`: Max results (default: 3)


**Use Case:** Track 12-month ridership trends for route 10 (753,284 total checkins)

---


### 5. Revenue Analysis (`get_revenue_analysis`)

**Revenue Performance by Route**

**Supported Queries:**
```
"Show revenue by route"
"Top revenue generating routes"
"Revenue per km analysis"
"Average fare by service"
"Revenue trends"
```

**Parameters:**
- `route_id`: Specific route (optional)
- `service`: Service type (optional)
- `month`: Month filter (optional)
- `limit`: Max results (default: 20)

---

### 6. Cost Efficiency (`get_cost_efficiency`)

**Operational Cost Efficiency**

**Supported Queries:**
```
"Show cost efficiency by route"
"Routes with lowest cost per km"
"Dead km analysis"
"Cost optimization opportunities"
```

**Parameters:**
- `route_id`: Specific route (optional)
- `service`: Service type (optional)
- `month`: Month filter (optional)
- `limit`: Max results (default: 20)


---



### 7. Service Summary (`get_service_summary`)

**Aggregate Statistics by Service Type**

**Supported Queries:**
```
"Show Urban service summary"
"Feeder service statistics"
"Service-level KPIs"
```

**Parameters:**
- `service`: Urban/Intercity/Feeder/Seasonal (required)
- `month`: Month filter (optional)

---

### 8. Top Routes by KPI (`get_top_routes_by_kpi`)

**Rank Routes by Any KPI**

**Supported Queries:**
```
"Top 10 routes by OTP%"
"Best routes by Load Factor"
"Highest revenue routes"
"Routes with best CRR"
"Top performers by checkins"
```

**Parameters:**
- `kpi`: Column name (e.g., 'OTP%', 'Load Factor', 'CRR', 'Checkins')
- `service`: Service type filter (optional)
- `limit`: Number of top routes (default: 10)
- `ascending`: Sort order (default: False = highest first)

**Available KPIs:**
- OTP%
- Load Factor
- CRR
- Checkins
- Unsettled Revenue
- Cost / Rev Km
- Avg Fare

---

### 9. Route Performance (`get_route_performance`)

**Comprehensive Performance Metrics for a Route**

**Supported Queries:**
```
"Complete performance data for route E100"
"Detailed route metrics"
```

**Parameters:**
- `route_id`: Route to analyze (required)
- `month`: Month filter (optional)

**Output:** All 33 KPI columns for the route

---

### 10. Weekend vs Weekday Analysis (`analyze_weekend_vs_weekday`)

**Compare Weekend vs Weekday Performance**

**Supported Queries:**
```
"Compare weekend vs weekday performance"
"Weekend vs weekday for Urban service"
"Weekend vs weekday in July 2025"
```

**Parameters:**
- `service`: Service type (Urban/Intercity/Feeder/Seasonal) - optional
- `month`: Month filter (e.g., 'July 2025') - optional

**Note:** This analysis uses Daily Summary data which is aggregated by Service, not by individual routes. Route-level weekend/weekday analysis is not supported.



## Combined Queries (Multi-Function)

The LLM planner currently seems could not automatically combine multiple functions, will improve in the future.

