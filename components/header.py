from dash import html, dcc
from .styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

def get_header(title, bg):
    return html.H1(
        title,
        style={
            'textAlign': 'center',
            'fontSize': '50px',
            'font-family': FONT_FAMILY,
            'color': TEXT_COLOR,
            'backgroundImage': f'url("/assets/{bg}")',
            'backgroundRepeat': 'no-repeat',
            'backgroundPosition': 'center',
            'backgroundSize': 'cover',
            'padding': '100px',
            'margin': '0px',
        }
    )