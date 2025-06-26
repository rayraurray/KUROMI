from dash import html, dcc
from .styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from .helpers.data_loader import load_data
from .sidebar import get_sidebar
from .header import get_header
from .controls import get_controls

df = load_data()

layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # Header stays at the top
    get_header("Agri-environmental Indicators Dashboard", "bg.gif"),

    # THIS is the flex container that lives below the header
    # with the sidebar and the content
    html.Div(
        style={
            'display': 'flex',
            'flexDirection': 'row',
            'height': 'calc(100vh - 80px)',
            'margin': 0,
            'padding': 0,
            'width': '100%',
        },
        children=[
            html.Div(
                children=get_sidebar().children,
                style={
                    'flex': '0 0 220px',
                    'height': '100vh',
                    'padding': '20px',
                    'backgroundColor': VIZ_COLOR,
                    'overflowY': 'auto',
                }
            ),

            html.Div(
                id='page-content',
                # children=[
                #     get_controls(df),
                # ],
                style={
                    'flex': 1,
                    'height': '100vh',
                    'overflowY': 'auto',
                    'padding': '20px 40px',
                    'fontFamily': FONT_FAMILY,
                    'backgroundColor': BACKGROUND_COLOR,
                    'color': TEXT_COLOR,
                }
            )
        ]
    )
])