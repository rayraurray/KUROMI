from dash import html, dcc
from .styles import TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

def get_card(id, title):
    return html.Div(
        id=f'{id}-card',
        children=[
            html.H2(
                title,
                style={
                    'color': TEXT_COLOR,
                    'margin-bottom': 10,
                    'fontSize': '20px',
                    'fontWeight': 'normal',
                    'font-family': FONT_FAMILY,
                }
            ),
            html.Div(
                id=id,
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
            # 'flex': '1',
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
    )