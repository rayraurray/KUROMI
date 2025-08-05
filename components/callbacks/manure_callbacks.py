from dash import Input, Output
import plotly.express as px
from dash import html, dcc

from ..helpers.get_continent import get_continent
from ..helpers.tools import apply_filters, style_title, normalize_by_agricultural_land
from ..styles import CHART_TITLE_CONFIG, VIZ_COLOR, TEXT_COLOR, FONT_FAMILY

def get_manure_callbacks(df, app):
    @app.callback(
        Output('kpi-total-manure', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('nutrient-dropdown', 'value')
    )
    def update_total_manure(countries, years, nutrients):
        d = apply_filters(df, selected_countries=countries, year_range=years, selected_nutrients=nutrients)
        total = d.loc[d['measure_category']=='Livestock manure production', 'obs_value'].sum()

        return f"{total:,.0f}"

    @app.callback(
        Output('kpi-avg-net-input', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('nutrient-dropdown', 'value')
    )
    def update_avg_net(countries, years, nutrients):
        d = apply_filters(df, selected_countries=countries, year_range=years, selected_nutrients=nutrients)
        avg = d.loc[d['measure_category']=='Net input of manure', 'obs_value'].mean()

        return f"{avg:,.2f}"

    @app.callback(
        Output('kpi-pct-manure', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('nutrient-dropdown', 'value')
    )
    def update_pct_manure(countries, years, nutrients):
        d = apply_filters(df, selected_countries=countries, year_range=years, selected_nutrients=nutrients)
        total = d['obs_value'].sum()
        manure = d.loc[d['measure_category'].str.contains('manure|livestock', case=False), 'obs_value'].sum()

        pct = (manure/total*100) if total else 0

        return f"{pct:.1f}%"

    @app.callback(
        Output('kpi-top-country', 'children'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('nutrient-dropdown', 'value')
    )
    def update_top_country(countries, years, nutrients):
        d = apply_filters(df, selected_countries=countries, year_range=years, selected_nutrients=nutrients)
        grp = d.loc[d['measure_category']=='Net input of manure'].groupby('country')['obs_value'].sum()
        if grp.empty:
            return html.Div([html.H4("Top Country by Net Input"), html.P("N/A")])
        country = grp.idxmax(); val = grp.max()

        return f"{country}: {val:,.0f}"

    @app.callback(
        Output('manure-globe', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('nutrient-dropdown', 'value')
    )
    def plot_manure_globe(countries, years, nutrients):
        d = apply_filters(df, selected_countries=countries, year_range=years, selected_nutrients=nutrients)

        cats = ['Manure management', 'Manure imports', 'Manure withdrawals', 'Net input of manure', 'Livestock manure production', 'Organic fertilisers (excluding livestock manure)']
        d = d[d['measure_category'].isin(cats)]
        d = d.groupby('country', as_index=False)['obs_value'].sum()
        d['obs_value'] = d['obs_value'].round(0)

        raw_title = 'Manure-related Categories by Country'

        fig = px.choropleth(
            d,
            title=style_title(raw_title),
            locations='country',
            locationmode='country names',
            color='obs_value',
            color_continuous_scale='Turbo',
            projection='orthographic',
            labels={
                'obs_value':'# of Indicators'
            }
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            margin=dict(l=0, r=0, t=60, b=20),
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(
                color=TEXT_COLOR,
                family=FONT_FAMILY
            )
        )

        fig.update_geos(
            showcoastlines=True,
            showcountries=True,
            showocean=True,
            oceancolor='#4682B4',
            bgcolor=VIZ_COLOR
        )

        return fig

    @app.callback(
    Output('manure-ecdf', 'figure'),
    Input('country-dropdown', 'value'),
    Input('year-slider', 'value'),
    Input('nutrient-dropdown', 'value')
    )
    def update_manure_ecdf(countries, years, nutrients):
        cats = ['Manure management', 'Manure imports', 'Manure withdrawals', 'Net input of manure', 'Livestock manure production', 'Organic fertilisers (excluding livestock manure)']
        d = apply_filters(df, selected_countries=countries, year_range=years, selected_nutrients=nutrients, selected_categories=cats)

        # d_cat = d.groupby(['year', 'measure_category'], as_index=False)['obs_value'].sum()

        raw_title = 'Cumulative Distribution of Manure‑Related Indicators'

        fig = px.ecdf(
            d,
            title=style_title(raw_title),
            x='year',
            y='obs_value',
            color='measure_category'
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            xaxis_title='Year',
            yaxis_title='Value',
            plot_bgcolor=VIZ_COLOR,
            paper_bgcolor=VIZ_COLOR,
            showlegend=False,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=0, r=0, t=60, b=20),
        )
        return fig


    @app.callback(
        Output('manure-chartie', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('nutrient-dropdown', 'value')
    )
    def update_manure_bar_normalized(countries, years, nutrients):
        import numpy as np

        cats = [
            'Manure management',
            'Manure imports',
            'Manure withdrawals',
            'Net input of manure',
            'Livestock manure production',
            'Organic fertilisers (excluding livestock manure)'
        ]

        # Filter data
        d = apply_filters(df, selected_countries=countries, year_range=years, selected_nutrients=nutrients, selected_categories=cats)

        # Aggregate by country
        d_country = d.groupby('country', as_index=False)['obs_value'].sum()

        # Normalize using your provided function
        d_country = normalize_by_agricultural_land(d_country, df, value_column='obs_value')

        # Get top 10 countries by normalized value
        top10 = d_country.sort_values('obs_value_log_normalized', ascending=False).head(10)

        raw_title = 'Top 10 Countries (Normalized by Ag Land Area) — Manure Indicators'

        fig = px.bar(
            top10.sort_values('obs_value_log_normalized'),  # sort low to high for horizontal bars
            x='obs_value_log_normalized',
            y='country',
            orientation='h',
            color='country',
            title=style_title(raw_title),
            labels={'obs_value_log_normalized': 'Normalized Value', 'country': 'Country'},
            color_discrete_sequence=px.colors.qualitative.Set3  # More colorful palette
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(l=20, r=20, t=60, b=40),
            yaxis=dict(tickmode='linear'),
            showlegend=False
        )

        return fig



    @app.callback(
        Output('manure-baby', 'figure'),
        Input('country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('nutrient-dropdown', 'value')
    )
    def update_manure_sunburst(countries, years, nutrients):
        cats = [
            'Manure management',
            'Manure imports',
            'Net input of manure',
            'Livestock manure production',
            'Organic fertilisers (excluding livestock manure)'
        ]

        d = apply_filters(
            df,
            selected_countries=countries,
            year_range=years,
            selected_nutrients=nutrients,
            selected_categories=cats
        )

        # Aggregate just by category (you can add more hierarchy if you want)
        d_grouped = d.groupby('measure_category', as_index=False)['obs_value'].sum()
        d_grouped['root'] = 'Manure'

        raw_title = 'Manure Categories Overview'

        fig = px.sunburst(
            d_grouped,
            path=['root', 'measure_category'],
            values='obs_value',
            color='measure_category',
            color_discrete_sequence=px.colors.qualitative.Bold,
            title=style_title(raw_title)
        )

        fig.update_layout(
            title=CHART_TITLE_CONFIG,
            paper_bgcolor=VIZ_COLOR,
            plot_bgcolor=VIZ_COLOR,
            font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
            margin=dict(t=80, l=0, r=0, b=0)
        )

        return fig
