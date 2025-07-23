from dash import Input, Output
from dash import html, dcc

from ..helpers.data_loader import load_data
from ..pages.overview import overview as page1_layout
from ..pages.nutrients import nutrients as page2_layout
from ..pages.manure import manure as page3_layout
from ..pages.erosion import erosion as page4_layout
from ..pages.water import water as page5_layout
from .overview_callbacks import get_overview_callbacks
from .manure_callbacks import get_manure_callbacks
from .nutrients_callbacks import get_nutrients_callbacks
from .erosion_callbacks import get_erosion_callbacks

df = load_data()

def register_callbacks(app):
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def display_page(pathname):
        # map URL paths to the layouts you imported
        page_map = {
            "/": page1_layout,
            "/n": page2_layout,
            "/m": page3_layout,
            "/e": page4_layout,
            "/w": page5_layout,
        }
        # return 404-ish div if not found
        return page_map.get(pathname, html.Div([
            html.H1("404: Not found"),
            html.P(f"No page for `{pathname}`")
        ]))

    #================================================================================

    get_overview_callbacks(df, app)

    #================================================================================

    get_manure_callbacks(df, app)

    #================================================================================

    get_nutrients_callbacks(df, app)
    
    #================================================================================

    get_erosion_callbacks(df, app)