# RTA Transit Analytics - AI-Powered Data Analysis

An intelligent chatbot for analyzing Dubai's transit system using natural language queries.

---

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Or set the environment variable directly:
```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Run the Application
```bash
streamlit run Welcome.py
```

---

## Example Questions

### Basic Data Queries
- "Show me all routes"
- "List all stops in zone 5"
- "How many stops are in each zone?"
- "What is the route name for 1004?"

### Performance Analysis
- "What are the top 10 routes by ridership in June 2025?"
- "Show me OTP performance for route E100 in August 2025"
- "Which routes generated the most revenue in August 2025?"
- "What are the 5 least efficient routes in August 2025?"

### Visualizations
- "Plot urban revenue from May to August 2025"
- "Show route E100 on a map"
- "Plot all stops in zone 5 on a map"
- "Plot daily urban revenue for August 2025"

### Advanced Analysis
- "What is the percentage change in urban revenue between July and August 2025?"
- "Which day had the most revenue in August 2025?"
- "Compare urban revenue for June vs July 2025"
- "What zones generated the most revenue in August 2025?"

---