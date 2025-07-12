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
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 0px'
        },

        children=[
            get_country_filter(df, 1),
            get_nutrients_filter(df, 1),
            get_year_filter(df, 2),
        ]
    ),

    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },

        children=[
            # Total Manure Card
            get_card('kpi-total-manure', "Total Livestock Manure Production", 1, '32px'),

            # Average Net Input Card
            get_card('kpi-avg-net-input', "Average Net Input of Manure", 1, '32px'),

            # Percentage Card
            get_card('kpi-pct-manure', "% Manure-related Categories", 1, '32px'),

            # Top Country by Net Input Card
            get_card('kpi-top-country', "Top Country by Net Input", 1, '32px'),

            get_graph('chart-production-line'),
            get_graph('chart-management-bar'),
            get_graph('chart-treemap'),
            get_graph('chart-box-plot')
        ]
    )
]