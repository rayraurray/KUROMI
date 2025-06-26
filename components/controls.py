from dash import html, dcc
from .styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

def get_overview_controls(df):
    return html.Div(
        style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'margin': '0px 100px 30px 100px',
            'flexDirection': 'column',
        },

        children=[
            html.Div(
                [
                    html.H2(
                        "Select Indicator Category",
                        style={
                            'fontSize': '18px',
                            'fontWeight': 'bold',
                            'font-family': FONT_FAMILY,
                            'padding-bottom': '10px',
                            'color': TEXT_COLOR
                        }
                    ),

                    dcc.Dropdown(
                        id='category-dropdown',
                        options=(
                            [{'label': 'All Categories', 'value': 'All'}]
                            + [{'label': d, 'value': d} for d in sorted(df['measure_category'].unique())]
                        ),
                        value='All',
                        clearable=False,
                    )
                ],

                style={
                    'flex': '1'
                }
            ),

            html.Div(
                [
                    html.H2(
                        "Select Year",
                        style={
                            'fontSize': '18px',
                            'fontWeight': 'bold',
                            'font-family': FONT_FAMILY,
                            'color': '#212529',
                            'padding-bottom': '10px',
                            'color': TEXT_COLOR
                        }
                    ),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=df['year'].min(),
                        max=df['year'].max(),
                        step=1,
                        value=[df['year'].min(), df['year'].max()],
                        marks={str(y): str(y) for y in sorted(df['year'].unique())},
                    )
                ],
                style={
                    'flex': '2',
                }
            )
        ]
    )