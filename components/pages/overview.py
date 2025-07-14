from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..card import get_card
from ..graph import get_graph
from ..filters import get_category_filter, get_year_filter, get_year_slider,get_country_filter, get_unit_filter

df = load_data()

overview = [
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 0px'
        },

        children=[
            get_category_filter(df, 1),
            get_country_filter(df, 1),
            get_year_slider(df, 2),
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
            # Summary Card
            get_card('total-indicators-display', "Total Indicators", 1, '32px'),
            get_card('total-countries', "Total Countries", 1, '32px'),
            get_card('avg-nutrient', "Average Nutrient Balance", 1, '32px'),
            get_card('percent-normal', "% Normal Observation Status", 1, '32px'),

            # Trend Chart
            get_graph('trend-chart', 2),

            # Line Chart
            get_graph('race-chart', 1),

            # Area Chart
            get_graph('area-chart', 1)
        ]
    )
]