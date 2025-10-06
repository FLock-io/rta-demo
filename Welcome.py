"""
RTA Transit Analytics - Welcome Page
Main landing page with navigation to different features.
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def main():
    st.set_page_config(
        page_title="RTA Transit Analytics",
        page_icon="🚇",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for welcome page
    st.markdown(
        """
    <style>
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .feature-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    .stats-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
    }
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    .nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        margin: 0.5rem;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
    }
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🚇 RTA Transit Analytics</h1>
        <h3>AI-Powered Transit Data Analysis for Dubai RTA</h3>
        <p>Explore Dubai's transit system with intelligent data analysis and insights</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("## 🎯 Welcome to RTA Analytics Platform")

        st.markdown(
            """
        <div class="feature-card">
            <h4>🤖 AI-Powered Chat Assistant</h4>
            <p>Ask natural language questions about Dubai's transit system and get instant, data-driven answers.
            Our AI understands your queries and provides comprehensive analysis with visualizations.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="feature-card">
            <h4>📊 Comprehensive Data Analysis</h4>
            <p>Analyze route performance, station usage, service frequency, and network connectivity.
            Access both GTFS open data and confidential TTSS route summaries for complete insights.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="feature-card">
            <h4>🗺️ Interactive Visualizations</h4>
            <p>Generate interactive maps, charts, and dashboards to visualize transit patterns,
            coverage areas, and performance metrics across Dubai's metro and bus networks.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Navigation button
        st.markdown("### 🚀 Get Started")

        # Custom CSS for button color
        st.markdown(
            """
        <style>
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        if st.button(
            "💬 Chat with AI Assistant", use_container_width=True, type="primary"
        ):
            st.switch_page("pages/ChatBot.py")

    with col2:
        st.markdown("## 📈 System Overview")

        # Stats container
        st.markdown(
            """
        <div class="stats-container">
            <div class="stat-item">
                <h3 style="color: #667eea; margin: 0;">Data Sources</h3>
                <h2 style="margin: 0.5rem 0;">GTFS + TTSS</h2>
                <p style="margin: 0; color: #666;">Open & Confidential Data</p>
            </div>
            <hr style="margin: 1rem 0;">
            <div class="stat-item">
                <h3 style="color: #667eea; margin: 0;">Analysis Functions</h3>
                <h2 style="margin: 0.5rem 0;">10+</h2>
                <p style="margin: 0; color: #666;">Built-in Analytics</p>
            </div>
            <hr style="margin: 1rem 0;">
            <div class="stat-item">
                <h3 style="color: #667eea; margin: 0;">Transit Modes</h3>
                <h2 style="margin: 0.5rem 0;">Metro + Bus</h2>
                <p style="margin: 0; color: #666;">Complete Coverage</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666;">
        <p>Built for Dubai RTA | Powered by Flock.io</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
