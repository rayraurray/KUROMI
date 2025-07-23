from dash import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc
import pandas as pd
import numpy as np

from ..helpers.get_continent import get_continent
from ..helpers.tools import apply_filters, style_title
from ..styles import CHART_TITLE_CONFIG, VIZ_COLOR, TEXT_COLOR, FONT_FAMILY

def get_erosion_callbacks(df, app):
    """
    Focused erosion callbacks with three insightful visualizations
    """
    
    # KPI 1: Total Observations
    @app.callback(
        Output('kpi-total-observations', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('status-dropdown', 'value')
    )
    def update_total_observations(countries, years, erosion_levels, status):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels, selected_status=status)
        
        total = len(d)
        return f"{total:,}"

    # KPI 2: Critical Risk Areas (High/Very High/Severe/Critical risk levels)
    @app.callback(
        Output('kpi-critical-risk-areas', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('status-dropdown', 'value')
    )
    def update_critical_risk_areas(countries, years, erosion_levels, status):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels, selected_status=status)
        
        if d.empty:
            return "0"
        
        critical_indicators = ['High', 'Very high', 'Severe', 'Critical', 'Extreme']
        critical_count = d[d['erosion_risk_level'].str.contains('|'.join(critical_indicators), case=False, na=False)].shape[0]
        return f"{critical_count:,}"

    # KPI 3: Average Erosion Intensity
    @app.callback(
        Output('kpi-avg-erosion-intensity', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('status-dropdown', 'value')
    )
    def update_avg_erosion_intensity(countries, years, erosion_levels, status):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels, selected_status=status)
        
        avg = d['obs_value'].mean() if not d.empty else 0
        return f"{avg:.1f}"

    # KPI 4: Countries Affected
    @app.callback(
        Output('kpi-countries-affected', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('status-dropdown', 'value')
    )
    def update_countries_affected(countries, years, erosion_levels, status):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels, selected_status=status)
        
        unique_countries = d['country'].nunique() if not d.empty else 0
        return f"{unique_countries:,}"

    # Visualization 1: Erosion Risk Evolution Over Time
    @app.callback(
        Output('erosion-temporal-evolution', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('status-dropdown', 'value')
    )
    def update_erosion_temporal_evolution(countries, years, erosion_levels, status):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels, selected_status=status)
        
        if d.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available for selected filters", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(title=style_title('No Data Available'), 
                            paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR)
            return fig
        
        # Add continent information
        if 'continent' not in d.columns:
            d['continent'] = d['country'].apply(get_continent)
        
        # Temporal analysis by erosion type and continent
        temporal_data = d.groupby(['year', 'measure_category', 'continent']).agg({
            'obs_value': ['mean', 'count', 'std']
        }).reset_index()
        
        temporal_data.columns = ['year', 'measure_category', 'continent', 'avg_intensity', 'observation_count', 'volatility']
        temporal_data['volatility'] = temporal_data['volatility'].fillna(0)
        
        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Average Erosion Intensity Over Time', 'Observation Count and Risk Volatility'),
            vertical_spacing=0.12,
            specs=[[{"secondary_y": True}], [{"secondary_y": True}]]
        )
        
        # Color palette for different erosion types
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
        erosion_types = temporal_data['measure_category'].unique()
        
        # Top panel: Average intensity over time
        for i, erosion_type in enumerate(erosion_types):
            type_data = temporal_data[temporal_data['measure_category'] == erosion_type]
            yearly_avg = type_data.groupby('year')['avg_intensity'].mean().reset_index()
            
            fig.add_trace(
                go.Scatter(
                    x=yearly_avg['year'],
                    y=yearly_avg['avg_intensity'],
                    mode='lines+markers',
                    name=f'{erosion_type}',
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8),
                    fill='tonexty' if i > 0 else 'tozeroy',
                    fillcolor=f'rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.3)'
                ),
                row=1, col=1
            )
        
        # Bottom panel: Observation count (bars) and volatility (line)
        yearly_totals = temporal_data.groupby('year').agg({
            'observation_count': 'sum',
            'volatility': 'mean'
        }).reset_index()
        
        fig.add_trace(
            go.Bar(
                x=yearly_totals['year'],
                y=yearly_totals['observation_count'],
                name='Observations',
                marker_color='rgba(70, 130, 180, 0.8)',
                yaxis='y3'
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=yearly_totals['year'],
                y=yearly_totals['volatility'],
                mode='lines+markers',
                name='Risk Volatility',
                line=dict(color='orange', width=3),
                marker=dict(size=10, color='orange'),
                yaxis='y4'
            ),
            row=2, col=1, secondary_y=True
        )
        
        # Update layout
        fig.update_layout(
            title=style_title('Erosion Risk Evolution: Temporal Trends and Patterns'),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=60, r=60, t=100, b=60),
            height=700,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Update axes
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="Average Intensity", row=1, col=1)
        fig.update_yaxes(title_text="Observations", row=2, col=1)
        fig.update_yaxes(title_text="Risk Volatility", row=2, col=1, secondary_y=True)
        
        return fig

    # Visualization 2: Geographic Risk Distribution Heatmap
    @app.callback(
        Output('erosion-geographic-heatmap', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('status-dropdown', 'value')
    )
    def update_erosion_geographic_heatmap(countries, years, erosion_levels, status):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels, selected_status=status)
        
        if d.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available for selected filters", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(title=style_title('No Data Available'), 
                            paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR)
            return fig
        
        # Add continent information
        if 'continent' not in d.columns:
            d['continent'] = d['country'].apply(get_continent)
        
        # Create comprehensive geographic analysis
        geo_data = d.groupby(['country', 'measure_category', 'continent']).agg({
            'obs_value': ['mean', 'count', 'max', 'std']
        }).reset_index()
        
        geo_data.columns = ['country', 'measure_category', 'continent', 'avg_intensity', 'observation_count', 'max_intensity', 'risk_variability']
        geo_data['risk_variability'] = geo_data['risk_variability'].fillna(0)
        
        # Create matrix for heatmap
        heatmap_matrix = geo_data.pivot_table(
            index='country', 
            columns='measure_category', 
            values='avg_intensity', 
            fill_value=0
        )
        
        # Create subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Average Erosion Intensity by Country & Type', 'Risk Distribution by Continent', 
                          'Observation Density', 'High Risk Concentration'),
            specs=[[{"type": "heatmap"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "box"}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.08
        )
        
        # Top-left: Main heatmap
        fig.add_trace(
            go.Heatmap(
                z=heatmap_matrix.values,
                x=heatmap_matrix.columns,
                y=heatmap_matrix.index,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(x=0.45, len=0.4),
                text=heatmap_matrix.values.round(2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverinformation='z+x+y'
            ),
            row=1, col=1
        )
        
        # Top-right: Continental risk distribution
        continent_risk = geo_data.groupby('continent')['avg_intensity'].mean().sort_values(ascending=False)
        fig.add_trace(
            go.Bar(
                x=continent_risk.index,
                y=continent_risk.values,
                marker_color='rgba(255, 99, 71, 0.8)',
                text=continent_risk.values.round(2),
                textposition='auto',
            ),
            row=1, col=2
        )
        
        # Bottom-left: Observation density scatter
        fig.add_trace(
            go.Scatter(
                x=geo_data['observation_count'],
                y=geo_data['avg_intensity'],
                mode='markers',
                marker=dict(
                    size=geo_data['risk_variability'] * 2 + 5,
                    color=geo_data['max_intensity'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(x=1.05, len=0.4),
                    opacity=0.7,
                    line=dict(width=1, color='white')
                ),
                text=[f"{country}<br>Continent: {continent}<br>Max Risk: {max_risk:.1f}" 
                      for country, continent, max_risk in zip(geo_data['country'], geo_data['continent'], geo_data['max_intensity'])],
                hovertemplate='<b>%{text}</b><br>Observations: %{x}<br>Avg Intensity: %{y:.2f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Bottom-right: Risk distribution by erosion type
        for erosion_type in geo_data['measure_category'].unique():
            type_data = geo_data[geo_data['measure_category'] == erosion_type]
            fig.add_trace(
                go.Box(
                    y=type_data['avg_intensity'],
                    name=erosion_type,
                    boxpoints='outliers',
                    jitter=0.3,
                    pointpos=-1.8
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title=style_title('Geographic Erosion Risk Distribution: Comprehensive Analysis'),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=80, r=120, t=100, b=80),
            height=800,
            showlegend=False
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Erosion Type", row=1, col=1)
        fig.update_yaxes(title_text="Country", row=1, col=1)
        fig.update_xaxes(title_text="Continent", row=1, col=2)
        fig.update_yaxes(title_text="Avg Intensity", row=1, col=2)
        fig.update_xaxes(title_text="Observation Count", row=2, col=1)
        fig.update_yaxes(title_text="Avg Intensity", row=2, col=1)
        fig.update_xaxes(title_text="Erosion Type", row=2, col=2)
        fig.update_yaxes(title_text="Risk Intensity", row=2, col=2)
        
        return fig

    # Visualization 3: Risk Level Distribution & Comparative Analysis
    @app.callback(
        Output('erosion-risk-comparison', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('status-dropdown', 'value')
    )
    def update_erosion_risk_comparison(countries, years, erosion_levels, status):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels, selected_status=status)
        
        if d.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available for selected filters", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(title=style_title('No Data Available'), 
                            paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR)
            return fig
        
        # Add continent information
        if 'continent' not in d.columns:
            d['continent'] = d['country'].apply(get_continent)
        
        # Create subplot layout for comparative analysis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Risk Level Distribution by Erosion Type', 'Continental Risk Comparison', 
                          'Risk Intensity Violin Plots', 'Risk Level Evolution'),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "violin"}, {"type": "scatter"}]],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Top-left: Risk level distribution by erosion type
        risk_dist = d.groupby(['measure_category', 'erosion_risk_level']).size().unstack(fill_value=0)
        
        colors_risk = ['#2E8B57', '#FFD700', '#FF6347', '#DC143C', '#8B0000']
        for i, risk_level in enumerate(risk_dist.columns):
            fig.add_trace(
                go.Bar(
                    x=risk_dist.index,
                    y=risk_dist[risk_level],
                    name=risk_level,
                    marker_color=colors_risk[i % len(colors_risk)],
                    text=risk_dist[risk_level],
                    textposition='auto'
                ),
                row=1, col=1
            )
        
        # Top-right: Continental risk scatter with trend
        continent_analysis = d.groupby(['continent', 'year']).agg({
            'obs_value': ['mean', 'count', 'std']
        }).reset_index()
        continent_analysis.columns = ['continent', 'year', 'avg_risk', 'count', 'std']
        continent_analysis['std'] = continent_analysis['std'].fillna(0)
        
        continent_colors = {'Asia': '#FF6B6B', 'Europe': '#4ECDC4', 'Africa': '#45B7D1', 
                          'North America': '#96CEB4', 'South America': '#FECA57', 'Oceania': '#FF8C69'}
        
        for continent in continent_analysis['continent'].unique():
            cont_data = continent_analysis[continent_analysis['continent'] == continent]
            fig.add_trace(
                go.Scatter(
                    x=cont_data['year'],
                    y=cont_data['avg_risk'],
                    mode='markers+lines',
                    name=continent,
                    marker=dict(
                        size=cont_data['count']/2,
                        color=continent_colors.get(continent, '#999999'),
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    line=dict(color=continent_colors.get(continent, '#999999'), width=2)
                ),
                row=1, col=2
            )
        
        # Bottom-left: Violin plots for risk distribution
        erosion_types = d['measure_category'].unique()
        colors_violin = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, erosion_type in enumerate(erosion_types):
            type_data = d[d['measure_category'] == erosion_type]
            fig.add_trace(
                go.Violin(
                    y=type_data['obs_value'],
                    name=erosion_type,
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor=colors_violin[i % len(colors_violin)],
                    opacity=0.6,
                    x0=erosion_type
                ),
                row=2, col=1
            )
        
        # Bottom-right: Risk evolution with confidence intervals
        yearly_risk = d.groupby('year').agg({
            'obs_value': ['mean', 'std', 'count']
        }).reset_index()
        yearly_risk.columns = ['year', 'mean_risk', 'std_risk', 'count']
        yearly_risk['std_risk'] = yearly_risk['std_risk'].fillna(0)
        yearly_risk['ci_upper'] = yearly_risk['mean_risk'] + 1.96 * (yearly_risk['std_risk'] / np.sqrt(yearly_risk['count']))
        yearly_risk['ci_lower'] = yearly_risk['mean_risk'] - 1.96 * (yearly_risk['std_risk'] / np.sqrt(yearly_risk['count']))
        
        # Add confidence interval
        fig.add_trace(
            go.Scatter(
                x=yearly_risk['year'].tolist() + yearly_risk['year'].tolist()[::-1],
                y=yearly_risk['ci_upper'].tolist() + yearly_risk['ci_lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(70, 130, 180, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% Confidence Interval',
                showlegend=True
            ),
            row=2, col=2
        )
        
        # Add mean line
        fig.add_trace(
            go.Scatter(
                x=yearly_risk['year'],
                y=yearly_risk['mean_risk'],
                mode='lines+markers',
                name='Mean Risk',
                line=dict(color='red', width=3),
                marker=dict(size=8, color='red')
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=style_title('Erosion Risk Analysis: Distribution Patterns and Comparisons'),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=80, r=80, t=100, b=80),
            height=800,
            hovermode='closest',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        
        # Update axes
        fig.update_xaxes(title_text="Erosion Type", row=1, col=1)
        fig.update_yaxes(title_text="Count", row=1, col=1)
        fig.update_xaxes(title_text="Year", row=1, col=2)
        fig.update_yaxes(title_text="Average Risk", row=1, col=2)
        fig.update_xaxes(title_text="Erosion Type", row=2, col=1)
        fig.update_yaxes(title_text="Risk Intensity", row=2, col=1)
        fig.update_xaxes(title_text="Year", row=2, col=2)
        fig.update_yaxes(title_text="Risk Level", row=2, col=2)
        
        return fig