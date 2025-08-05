from dash import Input, Output
import plotly.express as px
from dash import html, dcc
import pandas as pd
from ..helpers.tools import apply_filters, style_title, normalize_by_agricultural_land
from ..styles import CHART_TITLE_CONFIG, VIZ_COLOR, TEXT_COLOR, FONT_FAMILY
import json

def get_nutrients_callbacks(df, app):
    # =========================================================================
    # KPI: Avg Nitrogen (Normalized)
    # =========================================================================
    @app.callback(
        Output('avg-nitrogen', 'children'),
        [
            Input('country-dropdown','value'),
            Input('year-slider', 'value'),
            Input('nutrient-dropdown', 'value'),
            Input('category-dropdown', 'value'),
            Input('status-dropdown', 'value')
        ]
    )
    def update_avg_nitrogen(countries, years, nutrients, categories, status):
        filtered = apply_filters(df, selected_countries=countries, year_range=years, 
                                 selected_nutrients=nutrients, selected_categories=categories, 
                                 selected_status=status)
        nitrogen_balance = filtered[
            (filtered['nutrients'] == "Nitrogen") &
            (filtered['measure_category'] == "Balance (inputs minus outputs)")
        ]
        if nitrogen_balance.empty:
            return "0"
        nitrogen_balance = normalize_by_agricultural_land(nitrogen_balance, df, "obs_value")
        return f"{nitrogen_balance['obs_value_log_normalized'].mean():,.2f}"

    # =========================================================================
    # KPI: Avg Phosphorus (Normalized)
    # =========================================================================
    @app.callback(
        Output('avg-phosphorus','children'),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('nutrient-dropdown','value'),
            Input('country-dropdown','value'),
            Input('status-dropdown','value')
        ]
    )
    def update_avg_phosphorus(categories, years, nutrients, countries, status):
        filtered = apply_filters(df, selected_countries=countries, year_range=years, 
                                 selected_nutrients=nutrients, selected_categories=categories,
                                 selected_status=status)
        phosphorus_balance = filtered[
            (filtered['nutrients'] == "Phosphorus") &
            (filtered['measure_category'] == "Balance (inputs minus outputs)")
        ]
        if phosphorus_balance.empty:
            return "0"
        phosphorus_balance = normalize_by_agricultural_land(phosphorus_balance, df, "obs_value")
        return f"{phosphorus_balance['obs_value_log_normalized'].mean():,.2f}"

    # =========================================================================
    # Dual Line Chart (Normalized)
    # =========================================================================
    @app.callback(
        Output('dual-line-chart', 'figure'),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('nutrient-dropdown', 'value'),
            Input('country-dropdown', 'value'),
            Input('status-dropdown', 'value')
        ]
    )
    def update_dual_line_chart(categories, years, nutrients, countries, status):
        d = apply_filters(df, selected_categories=categories, year_range=years,
                          selected_nutrients=nutrients, selected_countries=countries,
                          selected_status=status)
        d = d[d['measure_category'].isin(['Nutrient inputs', 'Nutrient outputs'])]
        if d.empty:
            return px.line(title="Inputs/Outputs Over Time (No Data)")

        d = normalize_by_agricultural_land(d, df, "obs_value")
        d_grouped = d.groupby(['year', 'nutrients', 'measure_category'], as_index=False)['obs_value_log_normalized'].mean()
        d_grouped['label'] = d_grouped['nutrients'] + ' - ' + d_grouped['measure_category']

        fig = px.line(d_grouped, x='year', y='obs_value_log_normalized', color='label', markers=True,
                      title=style_title(f"Normalized Inputs/Outputs Over Time ({years[0]}–{years[1]})"))

        fig.update_layout(title=CHART_TITLE_CONFIG, paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR,
                          font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
                          xaxis=dict(title="Year", gridcolor='rgba(255,255,255,0.1)'),
                          yaxis=dict(title="Normalized Value", gridcolor='rgba(255,255,255,0.1)'))
        return fig

    # =========================================================================
    # Scatter Nitrogen I/O (Normalized)
    # =========================================================================
    @app.callback(
        Output('scatter-nitrogen-input-output', 'figure'),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('nutrient-dropdown', 'value'),
            Input('country-dropdown', 'value'),
            Input('status-dropdown', 'value')
        ]
    )
    def update_scatter_nitrogen_io(categories, years, nutrients, countries, status):
        d = apply_filters(df, selected_categories=categories, year_range=years,
                          selected_nutrients=nutrients, selected_countries=countries,
                          selected_status=status)
        d = d[(d['nutrients'] == 'Nitrogen') & (d['measure_category'].isin(['Nutrient inputs', 'Nutrient outputs']))]
        if d.empty:
            return px.scatter(title="Nitrogen Input vs Output (No Data)")

        d = normalize_by_agricultural_land(d, df, "obs_value")
        pivot = d.pivot_table(index='country', columns='measure_category',
                              values='obs_value_log_normalized', aggfunc='mean').dropna()

        fig = px.scatter(pivot, x='Nutrient inputs', y='Nutrient outputs', text=pivot.index,
                         labels={'Nutrient inputs': 'Nitrogen Input (Normalized)',
                                 'Nutrient outputs': 'Nitrogen Output (Normalized)'},
                         title=style_title("Nitrogen Input vs Output by Country (Normalized)"))

        fig.update_traces(textposition='top center')
        fig.update_layout(title=CHART_TITLE_CONFIG, paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR,
                          font=dict(color=TEXT_COLOR, family=FONT_FAMILY))
        return fig

    # =========================================================================
    # Avg Balance Bar Chart (Normalized)
    # =========================================================================
    @app.callback(
        Output('avg-balance-bar-chart', 'figure'),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('nutrient-dropdown', 'value'),
            Input('country-dropdown', 'value'),
            Input('status-dropdown', 'value')
        ]
    )
    def update_avg_balance_bar(categories, years, nutrients, countries, status):
        d = apply_filters(df, selected_categories=categories, year_range=years,
                          selected_nutrients=nutrients, selected_countries=countries,
                          selected_status=status)
        d = d[d['measure_category'] == 'Balance (inputs minus outputs)']
        if d.empty:
            return px.bar(title="No Data Available")

        d = normalize_by_agricultural_land(d, df, "obs_value")
        d_grouped = d.groupby(['country', 'nutrients'], as_index=False)['obs_value_log_normalized'].mean()

        fig = px.bar(d_grouped, x='country', y='obs_value_log_normalized', color='nutrients', barmode='group',
                     labels={'obs_value_log_normalized': 'Normalized Balance', 'nutrients': 'Nutrient'},
                     title=style_title("Average Normalized Balance per Nutrient by Country"))

        fig.update_layout(title=CHART_TITLE_CONFIG, paper_bgcolor=VIZ_COLOR, plot_bgcolor=VIZ_COLOR,
                          font=dict(color=TEXT_COLOR, family=FONT_FAMILY))
        return fig

    # =========================================================================
    # D3 Chart Data Callback (Normalized)
    # =========================================================================
    @app.callback(
        Output("nutrients-d3-data", "data"),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('nutrient-dropdown', 'value'),
            Input('country-dropdown', 'value'),
            Input('status-dropdown', 'value')
        ]
    )
    def update_d3_data(categories, years, nutrients, countries, status):
        # Filter dataset
        filtered = apply_filters(
            df,
            selected_categories=categories,
            year_range=years,
            selected_nutrients=nutrients,
            selected_countries=countries,
            selected_status=status
        )

        # Keep only Inputs & Outputs
        filtered = filtered[filtered["measure_category"].isin(["Nutrient inputs", "Nutrient outputs"])]

        if filtered.empty:
            return []

        # Normalize values
        filtered = normalize_by_agricultural_land(filtered, df, "obs_value")

        # Group by country & measure_category
        grouped = (
            filtered.groupby(['country', 'measure_category'], as_index=False)['obs_value_log_normalized']
            .mean()
            .pivot(index='country', columns='measure_category', values='obs_value_log_normalized')
            .reset_index()
            .fillna(0)
        )

        # Rename columns for clarity
        grouped = grouped.rename(columns={
            "Nutrient inputs": "inputs",
            "Nutrient outputs": "outputs"
        })

        return grouped.to_dict(orient="records")

    # =========================================================================
    app.clientside_callback(
        """
        function(data) {
            if (!data || !Array.isArray(data) || data.length === 0) {
                const container = document.getElementById('nutrients-d3-container');
                container.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100%;color:#fff;">No data available</div>';
                return "0";
            }

            // Prepare grouped data: [{country, measure, value}]
            let grouped = [];
            data.forEach(d => {
                grouped.push({ country: d.country, measure: "Inputs", value: d.inputs });
                grouped.push({ country: d.country, measure: "Outputs", value: d.outputs });
            });

            // Load D3 if not already
            function loadD3() {
                return new Promise((resolve, reject) => {
                    if (typeof d3 !== 'undefined') { resolve(); return; }
                    const script = document.createElement('script');
                    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js';
                    script.onload = () => resolve();
                    script.onerror = () => reject(new Error('Failed to load D3.js'));
                    document.head.appendChild(script);
                });
            }

            function renderChart() {
                const container = d3.select('#nutrients-d3-container');
                container.selectAll('*').remove();

                const margin = { top: 30, right: 30, bottom: 150, left: 80 };
                const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
                const height = 350;

                const svg = container.append('svg')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom)
                .append('g')
                    .attr('transform', `translate(${margin.left},${margin.top})`);

                const x0 = d3.scaleBand()
                    .domain([...new Set(grouped.map(d => d.country))])
                    .range([0, width])
                    .paddingInner(0.2);

                const x1 = d3.scaleBand()
                    .domain(["Inputs", "Outputs"])
                    .range([0, x0.bandwidth()])
                    .padding(0.05);

                const y = d3.scaleLinear()
                    .domain([0, d3.max(grouped, d => d.value) * 1.1])
                    .nice()
                    .range([height, 0]);

                const color = d3.scaleOrdinal()
                    .domain(["Inputs", "Outputs"])
                    .range(["#3498db", "#e74c3c"]);

                // Tooltip
                const tooltip = d3.select('body').append('div')
                    .attr('class', 'd3-tooltip')
                    .style('position', 'absolute')
                    .style('background', 'rgba(0,0,0,0.8)')
                    .style('color', '#fff')
                    .style('padding', '8px')
                    .style('border-radius', '4px')
                    .style('visibility', 'hidden');

                // Draw bars
                svg.selectAll("g")
                    .data(grouped.reduce((acc, d) => {
                        let found = acc.find(a => a.country === d.country);
                        if (!found) acc.push({ country: d.country, values: [] });
                        acc.find(a => a.country === d.country).values.push(d);
                        return acc;
                    }, []))
                    .enter()
                    .append("g")
                    .attr("transform", d => `translate(${x0(d.country)},0)`)
                    .selectAll("rect")
                    .data(d => d.values)
                    .enter().append("rect")
                    .attr("x", d => x1(d.measure))
                    .attr("y", height)
                    .attr("width", x1.bandwidth())
                    .attr("height", 0)
                    .attr("fill", d => color(d.measure))
                    .on('mouseover', (event, d) => {
                        tooltip.style('visibility', 'visible')
                            .html(`<b>${d.country}</b><br>${d.measure}: ${d.value.toFixed(2)}`);
                    })
                    .on('mousemove', event => {
                        tooltip.style('top', (event.pageY - 20) + 'px')
                            .style('left', (event.pageX + 10) + 'px');
                    })
                    .on('mouseout', () => tooltip.style('visibility', 'hidden'))
                    .transition()
                    .duration(1000)
                    .attr("y", d => y(d.value))
                    .attr("height", d => height - y(d.value));

                // Axes
                svg.append('g')
                    .attr('transform', `translate(0,${height})`)
                    .call(d3.axisBottom(x0))
                    .selectAll('text')
                    .attr('transform', 'rotate(-45)')
                    .style('text-anchor', 'end')
                    .style('fill', '#fff');

                svg.append('g').call(d3.axisLeft(y)).selectAll('text').style('fill', '#fff');

                // Legend
                const legend = svg.append("g")
                    .attr("transform", `translate(${width - 120}, 0)`);

                ["Inputs", "Outputs"].forEach((key, i) => {
                    legend.append("rect")
                        .attr("x", 0)
                        .attr("y", i * 20)
                        .attr("width", 15)
                        .attr("height", 15)
                        .attr("fill", color(key));
                    legend.append("text")
                        .attr("x", 20)
                        .attr("y", i * 20 + 12)
                        .text(key)
                        .style("fill", "#fff")
                        .style("font-size", "12px");
                });
            }

            return loadD3().then(renderChart).then(() => data.length.toString());
        }
        """,
        Output('nutrients-d3-trigger', 'children'),
        Input('nutrients-d3-data', 'data'),
        prevent_initial_call=True
    )
