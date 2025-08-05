from dash import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..helpers.get_continent import get_continent
from ..helpers.tools import apply_filters, style_title, normalize_by_agricultural_land
from ..styles import VIZ_COLOR, TEXT_COLOR, FONT_FAMILY

def get_erosion_callbacks(df, app):

    # KPI 1: Total Observations
    @app.callback(
        Output('kpi-total-observations', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_total_observations(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        total = len(d)
        return f"{total:,}"

    # KPI 2: Agricultural Land at Risk
    @app.callback(
        Output('kpi-land-at-risk', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_land_at_risk(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        # Get total agricultural land affected by erosion
        total_land_data = d[d['erosion_risk_level'] == 'Total']
        if total_land_data.empty:
            # If no 'Total' data, calculate from all risk levels
            avg_land = d['obs_value'].mean() if not d.empty else 0
        else:
            avg_land = total_land_data['obs_value'].mean()
        
        return f"{avg_land:.1f}%"

    # KPI 3: Severe Risk Percentage
    @app.callback(
        Output('kpi-severe-risk-percent', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_severe_risk_percent(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        if d.empty:
            return "0%"
        
        # Exclude 'Total' observations for this calculation
        d_filtered = d[d['erosion_risk_level'] != 'Total']
        if d_filtered.empty:
            return "0%"
        
        severe_count = len(d_filtered[d_filtered['erosion_risk_level'] == 'Severe'])
        total_count = len(d_filtered)
        percentage = (severe_count / total_count) * 100 if total_count > 0 else 0
        
        return f"{percentage:.1f}%"

    # KPI 4: High-Risk Countries
    @app.callback(
        Output('kpi-high-risk-countries', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_high_risk_countries(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        # Count countries with High or Severe erosion risk
        high_risk_indicators = ['High', 'Severe']
        high_risk_data = d[d['erosion_risk_level'].isin(high_risk_indicators)]
        high_risk_countries_count = high_risk_data['country'].nunique() if not high_risk_data.empty else 0
        
        return f"{high_risk_countries_count}"

    # HOVER DETAIL CALLBACKS
    @app.callback(
        Output('kpi-total-observations-card', 'title'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_total_observations_hover(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        if d.empty:
            return "No observations found for selected filters"
        
        type_breakdown = d['measure_category'].value_counts()
        risk_breakdown = d[d['erosion_risk_level'] != 'Total']['erosion_risk_level'].value_counts()
        year_range = f"{d['year'].min()}-{d['year'].max()}" if d['year'].nunique() > 1 else str(d['year'].iloc[0])
        
        # Build strings with consistent formatting
        newline = '\n'
        type_lines = []
        for erosion_type, count in type_breakdown.items():
            type_lines.append(f"• {erosion_type}: {count} observations")
        
        risk_lines = []
        for risk, count in risk_breakdown.items():
            risk_lines.append(f"• {risk}: {count} observations")
        
        return f"""Total Observations: {len(d):,}

By Erosion Type:
{newline.join(type_lines)}

By Risk Level:
{newline.join(risk_lines)}

Year Range: {year_range}
Countries: {d['country'].nunique()} unique"""

    @app.callback(
        Output('kpi-land-at-risk-card', 'title'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_land_at_risk_hover(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        if d.empty:
            return "No land risk data available"
        
        total_land_data = d[d['erosion_risk_level'] == 'Total']
        if total_land_data.empty:
            country_details = d.groupby('country')['obs_value'].mean().sort_values(ascending=False)
            data_source = "calculated from risk levels"
        else:
            country_details = total_land_data.groupby('country')['obs_value'].mean().sort_values(ascending=False)
            data_source = "total land measurements"
        
        top_countries = country_details.head(8)
        
        # Build strings with consistent formatting
        newline = '\n'
        country_lines = []
        for country, percentage in top_countries.items():
            country_lines.append(f"• {country}: {percentage:.1f}%")
        
        return f"""Agricultural Land at Risk:

Top Countries:
{newline.join(country_lines)}

Total countries: {len(country_details)}
Data source: {data_source}"""

    @app.callback(
        Output('kpi-severe-risk-percent-card', 'title'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_severe_risk_percent_hover(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        if d.empty:
            return "No data available"
        
        d_filtered = d[d['erosion_risk_level'] != 'Total']
        severe_data = d_filtered[d_filtered['erosion_risk_level'] == 'Severe']
        
        if severe_data.empty:
            return f"No severe risk areas in selection\nTotal observations: {len(d_filtered)}"
        
        severe_by_country = severe_data['country'].value_counts()
        
        # Build strings with consistent formatting
        newline = '\n'
        country_lines = []
        for country, count in severe_by_country.head(8).items():
            country_lines.append(f"• {country}: {count} observations")
        
        return f"""Severe Risk Analysis:

{len(severe_data)} severe out of {len(d_filtered)} total
({len(severe_data)/len(d_filtered)*100:.1f}%)

Countries with severe risk:
{newline.join(country_lines)}"""

    @app.callback(
        Output('kpi-high-risk-countries-card', 'title'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_high_risk_countries_hover(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        high_risk_indicators = ['High', 'Severe']
        high_risk_data = d[d['erosion_risk_level'].isin(high_risk_indicators)]
        
        if high_risk_data.empty:
            return "No high-risk countries found"
        
        # Get the complete list of high-risk countries with details
        country_details = high_risk_data.groupby('country').agg({
            'erosion_risk_level': lambda x: ', '.join(sorted(x.unique())),
            'obs_value': 'mean'
        }).round(1).sort_values('obs_value', ascending=False)
        
        total_countries = len(country_details)
        high_only = len(high_risk_data[high_risk_data['erosion_risk_level'] == 'High']['country'].unique())
        severe_count = len(high_risk_data[high_risk_data['erosion_risk_level'] == 'Severe']['country'].unique())
        
        # Build strings with consistent formatting
        newline = '\n'
        country_lines = []
        for country, row in country_details.iterrows():
            country_lines.append(f"• {country}: {row['obs_value']:.1f}% ({row['erosion_risk_level']})")
        
        return f"""High-Risk Countries ({total_countries} total):

Complete List:
{newline.join(country_lines)}

Summary: {severe_count} severe, {high_only} high-only"""

    # Visualization 1: Erosion Risk Evolution Over Time
    @app.callback(
        Output('erosion-temporal-evolution', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_erosion_temporal_evolution(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
        if d.empty:
            fig = go.Figure()
            fig.add_annotation(text="No data available for selected filters", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(title=style_title('No Data Available'), 
                            paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR)
            return fig
        
        # Create temporal analysis
        temporal_data = d.groupby(['year', 'measure_category']).agg({
            'obs_value': ['sum', 'count', 'mean', 'std']
        }).reset_index()
        
        temporal_data.columns = ['year', 'measure_category', 'total_erosion', 'observation_count', 'avg_intensity', 'volatility']
        temporal_data['volatility'] = temporal_data['volatility'].fillna(0)
        
        # Create subplot with stacked area and volatility
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Cumulative Erosion Impact by Type', 'Observation Volatility'),
            vertical_spacing=0.15,
            row_heights=[0.7, 0.3]
        )
        
        # Define color palette
        colors = {
            'Water erosion': '#1f77b4',
            'Wind erosion': '#ff7f0e', 
            'Tillage erosion': '#2ca02c',
            'Other erosion': '#d62728'
        }
        
        # Top panel: Stacked area chart
        erosion_types = temporal_data['measure_category'].unique()
        
        for erosion_type in erosion_types:
            type_data = temporal_data[temporal_data['measure_category'] == erosion_type]
            yearly_total = type_data.groupby('year')['total_erosion'].sum().reset_index()
            
            fig.add_trace(
                go.Scatter(
                    x=yearly_total['year'],
                    y=yearly_total['total_erosion'],
                    mode='lines',
                    name=erosion_type,
                    stackgroup='one',
                    fillcolor=colors.get(erosion_type, '#999999'),
                    line=dict(color=colors.get(erosion_type, '#999999'), width=0.5),
                    hovertemplate='%{y:.0f}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Bottom panel: Volatility indicator
        yearly_volatility = temporal_data.groupby('year')['volatility'].mean().reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=yearly_volatility['year'],
                y=yearly_volatility['volatility'],
                mode='lines+markers',
                name='Risk Volatility',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8, color='#e74c3c'),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.3)',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='Erosion Risk Evolution: Temporal Trends and Volatility',
                x=0.5,  # Center the title
                xanchor='center',
                font=dict(size=18, color=TEXT_COLOR, family=FONT_FAMILY)
            ),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=60, r=60, t=100, b=60),
            height=600,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Update axes
        fig.update_xaxes(title_text="", showgrid=False, row=1, col=1)
        fig.update_xaxes(title_text="Year", showgrid=False, row=2, col=1)
        fig.update_yaxes(title_text="Total Erosion Impact", showgrid=True, gridcolor='rgba(255,255,255,0.1)', row=1, col=1)
        fig.update_yaxes(title_text="Volatility", showgrid=True, gridcolor='rgba(255,255,255,0.1)', row=2, col=1)
        
        return fig

    #Visualization 2: Geographic Risk Distribution Matrix (NORMALIZED)
    @app.callback(
        Output('erosion-geographic-matrix', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_erosion_geographic_matrix_normalized(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
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
        
        # Prepare data for visualization
        geo_data = d.groupby(['country', 'measure_category', 'continent']).agg({
            'obs_value': ['mean', 'count', 'max']
        }).reset_index()
        
        geo_data.columns = ['country', 'measure_category', 'continent', 'avg_intensity', 'observation_count', 'max_intensity']
        
        # APPLY NORMALIZATION BY AGRICULTURAL LAND
        normalized_geo = normalize_by_agricultural_land(geo_data, df, 'avg_intensity')
        
        # Filter only countries with valid agricultural land data (where normalization occurred)
        valid_geo_data = normalized_geo[
            normalized_geo['avg_intensity_log_normalized'] != normalized_geo['avg_intensity']
        ].copy()
        
        if valid_geo_data.empty:
            fig = go.Figure()
            fig.add_annotation(text="No countries with agricultural land data available", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(title=style_title('No Agricultural Land Data Available'), 
                            paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR)
            return fig
        
        # Create subplot with 2 visualizations
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Top 10 Countries: Normalized Erosion Intensity', 'Continental Risk Analysis (Normalized)'),
            specs=[[{"type": "heatmap"}, {"type": "scatter"}]],
            horizontal_spacing=0.20,
            column_widths=[0.50, 0.50]
        )
        
        # Left panel: Clean heatmap with top 10 normalized countries
        top_countries = valid_geo_data.groupby('country')['avg_intensity_log_normalized'].mean().nlargest(10).index
        heatmap_data = valid_geo_data[valid_geo_data['country'].isin(top_countries)]
        
        # Pivot for heatmap using normalized values
        heatmap_matrix = heatmap_data.pivot_table(
            index='country', 
            columns='measure_category', 
            values='avg_intensity_log_normalized', 
            fill_value=0
        )
        
        # Sort countries by total normalized intensity
        heatmap_matrix['total'] = heatmap_matrix.sum(axis=1)
        heatmap_matrix = heatmap_matrix.sort_values('total', ascending=False).drop('total', axis=1)
        
        fig.add_trace(
            go.Heatmap(
                z=heatmap_matrix.values,
                x=[col.replace(' erosion', '') for col in heatmap_matrix.columns],
                y=heatmap_matrix.index.tolist(),
                colorscale='YlOrRd',
                showscale=True,
                colorbar=dict(
                    title="Intensity", 
                    x=0.41,
                    y=0.5,
                    len=0.85
                ),
                hovertemplate='Country: %{y}<br>Type: %{x}<br>Norm. Intensity: %{z:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Right panel: Continental bubble chart with normalized data
        continent_summary = valid_geo_data.groupby('continent').agg({
            'avg_intensity_log_normalized': 'mean',
            'observation_count': 'sum',
            'country': 'nunique'
        }).reset_index()
        
        # Calculate risk score for bubble size using normalized values
        continent_summary['risk_score'] = (continent_summary['avg_intensity_log_normalized'] * 100)
        
        continent_colors = {
            'Asia': '#FF6B6B', 'Europe': '#4ECDC4', 'Africa': '#45B7D1',
            'North America': '#96CEB4', 'South America': '#FECA57', 'Oceania': '#FF8C69'
        }
        
        fig.add_trace(
            go.Scatter(
                x=continent_summary['observation_count'],
                y=continent_summary['avg_intensity_log_normalized'],
                mode='markers+text',
                marker=dict(
                    size=continent_summary['risk_score'],
                    color=[continent_colors.get(c, '#999999') for c in continent_summary['continent']],
                    opacity=0.7,
                    line=dict(width=2, color='white'),
                    sizemode='area',
                    sizeref=2.*max(continent_summary['risk_score'])/(40.**2),
                    sizemin=20
                ),
                text=continent_summary['continent'],
                textposition='middle center',
                textfont=dict(size=12, color='white', family=FONT_FAMILY),
                hovertemplate='<b>%{text}</b><br>Observations: %{x:,.0f}<br>Norm. Intensity: %{y:.2f}<br>Countries: %{customdata}<extra></extra>',
                customdata=continent_summary['country'],
                showlegend=False
            ),
            row=1, col=2
        )
        
        # Update layout
        fig.update_layout(
            title=dict(
                text='Normalized Geographic Erosion Risk Distribution (per Agricultural Hectare)',
                x=0.5,  # Center the title
                xanchor='center',
                font=dict(size=16, color=TEXT_COLOR, family=FONT_FAMILY)
            ),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=80, r=80, t=100, b=70),
            height=550,
            showlegend=False
        )
        
        # Update axes
        fig.update_xaxes(title_text="Erosion Type", tickangle=0, row=1, col=1)
        fig.update_yaxes(title_text="", row=1, col=1)
        fig.update_xaxes(
            title_text="Total Observations", 
            type="log",
            tickmode='linear',
            dtick=1,
            range=[0.5, 3.5],
            row=1, col=2
        )
        fig.update_yaxes(
            title_text="Normalized Intensity",
            row=1, col=2
        )
        
        # Style all subplots with consistent grid
        fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        
        # Add normalization explanation
        fig.add_annotation(
            text="Intensity normalized by agricultural land area (log scale). Higher values = more erosion per hectare.",
            xref="paper", yref="paper",
            x=0.5, y=-0.15,
            xanchor='center', yanchor='top',
            showarrow=False,
            font=dict(size=10, color=TEXT_COLOR),
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        )
        
        return fig


    # Visualization 3: Risk Pattern Analysis
    @app.callback(
        Output('erosion-risk-patterns', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('erosion-risk-dropdown', 'value'),
        Input('erosion-type-dropdown', 'value')
    )
    def update_erosion_risk_patterns(countries, years, erosion_levels, erosion_types):
        erosion_measures = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
        d = apply_filters(erosion_measures, selected_countries=countries, year_range=years, 
                         selected_erosion_levels=erosion_levels)
        
        # Apply erosion type filter
        if erosion_types and 'All' not in erosion_types:
            d = d[d['measure_category'].isin(erosion_types)]
        
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
        
        # Risk Distribution Matrix
        fig = go.Figure()
        
        # FILTER OUT "Total" risk level
        d_filtered = d[d['erosion_risk_level'].str.lower() != 'total']
        
        # Prepare data
        risk_summary = d_filtered.groupby(['erosion_risk_level', 'measure_category']).agg({
            'obs_value': ['mean', 'count', 'std']
        }).reset_index()
        
        risk_summary.columns = ['erosion_risk_level', 'measure_category', 'avg_intensity', 'count', 'std']
        
        # Define risk level order (excluding "Total")
        risk_order = ['Low', 'Moderate', 'Tolerable', 'High', 'Severe']
        risk_summary['risk_rank'] = risk_summary['erosion_risk_level'].map(
            {level: i for i, level in enumerate(risk_order)}
        )
        risk_summary = risk_summary.sort_values('risk_rank')
        
        # Create bubble matrix
        erosion_types = risk_summary['measure_category'].unique()
        risk_levels = [r for r in risk_order if r in risk_summary['erosion_risk_level'].unique()]
        
        # Updated color scale for your specific risk levels
        color_scale = {
            'Low': '#BADD7F', 
            'Moderate': '#fff394', 
            'Tolerable': '#a2d2ff',
            'High': '#ec8366',
            'Severe': '#f00000'
        }
        
        for erosion_type in erosion_types:
            type_data = risk_summary[risk_summary['measure_category'] == erosion_type]
            
            # Calculate bubble sizes based on observation count
            max_count = risk_summary['count'].max()
            bubble_sizes = (type_data['count'] / max_count * 100).fillna(0)
            
            fig.add_trace(
                go.Scatter(
                    x=[erosion_type.replace(' erosion', '')] * len(type_data),
                    y=type_data['erosion_risk_level'],
                    mode='markers+text',
                    marker=dict(
                        size=bubble_sizes,
                        color=[color_scale.get(r, "#C8C0C0") for r in type_data['erosion_risk_level']],
                        opacity=0.8,
                        line=dict(width=2, color='white'),
                        sizemode='diameter',
                        sizeref=2,
                        sizemin=10
                    ),
                    text=type_data['count'].astype(str),
                    textfont=dict(size=10, color='white', family=FONT_FAMILY),
                    textposition='middle center',
                    hovertemplate='<b>%{x} - %{y}</b><br>Observations: %{text}<br>Avg Intensity: %{customdata:.1f}<extra></extra>',
                    customdata=type_data['avg_intensity'],
                    showlegend=False
                )
            )
        
        # Add intensity gradient background
        for i, risk_level in enumerate(risk_levels):
            fig.add_shape(
                type="rect",
                xref="paper", yref="y",
                x0=0, x1=1,
                y0=i-0.4, y1=i+0.4,
                fillcolor=color_scale.get(risk_level, "#E4E2E2"),
                opacity=0.2,
                layer="below",
                line_width=0
            )
        
        # Update layout for single clean visualization
        fig.update_layout(
            title=dict(
                text='Erosion Risk Pattern Matrix: Distribution by Type and Severity',
                x=0.5,  # Center the title
                xanchor='center',
                font=dict(size=18, color=TEXT_COLOR, family=FONT_FAMILY)
            ),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=120, r=80, t=100, b=120),
            height=600,
            xaxis=dict(
                title="Erosion Type",
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                tickangle=0
            ),
            yaxis=dict(
                title="Risk Level",
                showgrid=False,
                categoryorder='array',
                categoryarray=risk_levels
            ),
            showlegend=False
        )
        
        # Add annotations for clarity with adjusted positions
        fig.add_annotation(
            text="Bubble size = Number of observations",
            xref="paper", yref="paper",
            x=0.5, y=-0.20,
            showarrow=False,
            font=dict(size=12, color=TEXT_COLOR)
        )
        
        fig.add_annotation(
            text="Color intensity = Risk severity",
            xref="paper", yref="paper",
            x=0.5, y=-0.25,
            showarrow=False,
            font=dict(size=12, color=TEXT_COLOR)
        )
        
        return fig