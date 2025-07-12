from dash import html, dcc
from .styles import TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

def get_card(id, title, span, font_size):
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
                    'fontSize': f'{font_size}',
                    'fontWeight': 'bold',
                    'color': TEXT_COLOR,
                    'padding': '20px 0px'
                }
            )
        ],
        style={
            'backgroundColor': VIZ_COLOR,
            # 'flex': '1',
            'grid-column': f'span {span}',
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