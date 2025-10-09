"""
Visualization functions for RTA Transit Analytics
Handles all chart and plot generation
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, List
from .data_loader import DataLoader


class Visualizer:
    """Handles all visualization and plotting functions"""

    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def plot_monthly_kpi_trends(self, service: Optional[str] = None, kpis: Optional[List[str]] = None):
        """
        Plot monthly KPI trends as line charts.

        Args:
            service: Optional service type filter
            kpis: Optional list of specific KPIs to plot (e.g., ['OTP%', 'Load Factor', 'CRR'])

        Returns:
            Plotly figure with line charts
        """
        df = self.data_loader.get_totals_summary()

        if df.empty:
            return None

        # Filter by service if provided
        if service:
            df = df[df['Service'].str.lower() == service.lower()]

        # Determine which KPIs to plot
        if kpis:
            plot_kpis = kpis
        else:
            # Default KPIs for plotting
            plot_kpis = ['OTP%', 'Load Factor', 'CRR', 'Checkins']

        # Filter to available KPIs
        plot_kpis = [kpi for kpi in plot_kpis if kpi in df.columns]

        if not plot_kpis:
            return None

        # Sort by Month
        df = df.sort_values('Month')

        # Create figure
        if 'Service' in df.columns and not service:
            # Multiple services - use color coding
            fig = go.Figure()

            for kpi in plot_kpis:
                for svc in df['Service'].unique():
                    svc_data = df[df['Service'] == svc]
                    fig.add_trace(go.Scatter(
                        x=svc_data['Month'],
                        y=svc_data[kpi],
                        mode='lines+markers',
                        name=f"{svc} - {kpi}",
                        line=dict(width=2),
                        marker=dict(size=6)
                    ))

            title = "Monthly KPI Trends - All Services"
        else:
            # Single service or service filtered
            fig = go.Figure()

            for kpi in plot_kpis:
                fig.add_trace(go.Scatter(
                    x=df['Month'],
                    y=df[kpi],
                    mode='lines+markers',
                    name=kpi,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))

            service_name = service if service else "All Services"
            title = f"Monthly KPI Trends - {service_name}"

        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Month",
            yaxis_title="Value",
            hovermode='x unified',
            template='plotly_white',
            height=500,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )

        # Rotate x-axis labels for better readability
        fig.update_xaxes(tickangle=-45)

        return fig
