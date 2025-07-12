from dash import html, dcc
from .styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from .helpers.data_loader import load_data
from .sidebar import get_sidebar
from .header import get_header

df = load_data()

layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Header stays at the top
    get_header("Agri-environmental Indicators Dashboard", "bg.gif"),

    # THIS is the flex container that lives below the header
    # with the sidebar and the content
    html.Div(
        id='main',
        style={
            'display': 'flex',
            'flexDirection': 'row',
            'margin': 0,
            'padding': 0,
            'width': '100%',
        },
        children=[
            get_sidebar(),
            html.Div(
                id='page-content',
                style={
                    'flex': 1,
                    'padding': '20px 40px',
                    'fontFamily': FONT_FAMILY,
                    'backgroundColor': BACKGROUND_COLOR,
                    'color': TEXT_COLOR,
                }
            )
        ]
    )
])