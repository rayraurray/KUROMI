from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..sidebar import get_sidebar
from ..header import get_header
from ..controls import get_overview_controls

df = load_data()

overview = [
    get_overview_controls(df),
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 100px 0px 100px'
        },

        children=[
            # Summary Card
            html.Div(
                id='total-indicators-card',
                children=[
                    html.H2(
                        "Total Indicators",
                        style={
                            'color': TEXT_COLOR,
                            'margin-bottom': 10,
                            'fontSize': '20px',
                            'fontWeight': 'normal',
                            'font-family': FONT_FAMILY,
                        }
                    ),
                    html.Div(
                        id='total-indicators-display',
                        style={
                            'fontSize': '64px',
                            'fontWeight': 'bold',
                            'color': TEXT_COLOR,
                            'padding-bottom': '10px'
                        }
                    )
                ],
                style={
                    'backgroundColor': VIZ_COLOR,
                    'grid-column': 'span 2',
                    'height': '150px',
                    'width': '100%',
                    'padding': '',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'textAlign': 'center',
                    'margin': '0x 100px 0px 100px',
                    'overflow': 'hidden'
                }
            ),

            html.Div(
                [
                    dcc.Graph(id='trend-chart')
                ],
                style={
                    'backgroundColor': VIZ_COLOR,
                    'padding': '10px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'overflow': 'hidden'
                }
            ),

            # 3D Globe
            html.Div(
                [
                    dcc.Graph(id='globe-chart')
                ],
                style={
                    'backgroundColor': VIZ_COLOR,
                    'padding': '10px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'overflow': 'hidden'
                }
            ),

            # Line Chart
            html.Div(
                [
                    dcc.Graph(id='race-chart')
                ],
                style={
                    'backgroundColor': VIZ_COLOR,
                    'margin': '0 0 0 0',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'overflow': 'hidden'
                }
            ),

            # Area Chart
            html.Div(
                [
                    dcc.Graph(id='area-chart')
                ],
                style={
                    'backgroundColor': VIZ_COLOR,
                    'margin': '0 0 0 0',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'overflow': 'hidden'
                }
            ),
        ]
    )
]