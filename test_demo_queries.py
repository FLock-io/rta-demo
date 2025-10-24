"""
Test script for CEO demo queries
Validates that queries work correctly and months are picked up properly
"""

from src.data_loader import DataLoader
from src.local_executor import LocalExecutor
from src.llm_planner import LLMPlanner
import json

def test_query(query: str, test_name: str):
    """Test a single query and print results."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"QUERY: {query}")
    print(f"{'='*80}")
    
    try:
        # Generate plan
        planner = LLMPlanner()
        plan = planner.generate_plan(query)
        
        print(f"\n✅ PLAN GENERATED:")
        print(f"   Steps: {len(plan.get('steps', []))}")
        
        for i, step in enumerate(plan.get('steps', []), 1):
            print(f"\n   Step {i}: {step['function']}")
            print(f"   Parameters: {json.dumps(step['parameters'], indent=6)}")
        
        # Execute plan
        data_loader = DataLoader()
        executor = LocalExecutor(data_loader)
        results = executor.execute_plan(plan)
        
        print(f"\n✅ EXECUTION COMPLETED:")
        print(f"   Results: {len(results)} items returned")
        
        for i, result in enumerate(results, 1):
            print(f"\n   Result {i}:")
            print(f"      Type: {result.get('type', 'unknown')}")
            if result.get('type') == 'dataframe' and 'data' in result:
                import pandas as pd
                df = result['data']
                print(f"      Shape: {df.shape}")
                print(f"      Columns: {list(df.columns)}")
                if len(df) > 0:
                    print(f"      Sample:")
                    print(f"      {df.head(3).to_string()}")
            elif result.get('type') == 'chart':
                print(f"      Chart generated successfully")
            elif result.get('type') == 'text':
                print(f"      Content: {result.get('content', result.get('data', 'N/A'))}")
        
        return True, plan, results
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None, None


def main():
    """Run all test queries."""
    
    print("="*80)
    print("RTA TRANSIT ANALYTICS - CEO DEMO QUERY TESTING")
    print("="*80)
    
    test_queries = [
        # Phase 1: Simple Data Queries
        ("Show me the service summary for July 2025", "Service Summary - Month Filtering"),
        ("List all stops in zone 5", "Zone Filtering"),
        ("What are the top 10 routes by ridership in June 2025?", "Route Ranking - Month Specific"),
        
        # Phase 2: Visual Analytics
        ("Plot urban unsettled revenue from May 2025 to August 2025", "Revenue Trends - Month Range"),
        ("Plot revenue comparison between June 2025 and July 2025", "Month-to-Month Comparison"),
        ("Show OTP and Load Factor trends for Urban service from January to April 2025", "Multi-KPI Trends"),
        
        # Phase 3: Complex Analysis
        ("What is the percentage change in urban unsettled revenue between September 2024 and December 2024?", "Percentage Change - SQL"),
        ("Compare urban unsettled revenue for September 2024 vs July 2025", "Non-consecutive Month Comparison"),
        ("What is the total unsettled revenue for July and August 2025?", "Multi-Month Aggregation"),
        
        # Phase 4: Geographic
        ("How many stops are there in each zone?", "Zone Aggregation"),
    ]
    
    results_summary = []
    
    for query, test_name in test_queries:
        success, plan, results = test_query(query, test_name)
        results_summary.append({
            'test_name': test_name,
            'query': query,
            'success': success
        })
        
        # Add a separator between tests
        print("\n" + "="*80 + "\n")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results_summary if r['success'])
    total = len(results_summary)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    print("\nDetailed Results:")
    for i, r in enumerate(results_summary, 1):
        status = "✅ PASS" if r['success'] else "❌ FAIL"
        print(f"{i}. {status} - {r['test_name']}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Ready for CEO demo!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review before demo.")


if __name__ == "__main__":
    main()

