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

    def _sort_by_month(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort DataFrame by month in chronological order."""
        if df.empty or 'Month' not in df.columns:
            return df
            
        # Define month order mapping
        month_order = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
        # Extract month name and year from Month column
        def get_month_sort_key(month_str):
            try:
                # Handle formats like "July 2025", "December 2024"
                parts = month_str.split()
                if len(parts) >= 2:
                    month_name = parts[0]
                    year = int(parts[1])
                    month_num = month_order.get(month_name, 13)  # 13 for unknown months
                    return (year, month_num)
                else:
                    return (9999, 13)  # Put unknown formats at end
            except:
                return (9999, 13)  # Put errors at end
        
        # Add sort key column
        df = df.copy()
        df['_sort_key'] = df['Month'].apply(get_month_sort_key)
        
        # Sort by the sort key
        df = df.sort_values('_sort_key')
        
        # Remove the sort key column
        df = df.drop('_sort_key', axis=1)
        
        return df

    def plot_monthly_kpi_trends(self, service: Optional[str] = None, kpis: Optional[List[str]] = None, months: Optional[List[str]] = None):
        """
        Plot monthly KPI trends as line charts.

        Args:
            service: Optional service type filter
            kpis: Optional list of specific KPIs to plot (e.g., ['OTP%', 'Load Factor', 'CRR'])
            months: Optional list of specific months to filter (e.g., ['May 2025', 'June 2025', 'July 2025', 'August 2025'])

        Returns:
            Plotly figure with line charts
        """
        df = self.data_loader.get_totals_summary(months=months)

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

        # Sort by Month in chronological order
        df = self._sort_by_month(df)

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

    def plot_daily_kpi_trends(self, month: str, service: Optional[str] = None, kpis: Optional[List[str]] = None):
        """
        Plot DAILY KPI trends as line charts for a specific month.

        Args:
            month: Month to plot (e.g., 'August 2025')
            service: Optional service type filter
            kpis: Optional list of specific KPIs to plot (e.g., ['Unsettled Revenue', 'OTP%', 'Load Factor'])

        Returns:
            Plotly figure with line charts
        """
        # Load daily summary data for the specified month
        df = self.data_loader.get_daily_summary(months=[month])

        if df.empty:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"No daily data available for {month}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Filter by service if provided
        if service:
            df = df[df['Service'].str.lower() == service.lower()]

        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text=f"No data for service '{service}' in {month}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Determine which KPIs to plot
        if kpis:
            plot_kpis = kpis
        else:
            # Default KPIs for plotting
            plot_kpis = ['Unsettled Revenue', 'OTP%', 'Load Factor', 'Checkins']

        # Filter to available KPIs
        plot_kpis = [kpi for kpi in plot_kpis if kpi in df.columns]

        if not plot_kpis:
            fig = go.Figure()
            fig.add_annotation(
                text="No valid KPIs found in data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig

        # Sort by date
        df = df.sort_values('Date')

        # Create figure
        fig = go.Figure()

        # If service-level data (multiple services), create separate traces per service
        if 'Service' in df.columns and df['Service'].nunique() > 1 and not service:
            for svc in df['Service'].unique():
                svc_df = df[df['Service'] == svc]
                for kpi in plot_kpis:
                    fig.add_trace(go.Scatter(
                        x=svc_df['Date'],
                        y=svc_df[kpi],
                        mode='lines+markers',
                        name=f"{svc} - {kpi}",
                        line=dict(width=2),
                        marker=dict(size=6)
                    ))
            title = f"Daily KPI Trends - {month}"
        else:
            # Single service or filtered by service
            for kpi in plot_kpis:
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df[kpi],
                    mode='lines+markers',
                    name=kpi,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))

            service_name = service if service else "All Services"
            title = f"Daily KPI Trends - {service_name} - {month}"

        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Date",
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

        # Format x-axis to show dates nicely
        fig.update_xaxes(tickformat="%b %d", tickangle=-45)

        return fig

    def plot_month_comparison(self, month1: str, month2: str, service: Optional[str] = None, kpis: Optional[List[str]] = None):
        """
        Plot comparison between two specific months.
        
        Args:
            month1: First month (e.g., 'July 2025')
            month2: Second month (e.g., 'August 2025')
            service: Optional service type filter
            kpis: Optional list of specific KPIs to compare
            
        Returns:
            Plotly figure with comparison chart
        """
        # Use totals summary for service-level comparisons, monthly data for route-level
        if service:
            months_data = self.data_loader.get_totals_summary(months=[month1, month2])
        else:
            months_data = self.data_loader.get_monthly_data(months=[month1, month2])
        
        if months_data.empty:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"No data found for {month1} and {month2}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Month Comparison: {month1} vs {month2}",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template='plotly_white',
                height=400
            )
            return fig
            
        # Filter by service if provided
        if service:
            months_data = months_data[months_data['Service'].str.lower() == service.lower()]
            
        # Determine which KPIs to compare
        if kpis:
            plot_kpis = kpis
        else:
            # Default KPIs for comparison
            plot_kpis = ['OTP%', 'Load Factor', 'CRR', 'Checkins', 'Unsettled Revenue']
            
        # Filter to available KPIs
        available_kpis = [kpi for kpi in plot_kpis if kpi in months_data.columns]
        
        if not available_kpis:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"No available KPIs found for comparison",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Month Comparison: {month1} vs {month2}",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template='plotly_white',
                height=400
            )
            return fig
            
        # Create comparison chart with better structure
        fig = go.Figure()
        
        # Prepare data for grouped bar chart
        x_labels = []
        month1_values = []
        month2_values = []
        
        for kpi in available_kpis:
            month1_data = months_data[months_data['Month'] == month1]
            month2_data = months_data[months_data['Month'] == month2]
            
            if not month1_data.empty and not month2_data.empty:
                month1_avg = month1_data[kpi].mean()
                month2_avg = month2_data[kpi].mean()
                
                x_labels.append(kpi)
                month1_values.append(month1_avg)
                month2_values.append(month2_avg)
        
        if not x_labels:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"No data found for comparison between {month1} and {month2}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Month Comparison: {month1} vs {month2}",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template='plotly_white',
                height=400
            )
            return fig
            
        # Add traces for each month
        fig.add_trace(go.Bar(
            name=month1,
            x=x_labels,
            y=month1_values,
            text=[f"{v:.1f}" for v in month1_values],
            textposition='auto',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name=month2,
            x=x_labels,
            y=month2_values,
            text=[f"{v:.1f}" for v in month2_values],
            textposition='auto',
            marker_color='lightcoral'
        ))
        
        # Update layout
        fig.update_layout(
            title=f"Month Comparison: {month1} vs {month2}",
            xaxis_title="KPI",
            yaxis_title="Average Value",
            template='plotly_white',
            height=500,
            barmode='group',
            showlegend=True
        )
        
        return fig

    def plot_quarterly_comparison(self, quarter1: str, quarter2: str, service: Optional[str] = None, kpis: Optional[List[str]] = None):
        """
        Plot comparison between two quarters.
        
        Args:
            quarter1: First quarter (e.g., 'Q1 2025')
            quarter2: Second quarter (e.g., 'Q2 2025')
            service: Optional service type filter
            kpis: Optional list of specific KPIs to compare
            
        Returns:
            Plotly figure with quarterly comparison chart
        """
        # Map quarters to months
        quarter_months = {
            'Q1 2025': ['January 2025', 'February 2025', 'March 2025'],
            'Q2 2025': ['April 2025', 'May 2025', 'June 2025'],
            'Q3 2025': ['July 2025', 'August 2025', 'September 2025'],
            'Q4 2024': ['October 2024', 'November 2024', 'December 2024'],
            'Q1 2024': ['January 2024', 'February 2024', 'March 2024'],
            'Q2 2024': ['April 2024', 'May 2024', 'June 2024'],
            'Q3 2024': ['July 2024', 'August 2024', 'September 2024'],
            'Q4 2024': ['October 2024', 'November 2024', 'December 2024']
        }
        
        if quarter1 not in quarter_months or quarter2 not in quarter_months:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"Invalid quarters: {quarter1} or {quarter2} not found",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Quarterly Comparison: {quarter1} vs {quarter2}",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template='plotly_white',
                height=400
            )
            return fig
            
        # Get data for both quarters
        quarter1_months = quarter_months[quarter1]
        quarter2_months = quarter_months[quarter2]
        
        all_months = quarter1_months + quarter2_months
        quarters_data = self.data_loader.get_monthly_data(months=all_months)
        
        if quarters_data.empty:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"No data found for {quarter1} and {quarter2}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Quarterly Comparison: {quarter1} vs {quarter2}",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template='plotly_white',
                height=400
            )
            return fig
            
        # Filter by service if provided
        if service:
            quarters_data = quarters_data[quarters_data['Service'].str.lower() == service.lower()]
            
        # Determine which KPIs to compare
        if kpis:
            plot_kpis = kpis
        else:
            # Default KPIs for quarterly comparison
            plot_kpis = ['OTP%', 'Load Factor', 'CRR', 'Checkins', 'Unsettled Revenue']
            
        # Filter to available KPIs
        plot_kpis = [kpi for kpi in plot_kpis if kpi in quarters_data.columns]
        
        if not plot_kpis:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text=f"No available KPIs found for quarterly comparison",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title=f"Quarterly Comparison: {quarter1} vs {quarter2}",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                template='plotly_white',
                height=400
            )
            return fig
            
        # Calculate quarterly averages
        quarter1_data = quarters_data[quarters_data['Month'].isin(quarter1_months)]
        quarter2_data = quarters_data[quarters_data['Month'].isin(quarter2_months)]
        
        # Create comparison chart
        fig = go.Figure()
        
        for kpi in plot_kpis:
            if not quarter1_data.empty and not quarter2_data.empty:
                q1_avg = quarter1_data[kpi].mean()
                q2_avg = quarter2_data[kpi].mean()
                
                fig.add_trace(go.Bar(
                    name=quarter1,
                    x=[kpi],
                    y=[q1_avg],
                    text=f"{q1_avg:.1f}",
                    textposition='auto'
                ))
                
                fig.add_trace(go.Bar(
                    name=quarter2,
                    x=[kpi],
                    y=[q2_avg],
                    text=f"{q2_avg:.1f}",
                    textposition='auto'
                ))
        
        # Update layout
        fig.update_layout(
            title=f"Quarterly Comparison: {quarter1} vs {quarter2}",
            xaxis_title="KPI",
            yaxis_title="Average Value",
            template='plotly_white',
            height=500,
            barmode='group'
        )
        
        return fig
