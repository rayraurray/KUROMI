from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..sidebar import get_sidebar
from ..header import get_header
from ..controls import get_controls

# FOR NANH AND NGAN,
# IF YOU WANT TO BUILD ANOTHER PAGE, JUST USE THE `overview.py` FILE FOR REFERNCE
# FOR HOW TO BUILD A PAGE

df = load_data()

def get_vizualizations():
    return

nutrients = html.Div([

])