from dash import html, dcc
from .styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR

# Generic function to build a multi-select dropdown with an 'All' option
def _build_multi_dropdown(id, label, options, default_all=True, flex=1, span=2):
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
    ],
    style={
        'flex': str(flex),
        'grid-column': f'span {span}',
    }
    )


def get_country_filter(df, span=2):
    return _build_multi_dropdown(
        id='country-dropdown',
        label='Country',
        options=sorted(df['country'].unique()),
        flex=1,
        span=span
    )

def get_year_filter(df, span=2):
    return _build_multi_dropdown(
        id='year-dropdown',
        label='Year',
        options=sorted(df['year'].unique()),
        flex=1,
        span=span
    )


def get_year_slider(df, span=2):
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
        style={
            'flex': '2',
            'grid-column': f'span {span}',
        }
    )


def get_nutrients_filter(df, span=2):
    return _build_multi_dropdown(
        id='nutrient-dropdown',
        label='Nutrient',
        options=sorted(df['nutrients'].unique()),
        flex=1,
        span=span
    )


def get_unit_filter(df, span=2):
    return _build_multi_dropdown(
        id='unit-dropdown',
        label='Unit',
        options=sorted(df['measure_unit'].unique()),
        flex=1,
        span=span
    )


def get_category_filter(df, span=2):
    return _build_multi_dropdown(
        id='category-dropdown',
        label='Measure Category',
        options=sorted(df['measure_category'].unique()),
        flex=1,
        span=span
    )


def get_water_filter(df, span=2):
    """Water type filter without 'Not applicable' option"""
    water_types = sorted(df['water_type'].dropna().unique())
    # Remove 'Not applicable' if it exists
    water_types = [wt for wt in water_types if wt != 'Not applicable']
    return _build_multi_dropdown(
        id='water-type-dropdown',
        label='Water Type',
        options=water_types,
        flex=1,
        span=span
    )


def get_erosion_filter(df, span=2):
    return _build_multi_dropdown(
        id='erosion-risk-dropdown',
        label='Erosion Risk Level',
        options=sorted(df['erosion_risk_level'].dropna().unique()),
        flex=1,
        span=span
    )

def get_status_filter(df, span=2):
    return _build_multi_dropdown(
        id='status-dropdown',
        label='Observation Status',
        options=sorted(df['observation_status'].dropna().unique()),
        flex=1,
        span=span
    )
    
def get_erosion_type_filter_fixed(df, span=2):
    # Filter to only show erosion-related measure categories
    erosion_data = df[df['measure_category'].str.contains('erosion', case=False, na=False)]
    erosion_types = sorted(erosion_data['measure_category'].unique())
    
    return _build_multi_dropdown(
        id='erosion-type-dropdown',
        label='Erosion Type',
        options=erosion_types,  # This will be ['Water erosion', 'Wind erosion']
        flex=1,
        span=span
    )

def get_contamination_type_filter(span=2):
   """Contamination type filter using consistent styling"""
   contamination_types = ['Nitrate', 'Phosphorus', 'Pesticides', 'Pesticide Presence']
   return _build_multi_dropdown(
       id='contamination-type-dropdown',
       label='Contamination Type',
       options=contamination_types,
       default_all=True,
       flex=1,
       span=span
    )
