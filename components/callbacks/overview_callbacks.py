from dash import Input, Output
import plotly.express as px

from ..helpers.tools import apply_filters, style_title
from ..styles import CHART_TITLE_CONFIG, VIZ_COLOR, TEXT_COLOR, FONT_FAMILY


def get_overview_callbacks(df, app):
    @app.callback(
        Output('total-indicators-display', 'children'),
        [ 
            Input('category-dropdown', 'value'), 
            Input('year-slider', 'value'),
            Input('country-dropdown','value') 
        ]
    )
    def update_total_indicators(categories, years, countries):
        filtered = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        total = filtered['obs_value'].sum()

        return f"{total:,.0f}"

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
    #================================================================================
    @app.callback(
        Output("trend-chart", "figure"),
        [
            Input("category-dropdown", "value"), 
            Input("year-slider", "value"),
            Input("country-dropdown", "value")
        ]
    )
    def update_balance_trend(categories, years, countries):
        d = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        # Filter to measure_category == "Balance"
        d = d[d['measure_category'] == "Balance (inputs minus outputs)"]

        # Group by year and nutrients, calculate mean OBS_VALUE
        d_grouped = d.groupby(['year', 'nutrients'], as_index=False)['obs_value'].mean()

        raw_title = f"Average Balance Over Time by Nutrient ({years[0]}–{years[1]})"

        fig = px.line(
            d_grouped,
            title=style_title(raw_title),
            x='year',
            y='obs_value',
            color='nutrients',
            markers=True
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            xaxis=dict(
                title="Year",
                titlefont=dict(size=12),
                tickfont=dict(size=10),
            ),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            yaxis=dict(
                title="Average Balance",
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=1,
                titlefont=dict(size=12),
                tickfont=dict(size=10),
            ),
            margin=dict(l=0, r=0, t=60, b=20),
            legend_title=dict(
                text="Nutrients"
            ),
            font=dict(
                color=TEXT_COLOR,
                family=FONT_FAMILY
            )
        )

        return fig

    #================================================================================
    @app.callback(
        Output('race-chart', 'figure'),
        [
            Input('category-dropdown', 'value'), 
            Input('year-slider', 'value'),
            Input('country-dropdown', 'value')
        ]
    )
    def update_top_countries_by_observations(categories, years, countries):
        filtered = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        # Sum obs_value per country
        country_totals = (
            filtered.groupby('country', as_index=False)['obs_value']
            .sum()
            .sort_values(by='obs_value', ascending=False)
            .head(10)
        )

        raw_title = f"Top 10 Countries by Total Observations ({years[0]}–{years[1]})"

        fig = px.bar(
            country_totals,
            title=style_title(raw_title),
            x='obs_value',
            y='country',
            orientation='h',
            text='obs_value',
            color_discrete_sequence=['#3b52db']
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            xaxis=dict(
                title='Total Observations (Sum of obs_value)',
                titlefont=dict(size=12),
                tickfont=dict(size=10),
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=1,
            ),
            yaxis=dict(
                title='Country',
                titlefont=dict(size=12),
                tickfont=dict(size=10),
                categoryorder='total ascending',
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                size=14,
                color=TEXT_COLOR,
                family=FONT_FAMILY
            ),
            showlegend=False,
            margin=dict(l=20, r=20, t=60, b=20),
        )

        fig.update_traces(texttemplate='%{text:,}')

        return fig

    #================================================================================
    @app.callback(
        Output('area-chart', 'figure'),
        [
            Input('category-dropdown', 'value'), 
            Input('year-slider', 'value'),
            Input('country-dropdown', 'value')
        ]
    )
    def update_balance_heatmap(categories, years, countries):
        dfd = apply_filters(df, selected_categories=categories, year_range=years, selected_countries=countries)

        # Filter for Balance category only
        dfd = dfd[dfd['measure_category'] == "Balance (inputs minus outputs)"]

        # Group by country and year, summing OBS_VALUE
        pivot_df = (
            dfd.groupby(['country', 'year'], as_index=False)['obs_value']
            .sum()
            .pivot(index='country', columns='year', values='obs_value')
        )

        raw_title = f"Heatmap: Balance by Country & Year ({years[0]}–{years[1]})"

        fig = px.imshow(
            pivot_df,
            labels=dict(x="Year", y="Country", color="Total Balance"),
            title=style_title(raw_title),
            color_continuous_scale='Tealgrn'
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(
                color=TEXT_COLOR,
                family=FONT_FAMILY
            )
        )

        return fig
