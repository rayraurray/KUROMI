from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..graph import get_graph
from ..card import get_card
from ..filters import get_country_filter, get_year_filter, get_nutrients_filter

df = load_data()

manure = [
    html.Div(
        style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'margin': '0px 100px 30px 100px',
            'flexDirection': 'column',
        },

        children=[
            get_country_filter(df),
            get_year_filter(df),
            get_nutrients_filter(df)
        ]
    ),

    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 100px 0px 100px'
        },

        children=[
            # Total Manure Card
            get_card('kpi-total-manure', "Total Livestock Manure Production"),

            # Average Net Input Card
            get_card('kpi-avg-net-input', "Average Net Input of Manure"),

            # Percentage Card
            get_card('kpi-pct-manure', "% Manure-related Categories"),

            # Top Country by Net Input Card
            get_card('kpi-top-country', "Top Country by Net Input"),

            get_graph('chart-production-line'),
            get_graph('chart-management-bar'),
            get_graph('chart-treemap'),
            get_graph('chart-box-plot')
        ]
    )
]