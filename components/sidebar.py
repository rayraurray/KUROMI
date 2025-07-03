from dash import html, dcc
from .styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

# Define sidebar links
sidebar_links = [
    {'label': 'Overview', 'href': '/'},
    {'label': 'Nutrients', 'href': '/n'},
    {'label': 'Manure', 'href': '/m'},
    {'label': 'Erosion ', 'href': '/e'},
    {'label': 'Water', 'href': '/w'},
]

# Sidebar component
def get_sidebar():
    return html.Div(
        [
            html.H2(
                "KUROMI",
                className='sidebar-title',
                style={
                    'textAlign': 'center',
                    'color': TEXT_COLOR,
                    'font-family': FONT_FAMILY,
                }
            ),
            # html.Hr(),
            html.Div(
                [
                    dcc.Link(
                        link['label'],
                        href=link['href'],
                        className='sidebar-link',
                        style={
                            'display': 'block',
                            'padding': '10px 15px',
                            'color': TEXT_COLOR,
                            'textDecoration': 'none',
                            'fontWeight': 'bold'
                        }
                    ) for link in sidebar_links
                ],
                className='sidebar-menu',
                style={
                    'padding-top': '20px',
                    'color': TEXT_COLOR,
                    'font-family': FONT_FAMILY,
                }
            )
        ],
        className='sidebar',
        style={
            'flex': '0 0 220px',
            # 'padding': '20px',
            'backgroundColor': VIZ_COLOR,
            'height': '100%'
        }
    )
