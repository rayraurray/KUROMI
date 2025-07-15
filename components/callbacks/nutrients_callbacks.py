from dash import Input, Output
import plotly.express as px
from dash import html, dcc
import pandas as pd

from ..helpers.tools import apply_filters, style_title
from ..styles import CHART_TITLE_CONFIG, VIZ_COLOR, TEXT_COLOR, FONT_FAMILY

def get_nutrients_callbacks(df,app):
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
        filtered = apply_filters(df,selected_countries=countries, year_range=years, 
                                 selected_nutrients=nutrients, selected_categories=categories, 
                                 selected_status=status)
        
        # Apply fixed filters: nutrients = Nitrogen, measure_category = Balance
        nitrogen_balance = filtered[
            (filtered['nutrients'] == "Nitrogen") &
            (filtered['measure_category'] == "Balance (inputs minus outputs)")
        ]

        total = nitrogen_balance['obs_value'].mean()

        return f"{total:,.2f}"

    #================================================================================

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
    def update_avg_phosphorus(countries, years, nutrients, categories, status):
        filtered = apply_filters(df, selected_countries=countries, year_range=years, 
                                 selected_nutrients=nutrients, selected_categories=categories,
                                 selected_status=status)
        
        nitrogen_balance = filtered[
            (filtered['nutrients'] == "Phosphorus") &
            (filtered['measure_category'] == "Balance (inputs minus outputs)")
        ]

        total = nitrogen_balance['obs_value'].mean()

        return f"{total:,.2f}"
    
#================================================================================

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
        d = apply_filters(
            df,
            selected_categories=categories,
            year_range=years,
            selected_nutrients=nutrients,  # ✅ Nutrient filter applied here
            selected_countries=countries,
            selected_status=status
        )

        # Filter Input/Output categories only
        d = d[d['measure_category'].isin(['Nutrient inputs', 'Nutrient outputs'])]

        # Group by year, nutrients, measure_category
        d_grouped = d.groupby(['year', 'nutrients', 'measure_category'], as_index=False)['obs_value'].sum()

        # Create a combined label for clarity in the chart
        d_grouped['label'] = d_grouped['nutrients'] + ' - ' + d_grouped['measure_category']

        fig = px.line(
            d_grouped,
            x='year',
            y='obs_value',
            color='label',
            markers=True,
            title=style_title(f"Inputs/Outputs Over Time ({years[0]}–{years[1]})")
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            xaxis_title="Year",
            yaxis_title="Observation Value",
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig
    
#================================================================================

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
        d = apply_filters(
            df,
            selected_categories=categories,
            year_range=years,
            selected_nutrients=nutrients,
            selected_countries=countries,
            selected_status=status
        )

        # Filter for Nitrogen only, Input and Output only
        d = d[
            (d['nutrients'] == 'Nitrogen') &
            (d['measure_category'].isin(['Nutrient inputs', 'Nutrient outputs']))
        ]

        # Pivot table: rows = country, columns = measure_category
        pivot = d.pivot_table(
            index='country',
            columns='measure_category',
            values='obs_value',
            aggfunc='sum'
        ).dropna()

        if pivot.empty:
            return px.scatter(title="Nitrogen Input vs Output (No Data)")

        fig = px.scatter(
            pivot,
            x='Nutrient inputs',
            y='Nutrient outputs',
            text=pivot.index,
            labels={
                'Nutrient input': 'Nitrogen Input',
                'Nutrient output': 'Nitrogen Output'
            },
            title=style_title("Nitrogen Input vs Output by Country"),
        )

        fig.update_traces(textposition='top center')

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            xaxis_title="Nitrogen Input",
            yaxis_title="Nitrogen Output",
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig

#================================================================================

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
        d = apply_filters(
            df,
            selected_categories=categories,
            year_range=years,
            selected_nutrients=nutrients,
            selected_countries=countries,
            selected_status=status
        )

        # Filter for Balance only
        d = d[d['measure_category'] == 'Balance (inputs minus outputs)']

        if d.empty:
            return px.bar(title="No Data Available")

        # Group by country and nutrient, calculate mean balance value
        d_grouped = d.groupby(['country', 'nutrients'], as_index=False)['obs_value'].mean()

        fig = px.bar(
            d_grouped,
            x='country',
            y='obs_value',
            color='nutrients',
            barmode='group',
            labels={'obs_value': 'Average Balance', 'nutrients': 'Nutrient'},
            title=style_title("Average Balance per Nutrient by Country")
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            xaxis_title="Country",
            yaxis_title="Average Balance (obs_value)",
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        return fig