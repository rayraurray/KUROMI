from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..graph import get_graph
from ..card import get_card
from ..filters import get_country_filter, get_year_filter, get_nutrients_filter, get_year_slider

df = load_data()

manure = [
    # Filter controls
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 0px'
        },
        children=[
            get_country_filter(df, 1),
            get_nutrients_filter(df, 1),
            get_year_slider(df, 2)
        ]
    ),

    # KPI cards and description
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },
        children=[
            get_card('kpi-total-manure', "Total Livestock Manure Production", 1, '32px'),
            get_card('kpi-avg-net-input', "Average Net Input of Manure", 1, '32px'),
            get_card('kpi-pct-manure', "% Manure-related Categories", 1, '32px'),
            get_card('kpi-top-country', "Top Country by Net Input", 1, '32px'),

            # Description using html.Strong for bold parts
            html.Div(
                children=[
                    html.P([
                        html.Strong("Understanding the KPIs:"), " Each metric updates based on your filter selections. ",
                        "The Total and Average values reflect aggregate and per-unit scales, while percentages show category shares, ",
                        "and the Top Country highlights leaders in net manure input."
                    ])
                ],
                style={'grid-column': 'span 2', 'padding': '10px'}
            ),

            # Globe chart and its description
            get_graph('manure-globe', 2),
            html.Div(
                children=html.P([
                    html.Strong("Reading the Globe:"), " Hover over regions to explore country-level sums of manure-related indicators. ",
                    "Use rotation to compare hemispheric trends."
                ]),
                style={'grid-column': 'span 2', 'padding': '10px'}
            ),

            # Pie chart by continent and description
            get_graph('manure-pie', 2),
            html.Div(
                children=html.P([
                    html.Strong("Interpreting the Pie Chart:"), " The slices represent continents, aggregated from country data. ",
                    "Filter to refine which categories contribute most in each region."
                ]),
                style={'grid-column': 'span 2', 'padding': '10px'}
            ),

            # Single chart and description
            get_graph('manure-ecdf', 1),

            # Funnel chart and description
            get_graph('manure-funnel', 1),
            html.Div(
                children=html.P([
                    html.Strong("Reading the ECDF Chart:"), " The Empirical Cumulative Distribution Function (ECDF) shows the proportion of observations at or below each value. ",
                    "Use the x-axis to see value thresholds and the y-axis to gauge cumulative share of data points up to that threshold."
                ]),
                style={'grid-column': 'span 1', 'padding': '10px'}
            ),
            html.Div(
                children=html.P([
                    html.Strong("Using the Funnel Chart:"), " Categories are ordered from highest to lowest total values, emphasising the most significant contributors at the top. ",
                    "Read the category names on the y-axis and their corresponding values on the x-axis, which represent aggregate volumes."
                ]),
                style={'grid-column': 'span 1', 'padding': '10px'}
            )
        ]
    )
]
