from dash import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from ..styles import VIZ_COLOR, TEXT_COLOR

def filter_water_data(df, countries, years, water_types, contamination_types):
    """Filter the dataset based on user selections"""
    # Filter for water-related measures
    water_measures = [
        'Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for nitrate',
        'Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for phosphorus', 
        'Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for pesticides',
        'Share of monitoring sites in agricultural areas where one or more pesticides are present',
        'Agriculture freshwater abstraction',
        'Total freshwater abstraction'
    ]
    
    filtered_df = df[df['measure_category'].isin(water_measures)].copy()
    
    # Apply filters
    if countries and 'All' not in countries:
        filtered_df = filtered_df[filtered_df['country'].isin(countries)]
    
    if years:
        filtered_df = filtered_df[
            (filtered_df['year'] >= years[0]) & 
            (filtered_df['year'] <= years[1])
        ]
    
    if water_types and 'All' not in water_types:
        filtered_df = filtered_df[filtered_df['water_type'].isin(water_types)]
    
    # Filter by contamination type
    if contamination_types and 'All' not in contamination_types:
        contamination_filter = []
        if 'Nitrate' in contamination_types:
            contamination_filter.append('Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for nitrate')
        if 'Phosphorus' in contamination_types:
            contamination_filter.append('Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for phosphorus')
        if 'Pesticides' in contamination_types:
            contamination_filter.append('Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for pesticides')
        if 'Pesticide_Presence' in contamination_types:
            contamination_filter.append('Share of monitoring sites in agricultural areas where one or more pesticides are present')
        
        if contamination_filter:
            contamination_data = filtered_df[filtered_df['measure_category'].isin(contamination_filter)]
            abstraction_data = filtered_df[filtered_df['measure_category'].str.contains('abstraction')]
            filtered_df = pd.concat([contamination_data, abstraction_data])
    
    return filtered_df

def get_water_callbacks(df, app):
    
    @app.callback(
        [Output('kpi-high-contamination-countries', 'children'),
         Output('kpi-avg-contamination-rate', 'children'),
         Output('kpi-total-water-abstraction', 'children'),
         Output('kpi-worst-contamination-type', 'children')],
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_kpis(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            # KPI 1: High Risk Countries (>30% contamination)
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', na=False)
            ]
            if not contamination_data.empty:
                country_avg = contamination_data.groupby('country')['obs_value'].mean()
                high_risk_countries = (country_avg > 30).sum()
            else:
                high_risk_countries = 0
            
            # KPI 2: Average Contamination Rate
            if not contamination_data.empty:
                avg_contamination = contamination_data['obs_value'].mean()
                kpi2_value = f"{avg_contamination:.1f}%"
            else:
                kpi2_value = "0%"
            
            # KPI 3: Total Agricultural Water Use (latest year)
            abstraction_data = filtered_df[
                filtered_df['measure_category'] == 'Agriculture freshwater abstraction'
            ]
            if not abstraction_data.empty:
                latest_year = abstraction_data['year'].max()
                latest_data = abstraction_data[abstraction_data['year'] == latest_year]
                total_abstraction = latest_data['obs_value'].sum()
                if total_abstraction >= 1000000:
                    kpi3_value = f"{total_abstraction/1000000:.1f}M"
                elif total_abstraction >= 1000:
                    kpi3_value = f"{total_abstraction/1000:.1f}K"
                else:
                    kpi3_value = f"{total_abstraction:.0f}"
            else:
                kpi3_value = "0"
            
            # KPI 4: Worst Contamination Type
            if not contamination_data.empty:
                contamination_by_type = contamination_data.groupby('measure_category')['obs_value'].mean()
                worst_type = contamination_by_type.idxmax()
                if 'nitrate' in worst_type.lower():
                    kpi4_value = "Nitrate"
                elif 'phosphorus' in worst_type.lower():
                    kpi4_value = "Phosphorus"
                elif 'pesticide' in worst_type.lower():
                    kpi4_value = "Pesticides"
                else:
                    kpi4_value = "Unknown"
            else:
                kpi4_value = "N/A"
            
            return (str(high_risk_countries), kpi2_value, kpi3_value, kpi4_value)
            
        except Exception as e:
            return ("0", "0%", "0", "N/A")

    # HOVER DETAIL CALLBACKS FOR KPI CARDS
    @app.callback(
        Output('kpi-high-contamination-countries-card', 'title'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_high_risk_countries_hover(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', na=False)
            ]
            
            if contamination_data.empty:
                return "No contamination data available for selected filters"
            
            # Get country averages and identify high-risk countries
            country_avg = contamination_data.groupby('country')['obs_value'].mean().sort_values(ascending=False)
            high_risk_countries = country_avg[country_avg > 30]
            total_countries = len(country_avg)
            
            # Get breakdown by contamination type
            type_breakdown = contamination_data.groupby('measure_category')['country'].nunique()
            year_range = f"{contamination_data['year'].min()}-{contamination_data['year'].max()}" if contamination_data['year'].nunique() > 1 else str(contamination_data['year'].iloc[0])
            
            # Build strings with consistent formatting
            newline = '\n'
            country_lines = []
            for country, rate in high_risk_countries.head(8).items():
                country_lines.append(f"• {country}: {rate:.1f}% contamination")
            
            type_lines = []
            for measure_type, count in type_breakdown.items():
                simplified_type = measure_type.split('for ')[-1].replace('nitrate', 'Nitrate').replace('phosphorus', 'Phosphorus').replace('pesticides', 'Pesticides')
                type_lines.append(f"• {simplified_type}: {count} countries monitored")
            
            return f"""High-Risk Countries (>30% contamination): {len(high_risk_countries)} out of {total_countries}

Countries with Highest Risk:
{newline.join(country_lines)}

Monitoring Coverage by Type:
{newline.join(type_lines)}

Data Period: {year_range}
Threshold: >30% of monitoring sites exceed drinking water limits"""
            
        except Exception as e:
            return "Error loading high-risk countries data"

    @app.callback(
        Output('kpi-avg-contamination-rate-card', 'title'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_avg_contamination_hover(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', na=False)
            ]
            
            if contamination_data.empty:
                return "No contamination data available"
            
            # Calculate detailed statistics
            overall_avg = contamination_data['obs_value'].mean()
            by_type = contamination_data.groupby('measure_category')['obs_value'].agg(['mean', 'count']).round(1)
            by_water_type = contamination_data.groupby('water_type')['obs_value'].agg(['mean', 'count']).round(1)
            
            # Build strings with consistent formatting
            newline = '\n'
            type_lines = []
            for measure_type, stats in by_type.iterrows():
                simplified_type = measure_type.split('for ')[-1].replace('nitrate', 'Nitrate').replace('phosphorus', 'Phosphorus').replace('pesticides', 'Pesticides')
                type_lines.append(f"• {simplified_type}: {stats['mean']:.1f}% ({int(stats['count'])} sites)")
            
            water_lines = []
            for water_type, stats in by_water_type.iterrows():
                if water_type != 'Not applicable':
                    water_lines.append(f"• {water_type}: {stats['mean']:.1f}% ({int(stats['count'])} sites)")
            
            return f"""Average Contamination Rate: {overall_avg:.1f}%

By Contamination Type:
{newline.join(type_lines)}

By Water Source:
{newline.join(water_lines)}

Total Monitoring Sites: {len(contamination_data)}
Countries Monitored: {contamination_data['country'].nunique()}"""
            
        except Exception as e:
            return "Error loading contamination rate data"

    @app.callback(
        Output('kpi-total-water-abstraction-card', 'title'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_water_abstraction_hover(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            abstraction_data = filtered_df[
                filtered_df['measure_category'] == 'Agriculture freshwater abstraction'
            ]
            
            if abstraction_data.empty:
                return "No water abstraction data available"
            
            # Get latest year statistics
            latest_year = abstraction_data['year'].max()
            latest_data = abstraction_data[abstraction_data['year'] == latest_year]
            total_abstraction = latest_data['obs_value'].sum()
            
            # Get breakdown by water type and country
            by_water_type = latest_data.groupby('water_type')['obs_value'].sum().sort_values(ascending=False)
            top_countries = latest_data.groupby('country')['obs_value'].sum().sort_values(ascending=False).head(5)
            
            # Calculate trend if multiple years available
            if len(abstraction_data['year'].unique()) > 1:
                yearly_totals = abstraction_data.groupby('year')['obs_value'].sum()
                if len(yearly_totals) >= 2:
                    recent_years = yearly_totals.tail(2)
                    change = ((recent_years.iloc[-1] - recent_years.iloc[-2]) / recent_years.iloc[-2] * 100)
                    trend_text = f"Trend: {change:+.1f}% from previous year"
                else:
                    trend_text = "Trend: Insufficient data"
            else:
                trend_text = "Trend: Single year data"
            
            # Build strings with consistent formatting
            newline = '\n'
            water_type_lines = []
            for water_type, volume in by_water_type.items():
                if water_type != 'Not applicable':
                    water_type_lines.append(f"• {water_type}: {volume:,.0f} cubic metres")
            
            country_lines = []
            for country, volume in top_countries.items():
                country_lines.append(f"• {country}: {volume:,.0f} cubic metres")
            
            return f"""Total Agricultural Water Abstraction ({latest_year}): {total_abstraction:,.0f} cubic metres

By Water Source:
{newline.join(water_type_lines)}

Top 5 Countries:
{newline.join(country_lines)}

{trend_text}
Countries Reporting: {latest_data['country'].nunique()}"""
            
        except Exception as e:
            return "Error loading water abstraction data"

    @app.callback(
        Output('kpi-worst-contamination-type-card', 'title'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_worst_contamination_hover(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', na=False)
            ]
            
            if contamination_data.empty:
                return "No contamination data available"
            
            # Get contamination by type with detailed statistics
            contamination_by_type = contamination_data.groupby('measure_category').agg({
                'obs_value': ['mean', 'max', 'count'],
                'country': 'nunique'
            }).round(1)
            
            contamination_by_type.columns = ['avg_rate', 'max_rate', 'observations', 'countries']
            contamination_by_type = contamination_by_type.sort_values('avg_rate', ascending=False)
            
            # Get the worst type
            worst_type = contamination_by_type.index[0]
            worst_stats = contamination_by_type.iloc[0]
            
            # Simplify type names
            def simplify_name(name):
                if 'nitrate' in name.lower():
                    return 'Nitrate'
                elif 'phosphorus' in name.lower():
                    return 'Phosphorus'
                elif 'pesticide' in name.lower():
                    return 'Pesticides'
                else:
                    return 'Unknown'
            
            worst_simple = simplify_name(worst_type)
            
            # Build ranking list
            newline = '\n'
            ranking_lines = []
            for i, (measure_type, stats) in enumerate(contamination_by_type.iterrows(), 1):
                simple_name = simplify_name(measure_type)
                ranking_lines.append(f"{i}. {simple_name}: {stats['avg_rate']:.1f}% avg ({int(stats['observations'])} sites)")
            
            # Get countries most affected by worst type
            worst_type_data = contamination_data[contamination_data['measure_category'] == worst_type]
            worst_countries = worst_type_data.groupby('country')['obs_value'].mean().sort_values(ascending=False).head(3)
            
            country_lines = []
            for country, rate in worst_countries.items():
                country_lines.append(f"• {country}: {rate:.1f}%")
            
            return f"""Worst Pollutant: {worst_simple} ({worst_stats['avg_rate']:.1f}% average contamination)

Contamination Ranking:
{newline.join(ranking_lines)}

Most Affected Countries ({worst_simple}):
{newline.join(country_lines)}

Max Rate Recorded: {worst_stats['max_rate']:.1f}%
Countries Monitored: {int(worst_stats['countries'])}"""
            
        except Exception as e:
            return "Error loading worst contamination type data"
    
    # Visualization 1: Geographic Water Contamination
    @app.callback(
        Output('water-contamination-geographic', 'figure'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_contamination_geographic(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            # Filter for contamination data only
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', na=False) |
                filtered_df['measure_category'].str.contains('pesticides are present', na=False)
            ]
            
            if contamination_data.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No contamination data available for selected filters",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16, color=TEXT_COLOR)
                )
                fig.update_layout(
                    title=dict(
                        text='Geographic Water Contamination Analysis',
                        x=0.5, xanchor='center',
                        font=dict(size=18, color=TEXT_COLOR)
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=TEXT_COLOR),
                    height=600
                )
                return fig
            
            # Calculate average contamination by country
            country_contamination = contamination_data.groupby('country')['obs_value'].mean().reset_index()
            country_contamination.columns = ['country', 'avg_contamination']
            country_contamination = country_contamination.sort_values('avg_contamination', ascending=False)
            
            # Create single bar chart showing top countries
            top_countries = country_contamination.head(20)  # Show top 20
            
            fig = go.Figure()
            
            fig.add_trace(
                go.Bar(
                    y=top_countries['country'][::-1],  # Reverse for better readability
                    x=top_countries['avg_contamination'][::-1],
                    orientation='h',
                    marker=dict(
                        color=top_countries['avg_contamination'][::-1],
                        colorscale='Reds',
                        colorbar=dict(title="Contamination Rate (%)")
                    ),
                    hovertemplate='<b>%{y}</b><br>Contamination: %{x:.1f}%<extra></extra>'
                )
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text='Geographic Water Contamination Analysis',
                    x=0.5, xanchor='center',
                    font=dict(size=18, color=TEXT_COLOR)
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_COLOR),
                height=600,
                showlegend=False,
                xaxis_title="Average Contamination Rate (%)",
                yaxis_title="Countries",
                margin=dict(l=150, r=50, t=80, b=50)
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text="Error loading geographic data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color=TEXT_COLOR)
            )
            fig.update_layout(
                title=dict(
                    text='Geographic Water Contamination Analysis',
                    x=0.5, xanchor='center',
                    font=dict(size=18, color=TEXT_COLOR)
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_COLOR),
                height=600
            )
            return fig
    
    # Visualization 2: Water Usage vs Contamination
    @app.callback(
        Output('water-trends-dual-axis', 'figure'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_trends_dual_axis(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            # Create dual-axis subplot
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Get contamination trends (left axis)
            contamination_measures = [
                'Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for nitrate',
                'Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for phosphorus',
                'Share of monitoring sites in agricultural areas that exceed recommended drinking water limits for pesticides'
            ]
            
            colors = ['#FF6B6B', '#D1AEFC', '#FBDA91']
            labels = ['Nitrate', 'Phosphorus', 'Pesticides']
            
            for i, measure in enumerate(contamination_measures):
                measure_data = filtered_df[filtered_df['measure_category'] == measure]
                if not measure_data.empty:
                    yearly_avg = measure_data.groupby('year')['obs_value'].mean().reset_index()
                    
                    fig.add_trace(
                        go.Scatter(
                            x=yearly_avg['year'],
                            y=yearly_avg['obs_value'],
                            mode='lines+markers',
                            name=labels[i],
                            line=dict(color=colors[i], width=3),
                            marker=dict(size=6)
                        ),
                        secondary_y=False
                    )
            
            # Get abstraction data (right axis)
            abstraction_data = filtered_df[filtered_df['measure_category'] == 'Agriculture freshwater abstraction']
            if not abstraction_data.empty:
                yearly_abstraction = abstraction_data.groupby('year')['obs_value'].sum().reset_index()
                
                fig.add_trace(
                    go.Bar(
                        x=yearly_abstraction['year'],
                        y=yearly_abstraction['obs_value'],
                        name='Water Abstraction',
                        opacity=0.6,
                        marker_color='#96CEB4'
                    ),
                    secondary_y=True
                )
            
            # Update layout
            fig.update_xaxes(title_text="Year")
            fig.update_yaxes(title_text="Contamination Rate (%)", secondary_y=False)
            fig.update_yaxes(title_text="Water Abstraction (cubic metres)", secondary_y=True)
            
            fig.update_layout(
                title=dict(
                    text='Water Quality Degradation Trends vs Agricultural Water Consumption',
                    x=0.5, xanchor='center',
                    font=dict(size=18, color=TEXT_COLOR)
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_COLOR),
                legend=dict(
                    bgcolor='rgba(255,255,255)',
                    bordercolor=TEXT_COLOR,
                    borderwidth=1
                ),
                hovermode='x unified',
                height=500,
                hoverlabel=dict(
                    bgcolor="white",
                    font_color="black",
                    font_size=12,
                    bordercolor=TEXT_COLOR
                )
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text="Error loading trends data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color=TEXT_COLOR)
            )
            fig.update_layout(
                title=dict(
                    text='Water Quality Degradation Trends vs Agricultural Water Consumption',
                    x=0.5, xanchor='center',
                    font=dict(size=18, color=TEXT_COLOR)
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_COLOR),
                height=500
            )
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text="Error loading trends data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color=TEXT_COLOR)
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_COLOR),
                height=500
            )
            return fig
    
    # Visualization 3: Water Quality vs Usage Efficiency Analysis
    @app.callback(
        Output('water-quality-usage-analysis', 'figure'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_quality_usage_analysis(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            if filtered_df.empty:
                fig = go.Figure()
                fig.add_annotation(
                    text="No data available for selected filters",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16, color=TEXT_COLOR)
                )
                fig.update_layout(
                    title=dict(
                        text='Water Quality vs Usage Efficiency Analysis',
                        x=0.5, xanchor='center',
                        font=dict(size=18, color=TEXT_COLOR)
                    ),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=TEXT_COLOR),
                    height=550
                )
                return fig
            
            # Create subplots: Side-by-side bar chart + pie chart
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Top 10 Countries: Water Usage vs Contamination', 'Water Source Distribution'),
                specs=[[{"type": "bar"}, {"type": "pie"}]],
                column_widths=[0.6, 0.4],  # More space for bar chart
                horizontal_spacing=0.15 # Good spacing between chart
            )
            
            # Get contamination data
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', na=False) |
                filtered_df['measure_category'].str.contains('pesticides are present', na=False)
            ]
            
            # Get water abstraction data  
            abstraction_data = filtered_df[
                filtered_df['measure_category'] == 'Agriculture freshwater abstraction'
            ]
            
            # Top panel: Combined bar chart showing usage and contamination
            if not contamination_data.empty and not abstraction_data.empty:
                # Calculate country averages
                country_contamination = contamination_data.groupby('country')['obs_value'].mean().reset_index()
                country_contamination.columns = ['country', 'contamination_rate']
                
                country_abstraction = abstraction_data.groupby('country')['obs_value'].mean().reset_index()
                country_abstraction.columns = ['country', 'water_usage']
                
                # Merge data
                correlation_data = country_contamination.merge(country_abstraction, on='country', how='inner')
                
                if not correlation_data.empty:
                    # Sort by contamination rate and take top 10
                    top_countries = correlation_data.nlargest(10, 'contamination_rate')
                    
                    # Normalize water usage for better visualization (scale to 0-100)
                    max_usage = top_countries['water_usage'].max()
                    top_countries['usage_normalized'] = (top_countries['water_usage'] / max_usage) * 100
                    
                    # Add contamination rate bars
                    fig.add_trace(
                        go.Bar(
                            x=top_countries['country'],
                            y=top_countries['contamination_rate'],
                            name='Contamination Rate (%)',
                            marker_color='#c44d4d',
                            opacity=0.8,
                            hovertemplate='<b>%{x}</b><br>Contamination: %{y:.1f}%<extra></extra>',
                            showlegend=True
                        ),
                        row=1, col=1
                    )
                    
                    # Add normalized water usage bars
                    fig.add_trace(
                        go.Bar(
                            x=top_countries['country'],
                            y=top_countries['usage_normalized'],
                            name='Water Usage (Normalized)',
                            marker_color='#a2d2ff',
                            opacity=0.6,
                            hovertemplate='<b>%{x}</b><br>Water Usage: %{customdata:,.0f} cubic metres<extra></extra>',
                            customdata=top_countries['water_usage'],
                            showlegend=True
                        ),
                        row=1, col=1
                    )
                else:
                    fig.add_annotation(
                        text="No correlation data available",
                        xref="paper", yref="paper",
                        x=0.3, y=0.5, xanchor='center', yanchor='middle',
                        showarrow=False, font=dict(size=14, color=TEXT_COLOR)
                    )
            else:
                fig.add_annotation(
                    text="Insufficient data for analysis",
                    xref="paper", yref="paper",
                    x=0.3, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=14, color=TEXT_COLOR)
                )
            
            # Right panel: Water source distribution pie chart
            water_source_data = abstraction_data[
                abstraction_data['water_type'].isin(['Surface water', 'Ground water'])
            ]
            
            if not water_source_data.empty:
                source_totals = water_source_data.groupby('water_type')['obs_value'].sum().reset_index()
                
                if len(source_totals) > 0:
                    fig.add_trace(
                        go.Pie(
                            labels=source_totals['water_type'],
                            values=source_totals['obs_value'],
                            hole=0.4,
                            marker=dict(colors=['#c6e6e3', '#f3a0ad']),
                            textinfo='label+percent',
                            hovertemplate='<b>%{label}</b><br>Volume: %{value:,.0f} cubic metres<br>Percentage: %{percent}<extra></extra>',
                            showlegend=False  # Hide pie legend to avoid overlap with bar legend
                        ),
                        row=1, col=2
                    )
                    
                    fig.update_traces(
                        selector=dict(type="pie"),
                        domain=dict(x=[0.6, 0.95], y=[0.03, 0.98])  # Position pie chart on right side
                    )
                    
                else:
                    fig.add_annotation(
                        text="No water source data",
                        xref="paper", yref="paper",
                        x=0.8, y=0.5, xanchor='center', yanchor='middle',
                        showarrow=False, font=dict(size=14, color=TEXT_COLOR)
                    )
            else:
                fig.add_annotation(
                    text="No water source breakdown available",
                    xref="paper", yref="paper",
                    x=0.8, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=14, color=TEXT_COLOR)
                )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text='Water Quality vs Usage Efficiency Analysis',
                    x=0.5, xanchor='center',
                    font=dict(size=18, color=TEXT_COLOR)
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_COLOR),
                height=500,  # Standard height for side-by-side
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.5,  # Place legend below the charts
                    xanchor="center",
                    x=0.25  # Position over the bar chart area
                ),
                margin=dict(t=120, b=80, l=50, r=50), # Extra bottom margin for legend
                annotations=[
                    dict(text="Top 10 Countries: Water Usage vs Contamination", 
                         xref="paper", yref="paper", x=0.25, y=1, xanchor="center", 
                         font=dict(size=16), showarrow=False),
                    dict(text="Water Source Distribution", 
                         xref="paper", yref="paper", x=0.78, y=1, xanchor="center", 
                         font=dict(size=16), showarrow=False)  # Lower the pie chart title more
                ]
            )
            
            # Update axes for bar chart
            fig.update_xaxes(title_text="Countries", tickangle=45, row=1, col=1)
            fig.update_yaxes(title_text="Rate / Normalized Usage", row=1, col=1)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error loading water quality analysis: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font=dict(size=16, color=TEXT_COLOR)
            )
            fig.update_layout(
                title=dict(
                    text='Water Quality vs Usage Efficiency Analysis',
                    x=0.5, xanchor='center',
                    font=dict(size=18, color=TEXT_COLOR)
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=TEXT_COLOR),
                height=600
            )
            return fig