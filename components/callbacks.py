from dash import Input, Output
import plotly.express as px
from dash import html, dcc

from .helpers.data_loader import load_data
from .helpers.filters import apply_filters, remove_aggregates, style_title
from .styles import CHART_TITLE_CONFIG, VIZ_COLOR, TEXT_COLOR, FONT_FAMILY
from .pages.overview import overview as page1_layout
from .pages.nutrients import nutrients as page2_layout
from .pages.manure import manure as page3_layout
from .pages.erosion import erosion as page4_layout
from .pages.water import water as page5_layout

df = load_data()

def register_callbacks(app):
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def display_page(pathname):
        # map URL paths to the layouts you imported
        page_map = {
            "/": page1_layout,
            "/n": page2_layout,
            "/m": page3_layout,
            "/e": page4_layout,
            "/w": page5_layout,
        }
        # return 404-ish div if not found
        return page_map.get(pathname, html.Div([
            html.H1("404: Not found"),
            html.P(f"No page for `{pathname}`")
        ]))

    @app.callback(
        Output('total-indicators-display', 'children'),
        [ Input('category-dropdown', 'value'), Input('year-slider', 'value') ]
    )
    def update_total_indicators(selected_category, selected_years):
        filtered = apply_filters(df, selected_category, selected_years)
        filtered = filtered[~filtered['country'].isin(['World'])]

        total = filtered['obs_value'].sum()

        return f"{total:,.0f}"

    #================================================================================

    @app.callback(
        Output("trend-chart", "figure"),
        [Input("category-dropdown", "value"), Input("year-slider", "value")]
    )
    def update_trend(selected_category, selected_years):
        d = apply_filters(df, selected_category, selected_years).copy()
        # d = remove_aggregates(d)

        country_totals = d.groupby('country', as_index=False)['obs_value'].sum().nlargest(5, 'obs_value')

        top5_countries = country_totals['country'].tolist()

        d_top5 = d[d['country'].isin(top5_countries)]
        d_top5 = d_top5.groupby(['year', 'country'], as_index=False)['obs_value'].sum()

        raw_title = f"Trend of {selected_category} Indicators ({selected_years[0]}–{selected_years[1]})"

        fig = px.line(
            d_top5,
            title=style_title(raw_title),
            x='year',
            y='obs_value',
            color='country',
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
            yaxis = dict(
                title="Patent Count",
                showgrid=True,
                gridcolor='lightgray',
                gridwidth=1,
                titlefont=dict(size=12),
                tickfont=dict(size=10),
            ),
            margin=dict(l=0, r=0, t=60, b=20),
            legend_title=dict(
                text="Regions"
            ),
            font=dict(
                color=TEXT_COLOR,
                family=FONT_FAMILY
            )
        )

        return fig

    #================================================================================

    @app.callback(
        Output('globe-chart', 'figure'),
        [ Input('category-dropdown', 'value'), Input('year-slider', 'value') ]
    )
    def update_globe(selected_category, selected_years):
        dfg = apply_filters(df, selected_category, selected_years)
        # dfg = remove_aggregates(dfg, True)

        dfg = dfg.groupby('country', as_index=False)['obs_value'].sum()
        dfg['obs_value'] = dfg['obs_value'].round(0)

        raw_title = f"Global Distribution of {selected_category} Indicators ({selected_years[0]}–{selected_years[1]})"

        fig = px.choropleth(
            dfg,
            title=style_title(raw_title),
            locations='country',
            locationmode='country names',
            color='obs_value',
            color_continuous_scale='Viridis',
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
            bgcolor=VIZ_COLOR,
            oceancolor='#5E81AC',
        )

        return fig

    #================================================================================

    @app.callback(
        Output('race-chart', 'figure'),
        [ Input('category-dropdown', 'value'), Input('year-slider', 'value') ]
    )
    def update_race(selected_category, selected_years):
        filtered = apply_filters(df, selected_category, selected_years).copy()
        # filtered = remove_aggregates(filtered)

        filtered = filtered.groupby('country', as_index=False)['obs_value'].sum()

        filtered['obs_value'] = filtered['obs_value'].round(0)

        top10 = filtered.sort_values('obs_value', ascending=False).head(10)
        raw_title = f"Top 10 Regions of {selected_category} Indicators ({selected_years[0]}–{selected_years[1]})"

        fig = px.bar(
            top10,
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
                title='Number of Indicators',
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
                categoryorder='total ascending'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                size=14,
                color=TEXT_COLOR,
                family=FONT_FAMILY
            ),
            showlegend=True,
            margin=dict(l=20, r=20, t=60, b=20),
        )

        fig.update_traces(texttemplate='%{text:,.0f}')

        return fig

    #================================================================================

    @app.callback(
        Output('area-chart', 'figure'),
        [ Input('category-dropdown', 'value'), Input('year-slider', 'value') ]
    )
    def update_area(selected_category, selected_years):
        dfd = apply_filters(df, selected_category, selected_years)
        # dfd = remove_aggregates(dfd)

        size_counts = dfd.groupby('unit_multiplier', as_index=False)['obs_value'].sum()

        raw_title = f"Share of {selected_category} Indicators by Units ({selected_years[0]}–{selected_years[1]})"

        fig = px.treemap(
            size_counts,
            title=style_title(raw_title),
            path=['unit_multiplier'],
            values='obs_value',
            color='obs_value',
            color_continuous_scale=px.colors.sequential.Tealgrn,
            labels={
                'obs_value':'# of Indicators'
            }
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
