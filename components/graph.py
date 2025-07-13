from dash import html, dcc
from .styles import TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

def get_graph(id, span=2):
    return html.Div(
        [
            dcc.Graph(id=id)
        ],
        style={
            'backgroundColor': VIZ_COLOR,
            'padding': '10px',
            'borderRadius': '10px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'overflow': 'hidden',
            'grid-column': f'span {span}',
        }
    )
