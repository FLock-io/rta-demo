"""
RTA Transit Analytics Chat Assistant
AI-powered conversational interface for transit data analysis
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.llm_planner import LLMPlanner
from src.local_executor import LocalExecutor
from src.data_loader import DataLoader
from dotenv import load_dotenv

load_dotenv()


def main():
    st.set_page_config(page_title="RTA Chat Assistant", page_icon="🤖", layout="wide")

    # Initialize components
    if "data_loader" not in st.session_state:
        st.session_state.data_loader = DataLoader()
        st.session_state.llm_planner = LLMPlanner()
        st.session_state.local_executor = LocalExecutor(st.session_state.data_loader)
        st.session_state.messages = []

    # Header
    st.title("🚇 RTA Chat Assistant")
    st.caption("Ask me anything about Dubai's transit system")

    # Show welcome message and examples if no chat history
    if not st.session_state.messages:
        show_welcome_and_examples()

    # Display chat messages
    for msg_idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])

            if "plan" in message:
                display_execution_plan(message["plan"])

            if "results" in message:
                display_results(message["results"], msg_idx)

    # Chat input
    if prompt := st.chat_input("Ask a question about RTA transit data..."):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Set processing flag
        st.session_state.processing = True

        # Rerun to show user message and start processing
        st.rerun()

    # Process query if flag is set
    if st.session_state.get("processing", False):
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get the last user message
                last_user_msg = st.session_state.messages[-1]["content"]
                response = process_query(last_user_msg)
                st.session_state.messages.append(response)
                st.session_state.processing = False

                st.write("Here's what I found:")

                if "plan" in response:
                    display_execution_plan(response["plan"])

                if "results" in response:
                    # Use length of messages as index for new response
                    display_results(response["results"], len(st.session_state.messages) - 1)
                st.rerun()


def process_query(query):
    """Process user query and return response"""
    try:
        # Generate plan
        plan = st.session_state.llm_planner.generate_plan(query)

        # Execute plan
        results = st.session_state.local_executor.execute_plan(plan)

        return {
            "role": "assistant",
            "content": f"Analysis completed for: '{query}'",
            "plan": plan,
            "results": results,
        }

    except Exception as e:
        return {
            "role": "assistant",
            "content": f"Sorry, I encountered an error: {str(e)}",
            "results": [
                {
                    "type": "text",
                    "title": "Error",
                    "content": f"Error processing your request: {str(e)}",
                }
            ],
        }


def show_welcome_and_examples():
    """Show example queries in the main area"""
    # Example questions section
    st.subheader("💡 Try these sample questions:")

    sample_queries = [
        "Show me all metro routes and their names",
        "Find all stations with 'Mall' in the name",
        "Show coverage map of all stops",
        "What are the busiest stops?",
        "Generate a route map",
        "Show all transfer points",
        "Analyze service frequency for metro routes",
        "Show stop count by zone",
    ]

    # Display examples in a grid
    col1, col2 = st.columns(2)

    for i, query in enumerate(sample_queries):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(query, key=f"example_{i}", use_container_width=True):
                # Add to messages and trigger rerun
                st.session_state.messages.append({"role": "user", "content": query})
                response = process_query(query)
                st.session_state.messages.append(response)
                st.rerun()

    st.markdown("---")

    # Tips section
    st.info(
        """
    **💡 Tips for better results:**
    • Be specific about what you want to analyze
    • Ask for charts or maps when helpful
    • Request comparisons between routes/stations
    • Ask about performance metrics
    """
    )

    # Clear button
    # if st.button("🗑️ Clear Chat History", type="secondary"):
    #     st.session_state.messages = []
    #     st.rerun()


def display_execution_plan(plan):
    """Display execution plan in a collapsible format"""
    with st.expander("🔧 Execution Plan & Methodology", expanded=False):
        st.write(
            f"**Query Interpretation:** {plan.get('interpretation', 'Processing your request...')}"
        )

        for i, step in enumerate(plan.get("steps", []), 1):
            status = "✅" if step.get("completed") else "⏳"

            st.write(
                f"{status} **Step {i}:** {step.get('description', 'Unknown step')}"
            )
            st.code(f"Function: {step.get('function', 'unknown')}")

            if step.get("parameters"):
                st.caption(f"Parameters: {step.get('parameters', {})}")


def display_results(results, message_idx):
    """Display analysis results with unique keys based on message index"""
    for result_idx, result in enumerate(results):
        if result["type"] == "dataframe":
            st.subheader(f"📊 {result['title']}")
            st.dataframe(result["data"], use_container_width=True)

        elif result["type"] == "chart":
            st.subheader(f"📈 {result['title']}")
            # Generate unique key based on message index and result index
            chart_key = f"chart_msg{message_idx}_result{result_idx}"
            st.plotly_chart(result["data"], use_container_width=True, key=chart_key)

        elif result["type"] == "metric":
            st.metric(result["title"], result["value"], result.get("delta"))

        elif result["type"] == "text":
            st.subheader(f"📝 {result['title']}")
            st.write(result["content"])


if __name__ == "__main__":
    main()
