from dash import html, dcc
from .styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

# Generic function to build a multi-select dropdown with an 'All' option
def _build_multi_dropdown(id, label, options, default_all=True, flex=1):
    all_opt = [{'label': 'All', 'value': 'All'}]
    dropdown_opts = all_opt + [{'label': opt, 'value': opt} for opt in options]
    default_value = ['All'] if default_all else []
    return html.Div([
        html.H2(
            label,
            style={
                'fontSize': '18px',
                'fontWeight': 'bold',
                'font-family': FONT_FAMILY,
                'padding-bottom': '10px',
                'color': TEXT_COLOR
            }
        ),
        dcc.Dropdown(
            id=id,
            options=dropdown_opts,
            value=default_value,
            multi=True,
            clearable=False,
            style={'backgroundColor': VIZ_COLOR, 'color': TEXT_COLOR}
        )
    ], style={'flex': str(flex)})


def get_country_filter(df):
    return _build_multi_dropdown(
        id='country-dropdown',
        label='Country',
        options=sorted(df['country'].unique()),
        flex=1
    )

def get_year_filter(df):
    return _build_multi_dropdown(
        id='year-dropdown',
        label='Year',
        options=sorted(df['year'].unique()),
        flex=1
    )


def get_year_slider(df):
    return html.Div(
        [
            html.H2(
                "Year",
                style={
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'font-family': FONT_FAMILY,
                    'padding-bottom': '10px',
                    'color': TEXT_COLOR
                }
            ),
            dcc.RangeSlider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                step=1,
                value=[df['year'].min(), df['year'].max()],
                marks={str(y): str(y) for y in sorted(df['year'].unique())},
                tooltip={'always_visible': False}
            )
        ],
        style={'flex': '2'}
    )


def get_nutrients_filter(df):
    return _build_multi_dropdown(
        id='nutrient-dropdown',
        label='Nutrient',
        options=sorted(df['nutrient'].unique()),
        flex=1
    )


def get_unit_filter(df):
    return _build_multi_dropdown(
        id='unit-dropdown',
        label='Unit',
        options=sorted(df['unit_of_measure'].unique()),
        flex=1
    )


def get_category_filter(df):
    return _build_multi_dropdown(
        id='category-dropdown',
        label='Measure Category',
        options=sorted(df['measure_category'].unique()),
        flex=1
    )


def get_water_filter(df):
    return _build_multi_dropdown(
        id='water-type-dropdown',
        label='Water Type',
        options=sorted(df['water_type'].dropna().unique()),
        flex=1
    )


def get_erosion_filter(df):
    return _build_multi_dropdown(
        id='erosion-risk-dropdown',
        label='Erosion Risk Level',
        options=sorted(df['erosion_risk_level'].dropna().unique()),
        flex=1
    )
