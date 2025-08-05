from dash import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from ..styles import VIZ_COLOR, TEXT_COLOR
from ..helpers.tools import normalize_by_agricultural_land

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
    
    # Visualization 1: D3 data callback for high-risk countries
    @app.callback(
        Output('high-risk-countries-data', 'data'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('water-type-dropdown', 'value'),
         Input('contamination-type-dropdown', 'value')]
    )
    def update_high_risk_countries_d3_data_normalized(countries, years, water_types, contamination_types):
        try:
            filtered_df = filter_water_data(df, countries, years, water_types, contamination_types)
            
            # Get contamination data only
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', case=False, na=False) |
                filtered_df['measure_category'].str.contains('pesticides are present', case=False, na=False)
            ]
            
            if contamination_data.empty:
                return []
            
            # Calculate country-level statistics
            country_stats = contamination_data.groupby('country').agg({
                'obs_value': ['mean', 'count', 'max'],
                'measure_category': lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'
            }).reset_index()
            
            country_stats.columns = ['country', 'contamination_rate', 'monitoring_sites', 'max_contamination', 'main_pollutant']
            
            # Apply logarithmic normalization
            normalized_stats = normalize_by_agricultural_land(
                country_stats, df, 'contamination_rate'
            )
            
            # Filter for countries with agricultural land data and meaningful contamination
            high_risk_countries = normalized_stats[
                (normalized_stats['contamination_rate_log_normalized'] != normalized_stats['contamination_rate']) &
                (normalized_stats['contamination_rate_log_normalized'] > 0.1)  # Adjusted threshold for log values
            ].copy()
            
            # Clean up pollutant names
            def clean_pollutant_name(measure_category):
                if pd.isna(measure_category):
                    return 'Unknown'
                if 'nitrate' in str(measure_category).lower():
                    return 'Nitrate'
                elif 'phosphorus' in str(measure_category).lower():
                    return 'Phosphorus'
                elif 'pesticide' in str(measure_category).lower():
                    return 'Pesticides'
                else:
                    return 'Mixed'
            
            high_risk_countries['main_pollutant'] = high_risk_countries['main_pollutant'].apply(clean_pollutant_name)
            
            # Convert to list of dictionaries for D3
            d3_data = []
            for _, row in high_risk_countries.iterrows():
                d3_data.append({
                    'country': str(row['country']),
                    'contamination_rate': float(row['contamination_rate']),  # Raw for display
                    'contamination_rate_normalized': float(row['contamination_rate_log_normalized']),  # Log normalized for sorting
                    'monitoring_sites': int(row['monitoring_sites']),
                    'max_contamination': float(row['max_contamination']),
                    'main_pollutant': str(row['main_pollutant'])
                })
            
            # Sort by normalized contamination rate
            d3_data = sorted(d3_data, key=lambda x: x['contamination_rate_normalized'], reverse=True)
            
            return d3_data
            
        except Exception as e:
            return []

    # Clean D3 visualization callback - removed all console.log statements
    app.clientside_callback(
        f"""
        function(data) {{
            // Function to load D3 dynamically if not available
            function loadD3() {{
                return new Promise((resolve, reject) => {{
                    if (typeof d3 !== 'undefined') {{
                        resolve();
                        return;
                    }}
                    
                    const script = document.createElement('script');
                    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js';
                    script.onload = () => resolve();
                    script.onerror = () => reject(new Error('Failed to load D3'));
                    document.head.appendChild(script);
                }});
            }}
            
            // Function to create the visualization
            function createVisualization(data) {{
                const container = d3.select('#d3-high-risk-countries');
                if (container.empty()) {{
                    return;
                }}
                
                // Clear existing content
                container.selectAll('*').remove();
                
                if (!data || data.length === 0) {{
                    container.append('div')
                        .style('display', 'flex')
                        .style('justify-content', 'center')
                        .style('align-items', 'center')
                        .style('height', '100%')
                        .style('color', '{TEXT_COLOR}')
                        .style('font-size', '16px')
                        .style('font-family', 'Inter, sans-serif')
                        .text('No contamination data available for current filters');
                    return;
                }}
                
                // Set up dimensions
                const margin = {{top: 50, right: 70, bottom: 120, left: 90}};
                const containerRect = container.node().getBoundingClientRect();
                const width = Math.max(600, containerRect.width - margin.left - margin.right);
                const height = 350;
                
                // Create SVG
                const svg = container.append('svg')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom);
                
                const g = svg.append('g')
                    .attr('transform', `translate(${{margin.left}},${{margin.top}})`);
                
                // Sort and limit data
                const sortedData = data.sort((a, b) => b.contamination_rate - a.contamination_rate).slice(0, 20);
                
                // Set up scales
                const xScale = d3.scaleBand()
                    .domain(sortedData.map(d => d.country))
                    .range([0, width])
                    .padding(0.15);
                
                const yScale = d3.scaleLinear()
                    .domain([0, d3.max(sortedData, d => d.contamination_rate) * 1.1])
                    .range([height, 0]);
                
                // Color function
                const getColor = (rate) => {{
                    if (rate >= 50) return '#f94449';      // Severe - Red
                    if (rate >= 30) return '#fdac68';      // High - Orange  
                    if (rate >= 15) return '#fae588';      // Moderate - Yellow
                    return '#b9ffaf';                      // Low - Green
                }};
                
                // Remove any existing tooltips
                d3.selectAll('.d3-water-tooltip').remove();
                
                // Create tooltip
                const tooltip = d3.select('body')
                    .append('div')
                    .attr('class', 'd3-water-tooltip')
                    .style('position', 'absolute')
                    .style('visibility', 'hidden')
                    .style('background-color', 'rgba(0, 0, 0, 0.9)')
                    .style('color', 'white')
                    .style('padding', '12px')
                    .style('border-radius', '6px')
                    .style('font-size', '13px')
                    .style('font-family', 'Inter, sans-serif')
                    .style('box-shadow', '0 4px 8px rgba(0, 0, 0, 0.3)')
                    .style('z-index', '1000')
                    .style('pointer-events', 'none')
                    .style('max-width', '200px');
                
                // Create bars
                const bars = g.selectAll('.bar')
                    .data(sortedData)
                    .enter()
                    .append('rect')
                    .attr('class', 'bar')
                    .attr('x', d => xScale(d.country))
                    .attr('width', xScale.bandwidth())
                    .attr('y', height)
                    .attr('height', 0)
                    .attr('fill', d => getColor(d.contamination_rate))
                    .attr('stroke', 'rgba(255,255,255,0.2)')
                    .attr('stroke-width', 1)
                    .style('cursor', 'pointer');
                
                // Animate bars
                bars.transition()
                    .duration(1000)
                    .delay((d, i) => i * 30)
                    .attr('y', d => yScale(d.contamination_rate))
                    .attr('height', d => height - yScale(d.contamination_rate));
                
                // Add value labels
                const labels = g.selectAll('.label')
                    .data(sortedData)
                    .enter()
                    .append('text')
                    .attr('class', 'label')
                    .attr('x', d => xScale(d.country) + xScale.bandwidth() / 2)
                    .attr('y', d => yScale(d.contamination_rate) - 8)
                    .attr('text-anchor', 'middle')
                    .style('fill', '{TEXT_COLOR}')
                    .style('font-size', '11px')
                    .style('font-weight', 'bold')
                    .style('font-family', 'Inter, sans-serif')
                    .style('opacity', 0)
                    .text(d => d.contamination_rate.toFixed(1) + '%');
                
                labels.transition()
                    .duration(1000)
                    .delay((d, i) => i * 30 + 500)
                    .style('opacity', 1);
                
                // Add interactivity
                bars.on('mouseover', function(event, d) {{
                    d3.select(this)
                        .transition().duration(150)
                        .attr('opacity', 0.8)
                        .attr('stroke-width', 2)
                        .attr('stroke', 'white');
                    
                    const riskLevel = d.contamination_rate >= 50 ? 'Severe' :
                                    d.contamination_rate >= 30 ? 'High' :
                                    d.contamination_rate >= 15 ? 'Moderate' : 'Low';
                    
                    tooltip.html(`
                        <div style="font-weight: bold; margin-bottom: 5px;">${{d.country}}</div>
                        <div style="color: ${{getColor(d.contamination_rate)}}; margin-bottom: 3px;">● ${{riskLevel}} Risk</div>
                        <div><strong>${{d.contamination_rate.toFixed(1)}}%</strong> contamination rate</div>
                        <div>${{d.monitoring_sites}} monitoring sites</div>
                        <div>Main pollutant: ${{d.main_pollutant}}</div>
                    `)
                    .style('visibility', 'visible');
                }})
                .on('mousemove', function(event) {{
                    tooltip
                        .style('top', (event.pageY - 10) + 'px')
                        .style('left', (event.pageX + 10) + 'px');
                }})
                .on('mouseout', function() {{
                    d3.select(this)
                        .transition().duration(150)
                        .attr('opacity', 1)
                        .attr('stroke-width', 1)
                        .attr('stroke', 'rgba(255,255,255,0.2)');
                    
                    tooltip.style('visibility', 'hidden');
                }});
                
                // Add axes
                const xAxis = g.append('g')
                    .attr('transform', `translate(0,${{height}})`)
                    .call(d3.axisBottom(xScale));
                
                xAxis.selectAll('text')
                    .style('text-anchor', 'end')
                    .style('fill', '{TEXT_COLOR}')
                    .style('font-family', 'Inter, sans-serif')
                    .style('font-size', '10px')
                    .attr('dx', '-.8em')
                    .attr('dy', '.15em')
                    .attr('transform', 'rotate(-45)');
                
                const yAxis = g.append('g')
                    .call(d3.axisLeft(yScale).tickFormat(d => d + '%'));
                
                yAxis.selectAll('text')
                    .style('fill', '{TEXT_COLOR}')
                    .style('font-family', 'Inter, sans-serif')
                    .style('font-size', '11px');
                
                // Style axes
                g.selectAll('.domain, .tick line')
                    .style('stroke', '{TEXT_COLOR}')
                    .style('opacity', 0.3);
                
                // Add axis labels
                g.append('text')
                    .attr('transform', 'rotate(-90)')
                    .attr('y', 0 - margin.left + 20)
                    .attr('x', 0 - (height / 2))
                    .attr('dy', '1em')
                    .style('text-anchor', 'middle')
                    .style('fill', '{TEXT_COLOR}')
                    .style('font-size', '12px')
                    .style('font-family', 'Inter, sans-serif')
                    .text('Contamination Rate (%)');
                
                // Add gridlines
                g.append('g')
                    .attr('class', 'grid')
                    .call(d3.axisLeft(yScale)
                        .tickSize(-width)
                        .tickFormat('')
                    )
                    .style('stroke-dasharray', '2,2')
                    .style('opacity', 0.1);
                
                g.selectAll('.grid line')
                    .style('stroke', '{TEXT_COLOR}');
                
                g.selectAll('.grid path')
                    .style('stroke-width', 0);
                
                // Add summary stats
                const avgRate = d3.mean(sortedData, d => d.contamination_rate);
                const severeCount = sortedData.filter(d => d.contamination_rate >= 50).length;
                const highCount = sortedData.filter(d => d.contamination_rate >= 30 && d.contamination_rate < 50).length;
                
                g.append('text')
                    .attr('x', width)
                    .attr('y', -15)
                    .attr('text-anchor', 'end')
                    .style('fill', '{TEXT_COLOR}')
                    .style('font-size', '11px')
                    .style('font-family', 'Inter, sans-serif')
                    .style('font-weight', 'bold')
                    .text(`Avg: ${{avgRate.toFixed(1)}}% | Severe: ${{severeCount}} | High: ${{highCount}}`);
            }}
            
            // Main execution - silent operation
            loadD3()
                .then(() => createVisualization(data))
                .catch(() => {{
                    // Silent error handling
                    const container = d3.select('#d3-high-risk-countries');
                    if (!container.empty()) {{
                        container.selectAll('*').remove();
                        container.append('div')
                            .style('display', 'flex')
                            .style('justify-content', 'center')
                            .style('align-items', 'center')
                            .style('height', '100%')
                            .style('color', '{TEXT_COLOR}')
                            .style('font-size', '16px')
                            .text('Visualization temporarily unavailable');
                    }}
                }});
            
            return data ? data.length.toString() : '0';
        }}
        """,
        Output('d3-update-trigger', 'children'),
        Input('high-risk-countries-data', 'data')
    )

    
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
    def update_quality_usage_analysis_clean(countries, years, water_types, contamination_types):
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
                        text='Water Quality vs Usage Analysis',
                        x=0.5, xanchor='center',
                        font=dict(size=18, color=TEXT_COLOR)
                    ),
                    plot_bgcolor=VIZ_COLOR,
                    paper_bgcolor=VIZ_COLOR,
                    font=dict(color=TEXT_COLOR),
                    height=550
                )
                return fig
            
            # Create subplots with more space
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Water Impact Intensity by Country', 'Water Source Distribution'),
                specs=[[{"secondary_y": True}, {"type": "pie"}]],
                column_widths=[0.7, 0.3],  # Give more space to the bar chart
                horizontal_spacing=0.1
            )
            
            # Get contamination and abstraction data
            contamination_data = filtered_df[
                filtered_df['measure_category'].str.contains('exceed recommended drinking water limits', na=False) |
                filtered_df['measure_category'].str.contains('pesticides are present', na=False)
            ]
            
            abstraction_data = filtered_df[
                filtered_df['measure_category'] == 'Agriculture freshwater abstraction'
            ]
            
            # Normalized analysis
            if not contamination_data.empty and not abstraction_data.empty:
                # Calculate country averages
                country_contamination = contamination_data.groupby('country')['obs_value'].mean().reset_index()
                country_contamination.columns = ['country', 'contamination_rate']
                
                country_abstraction = abstraction_data.groupby('country')['obs_value'].mean().reset_index()
                country_abstraction.columns = ['country', 'water_usage']
                
                # Apply logarithmic normalization
                normalized_contamination = normalize_by_agricultural_land(
                    country_contamination, df, 'contamination_rate'
                )
                normalized_abstraction = normalize_by_agricultural_land(
                    country_abstraction, df, 'water_usage'
                )
                
                # Merge data
                correlation_data = normalized_contamination.merge(
                    normalized_abstraction, on='country', how='inner'
                )
                
                # Filter valid data
                correlation_data = correlation_data[
                    (correlation_data['contamination_rate_log_normalized'] != correlation_data['contamination_rate']) &
                    (correlation_data['water_usage_log_normalized'] != correlation_data['water_usage'])
                ]
                
                if not correlation_data.empty:
                    # Take top 8 countries for better readability
                    top_countries = correlation_data.nlargest(8, 'contamination_rate_log_normalized')
                    
                    # CONTAMINATION BARS (Primary Y-axis)
                    fig.add_trace(
                        go.Bar(
                            x=top_countries['country'],
                            y=top_countries['contamination_rate_log_normalized'],
                            name='Contamination',
                            marker=dict(
                                color='#c44d4d',
                                opacity=0.8
                            ),
                            hovertemplate='<b>%{x}</b><br>Contamination: %{y:.1f}<br>Raw Rate: %{customdata:.1f}%<extra></extra>',
                            customdata=top_countries['contamination_rate'],
                            offsetgroup=1,
                            width=0.35
                        ),
                        row=1, col=1,
                        secondary_y=False
                    )
                    
                    # WATER USAGE BARS (Secondary Y-axis) 
                    fig.add_trace(
                        go.Bar(
                            x=top_countries['country'],
                            y=top_countries['water_usage_log_normalized'],
                            name='Water Usage',
                            marker=dict(
                                color='#a2d2ff',
                                opacity=0.8
                            ),
                            hovertemplate='<b>%{x}</b><br>Usage: %{y:.1f}<br>Raw: %{customdata:,.0f} m³<extra></extra>',
                            customdata=top_countries['water_usage'],
                            offsetgroup=2,
                            width=0.35
                        ),
                        row=1, col=1,
                        secondary_y=True
                    )
                    
                else:
                    fig.add_annotation(
                        text="No countries with complete data",
                        xref="paper", yref="paper",
                        x=0.35, y=0.5, xanchor='center', yanchor='middle',
                        showarrow=False, font=dict(size=14, color=TEXT_COLOR)
                    )
            else:
                fig.add_annotation(
                    text="Insufficient data for analysis",
                    xref="paper", yref="paper",
                    x=0.35, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=14, color=TEXT_COLOR)
                )
            
            # SIMPLIFIED PIE CHART
            water_source_data = abstraction_data[
                abstraction_data['water_type'].isin(['Surface water', 'Ground water'])
            ]
            
            if not water_source_data.empty:
                source_totals = water_source_data.groupby('water_type')['obs_value'].sum().reset_index()
                
                fig.add_trace(
                    go.Pie(
                        labels=source_totals['water_type'],
                        values=source_totals['obs_value'],
                        hole=0.3,
                        marker=dict(colors=['#96CEB4', '#FECA57']),
                        textinfo='label+percent',
                        textfont=dict(size=11),
                        hovertemplate='<b>%{label}</b><br>%{value:,.0f} m³<extra></extra>',
                        showlegend=False
                    ),
                    row=1, col=2
                )
            
            # CLEAN LAYOUT
            fig.update_layout(
                title=dict(
                    text='Agricultural Water Impact: Contamination vs Usage Intensity',
                    x=0.5, xanchor='center',
                    font=dict(size=16, color=TEXT_COLOR)
                ),
                plot_bgcolor=VIZ_COLOR,
                paper_bgcolor=VIZ_COLOR,
                font=dict(color=TEXT_COLOR),
                height=480,  # Reduced height
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.23,
                    xanchor="center",
                    x=0.30
                ),
                margin=dict(t=80, b=100, l=60, r=40),  # Better margins
                barmode='group',
                bargap=0.2,
                bargroupgap=0.1
            )
            
            # SIMPLIFIED AXES
            fig.update_xaxes(
                title_text="",  # Remove x-axis title to save space
                tickangle=45,
                tickfont=dict(size=10),
                row=1, col=1
            )
            
            # Primary Y-axis (Contamination) - LEFT
            fig.update_yaxes(
                title_text="Contamination Score",
                title_font=dict(color='#c44d4d', size=12),
                tickfont=dict(color='#c44d4d', size=10),
                showgrid=True,
                gridcolor='rgba(255, 107, 107, 0.2)',
                row=1, col=1,
                secondary_y=False
            )
            
            # Secondary Y-axis (Water Usage) - RIGHT
            fig.update_yaxes(
                title_text="Usage Score",
                title_font=dict(color='#a2d2ff', size=12),
                tickfont=dict(color='#a2d2ff', size=10),
                showgrid=False,  # Don't overlap grids
                row=1, col=1,
                secondary_y=True
            )
            
            # SINGLE CLEAN EXPLANATION
            fig.add_annotation(
                text="Intensity scores normalize raw values by agricultural land area. Higher = more intensive impact per hectare.",
                xref="paper", yref="paper",
                x=0.3, y=-0.23,
                xanchor='center', yanchor='top',
                showarrow=False,
                font=dict(size=9, color=TEXT_COLOR),
                bgcolor="rgba(255,255,255,0.05)",
                bordercolor='rgba(255,255,255,0.2)',
                borderwidth=1
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text="Error loading data",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color=TEXT_COLOR)
            )
            fig.update_layout(
                plot_bgcolor=VIZ_COLOR,
                paper_bgcolor=VIZ_COLOR,
                font=dict(color=TEXT_COLOR),
                height=480
            )
            return fig