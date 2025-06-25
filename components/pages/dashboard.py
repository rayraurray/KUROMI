from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..data_loader import load_data

df = load_data()

dashboard = html.Div(
    style={
        'font-family': FONT_FAMILY,
        'backgroundColor': BACKGROUND_COLOR,
        'color': TEXT_COLOR,
        'width': '100vw',
        'minHeight': '100vh',
        'margin': 0,
        'padding': 0,
    },

    children=[
        html.H1(
            "Agri-environmental Indicators Dashboard",
            style={
                'textAlign': 'center',
                'fontSize': '50px',
                'font-family': FONT_FAMILY,
                'backgroundImage': 'url("/assets/bg.gif")',
                'backgroundRepeat': 'no-repeat',
                'backgroundPosition': 'center',
                'backgroundSize': 'cover',
                'padding': '100px 20px',
                'margin': '0px 100px 30px 100px',
            }
        ),

        # Controls
        html.Div(
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
        ),

        # Visualizations
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

                # 3D Innovation Globe
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

                # Innovation Race
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

                # Innovation Galaxy
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
)