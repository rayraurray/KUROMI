from dash import Input, Output
import plotly.express as px

from ..helpers.tools import apply_filters, style_title
from ..styles import CHART_TITLE_CONFIG, VIZ_COLOR, TEXT_COLOR, FONT_FAMILY
from ..helpers.tools import apply_filters, style_title, normalize_by_agricultural_land

import json
from dash import dcc


def get_overview_callbacks(df, app):
    @app.callback(
        Output('total-indicators-display', 'children'),
        [Input('category-dropdown', 'value'), Input('year-slider', 'value'), Input('country-dropdown','value')]
    )
    def update_total_indicators(categories, years, countries):
        filtered = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        # Normalize obs_value
        normalized_df = normalize_by_agricultural_land(filtered, df, "obs_value")

        total = normalized_df["obs_value_log_normalized"].sum()

        return f"{total:,.2f}"  # Show normalized sum


    #================================================================================
    @app.callback(
            Output("total-countries", "children"),
            [
                Input('category-dropdown', 'value'),
                Input('year-slider', 'value'),
                Input('country-dropdown', 'value')
            ]
    )
    def update_total_countries(categories, years, countries):
        filtered = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        unique_countries = filtered['country'].nunique()

        return f"{unique_countries:,}"

    #================================================================================
    @app.callback(
        Output('avg-nutrient','children'),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('country-dropdown', 'value')
        ]
    )
    def update_avg_nutrient(categories, years, countries):
        filtered = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        # Filter for Balance only
        balance_data = filtered[filtered['measure_category'] == 'Balance (inputs minus outputs)']

        avg_balance = balance_data['obs_value'].mean()

        return f"{avg_balance:,.2f}"

    #================================================================================
    @app.callback(
        Output('percent-normal', 'children'),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('country-dropdown', 'value')
        ]
    )
    def update_percent_normal(categories, years, countries):
        filtered = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        total_count = len(filtered)
        normal_count = (filtered['observation_status'] == "Normal value").sum()

        percentage = (normal_count / total_count) * 100

        return f"{percentage:.2f}%"
    # ==============================
    # TREND CHART (Dark Themed)
    # ==============================
    @app.callback(
        Output("trend-chart", "figure"),
        [Input("category-dropdown", "value"),
         Input("year-slider", "value"),
         Input("country-dropdown", "value")]
    )
    def update_balance_trend(categories, years, countries):
        d = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)
        d = d[d['measure_category'] == "Balance (inputs minus outputs)"]
        d = normalize_by_agricultural_land(d, df, "obs_value")

        d_grouped = d.groupby(['year', 'nutrients'], as_index=False)['obs_value_log_normalized'].mean()

        fig = px.line(
            d_grouped,
            x='year',
            y='obs_value_log_normalized',
            color='nutrients',
            markers=True,
            title=style_title(f"Normalized Balance Over Time ({years[0]}–{years[1]})")
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            xaxis=dict(title="Year", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title="Normalized Balance", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(l=20, r=20, t=60, b=40),
            legend_title=dict(text="Nutrients")
        )
        return fig

    # ==============================
    # HEATMAP (Dark Themed)
    # ==============================
    @app.callback(
        Output('area-chart', 'figure'),
        [Input('category-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('country-dropdown', 'value')]
    )
    def update_balance_heatmap(categories, years, countries):
        dfd = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)
        dfd = dfd[dfd['measure_category'] == "Balance (inputs minus outputs)"]
        dfd = normalize_by_agricultural_land(dfd, df, "obs_value")

        pivot_df = (
            dfd.groupby(['country', 'year'], as_index=False)['obs_value_log_normalized']
            .sum()
            .pivot(index='country', columns='year', values='obs_value_log_normalized')
        )

        fig = px.imshow(
            pivot_df,
            labels=dict(x="Year", y="Country", color="Normalized Balance"),
            color_continuous_scale='Tealgrn',
            title=style_title(f"Normalized Heatmap: Balance by Country & Year ({years[0]}–{years[1]})")
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=20, r=20, t=60, b=40)
        )
        return fig

    # ==============================
    # D3 Data Callback
    # ==============================x
    @app.callback(
        Output("d3-data", "data"),
        [
            Input('category-dropdown', 'value'),
            Input('year-slider', 'value'),
            Input('country-dropdown', 'value')
        ]
    )
    def update_d3_data(categories, years, countries):
        # Filter
        filtered = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)
        filtered = filtered[filtered["measure_category"] == "Balance (inputs minus outputs)"]

        if filtered.empty:
            return []

        # ✅ Normalize BEFORE aggregation
        filtered = normalize_by_agricultural_land(filtered, df, "obs_value")

        # ✅ Group using normalized values per country
        grouped = (
            filtered.groupby("country", as_index=False)
            .agg(
                raw_value=("obs_value", "mean"),  # Average raw balance
                normalized_value=("obs_value_log_normalized", "mean")  # Average normalized balance
            )
            .sort_values(by="normalized_value", ascending=False)
        )

        # ✅ Convert to list of dict for D3
        return grouped.to_dict(orient="records")

    #================================================================================
    app.clientside_callback(
        """
        function(data) {
            // ✅ Safety: Exit early if no data
            if (!data || !Array.isArray(data) || data.length === 0) {
                const container = document.getElementById('d3-container');
                if (container) {
                    container.innerHTML = '<div style="display:flex;justify-content:center;align-items:center;height:100%;color:#fff;">No data available</div>';
                }
                return "0";
            }

            console.log("D3 Data received:", data); // Debugging log

            // ✅ Sort descending by normalized_value
            data.sort((a, b) => b.normalized_value - a.normalized_value);

            // Dynamically load D3.js if missing
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

            // Chart rendering after D3 is loaded
            function renderChart() {
                const container = d3.select('#d3-container');
                container.selectAll('*').remove();

                const margin = {top: 40, right: 40, bottom: 100, left: 80};
                const width = container.node().getBoundingClientRect().width - margin.left - margin.right;
                const height = 350;

                const svg = container.append('svg')
                    .attr('width', width + margin.left + margin.right)
                    .attr('height', height + margin.top + margin.bottom)
                .append('g')
                    .attr('transform', `translate(${margin.left},${margin.top})`);

                const x = d3.scaleBand()
                    .domain(data.map(d => d.country))
                    .range([0, width])
                    .padding(0.2);

                const y = d3.scaleLinear()
                    .domain([0, d3.max(data, d => d.normalized_value) * 1.1])
                    .nice()
                    .range([height, 0]);

                const color = d3.scaleSequential(d3.interpolateBlues)
                    .domain([0, d3.max(data, d => d.normalized_value)]);

                // Tooltip setup
                const tooltip = d3.select('body').append('div')
                    .attr('class', 'd3-tooltip')
                    .style('position', 'absolute')
                    .style('background', 'rgba(0,0,0,0.8)')
                    .style('color', '#fff')
                    .style('padding', '8px')
                    .style('border-radius', '4px')
                    .style('visibility', 'hidden');

                // Bars
                svg.selectAll('.bar')
                    .data(data)
                    .enter()
                    .append('rect')
                    .attr('class', 'bar')
                    .attr('x', d => x(d.country))
                    .attr('width', x.bandwidth())
                    .attr('y', height)
                    .attr('height', 0)
                    .attr('fill', d => color(d.normalized_value))
                    .on('mouseover', (event, d) => {
                        tooltip.style('visibility', 'visible')
                            .html(`<b>${d.country}</b><br>Normalized: ${d.normalized_value.toFixed(2)}<br>Raw: ${d.raw_value.toFixed(2)}`);
                    })
                    .on('mousemove', event => {
                        tooltip.style('top', (event.pageY - 20) + 'px').style('left', (event.pageX + 10) + 'px');
                    })
                    .on('mouseout', () => tooltip.style('visibility', 'hidden'))
                    .transition()
                    .duration(1000)
                    .attr('y', d => y(d.normalized_value))
                    .attr('height', d => height - y(d.normalized_value));

                // Axes
                svg.append('g')
                    .attr('transform', `translate(0,${height})`)
                    .call(d3.axisBottom(x))
                    .selectAll('text')
                    .attr('transform', 'rotate(-45)')
                    .style('text-anchor', 'end');

                svg.append('g').call(d3.axisLeft(y));
            }

            // ✅ Ensure D3 is loaded before rendering
            return loadD3().then(renderChart).then(() => data.length.toString());
        }
        """,
        Output('overview-d3-update-trigger', 'children'),
        Input('d3-data', 'data'),
        prevent_initial_call=True
    )
