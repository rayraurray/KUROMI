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
                    'margin': '10px 0px',
                    'fontSize': '20px',
                    'fontWeight': 'normal',
                    'font-family': FONT_FAMILY,
                }
            ),
            html.Div(
                id=id,
                style={
                    'flexGrow': '1',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'fontSize': f'{font_size}',
                    'fontWeight': 'bold',
                    'color': TEXT_COLOR,
                    'width': '100%'
                }
            )
        ],
        style={
            'backgroundColor': VIZ_COLOR,
            'grid-column': f'span {span}',
            'height': '150px',
            'width': '100%',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'textAlign': 'center',
            'overflow': 'hidden',
            'display': 'flex',
            'flexDirection': 'column',
            'alignItems': 'center',
        }
    )
