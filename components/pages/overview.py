from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..card import get_card
from ..graph import get_graph
from ..filters import get_category_filter, get_year_filter, get_year_slider

df = load_data()

overview = [
    html.Div(
        style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'margin': '0px 100px 30px 100px',
            'flexDirection': 'column',
        },

        children=[
            get_category_filter(df),
            get_year_slider(df)
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
            # Summary Card
            get_card('total-indicators-display', "Total Indicators"),

            # Trend Chart
            get_graph('trend-chart'),

            # 3D Globe
            get_graph('globe-chart'),

            # Line Chart
            get_graph('race-chart'),

            # Area Chart
            get_graph('area-chart')
        ]
    )
]