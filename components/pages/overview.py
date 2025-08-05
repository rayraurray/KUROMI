from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..card import get_card
from ..graph import get_graph
from ..filters import get_category_filter, get_year_slider, get_country_filter
import dash_html_components as html

# Load the dataset
df = load_data()

overview = [
    # ===========================
    # FILTERS ROW 
    # ===========================
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 0px'
        },
        children=[
            get_category_filter(df, 1),
            get_country_filter(df, 1),
            get_year_slider(df, 2),
        ]
    ),

    # ===========================
    # KPI CARDS
    # ===========================
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr 1fr 1fr',  
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },
        children=[
            get_card('total-indicators-display', "Total Indicators", 1, '28px'),
            get_card('total-countries', "Total Countries", 1, '28px'),
            get_card('avg-nutrient', "Average Nutrient Balance", 1, '28px'),
            get_card('percent-normal', "% Normal Observation Status", 1, '28px'),
        ]
    ),

    # ===========================
    # MAIN VISUALIZATIONS SECTION
    # ===========================
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr',
            'grid-gap': '30px',
            'margin': '40px 0px 0px 0px'
        },
        children=[
            # ===========================
            # TREND CHART + DESCRIPTION
            # ===========================
            html.Div([
                get_graph('trend-chart', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Average Nutrient Balance Analysis: "), html.Br(),
                        "This chart illustrates long-term nutrient trends (1985–2023). "
                        "Nitrogen remains consistently higher than Phosphorus, peaking in 2020 before a sharp drop in 2021, "
                        "suggesting potential reporting anomalies or policy-driven shifts. "
                        "Both nutrients show synchronized patterns in recent years, indicating systemic external influences."
                    ]),
                    style={
                        'padding': '15px',
                        'color': TEXT_COLOR,
                        'background-color': 'rgba(255,255,255,0.05)',
                        'border-radius': '8px',
                        'margin-top': '10px',
                        'line-height': '1.5'
                    }
                )
            ]),

            # ===========================
            # TOP COUNTRIES BAR CHART
            # ===========================
            html.Div(
                children=html.P([
                    html.Strong("Top 10 Countries (Cumulative) Analysis: "), html.Br(),
                    "This bar chart displays the cumulative normalized nutrient balance across the selected years. "
                    "It highlights which countries have the largest total nutrient impact over time. "
                    "China and the US lead significantly, indicating their overall dominance in nutrient accumulation, "
                    "while other countries like the EU, India, and Brazil follow with substantial but lower totals."
                ]),
                style={
                    'padding': '15px',
                    'color': TEXT_COLOR,
                    'background-color': 'rgba(255,255,255,0.05)',
                    'border-radius': '8px',
                    'margin-top': '10px',
                    'line-height': '1.5'
                }
            ),
            
            # ===========================
            # HEATMAP VISUALIZATION
            # ===========================
            html.Div([
                get_graph('area-chart', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Balance by Countries Analysis: "), html.Br(),
                        "This heatmap visualizes nutrient balance by country/year. "
                        "Canada and Indonesia exhibit sustained high balances post-2000, "
                        "while smaller nations such as Latvia and Malta show lighter or inconsistent reporting."
                    ]),
                    style={
                        'padding': '15px',
                        'color': TEXT_COLOR,
                        'background-color': 'rgba(255,255,255,0.05)',
                        'border-radius': '8px',
                        'margin-top': '10px',
                        'line-height': '1.5'
                    }
                )
            ]),

            # ===========================
            # D3 NUTRIENT BALANCE VISUALIZATION
            # ===========================
            html.Div([
                html.H4("D3.js Nutrient Balance Visualization", 
                        style={'color': TEXT_COLOR, 'margin-bottom': '10px'}),
                dcc.Store(id="d3-data"),
                html.Div(id="d3-container", style={
                    "border": "1px solid rgba(255,255,255,0.1)",
                    "height": "400px",
                    "backgroundColor": "rgba(255,255,255,0.02)",
                    "borderRadius": "8px",
                    "margin-bottom": "30px",
                    "position": "relative"
                }),
                html.Div(id='overview-d3-update-trigger', style={'display': 'none'}),
                html.Div(
                    children=html.P([
                        html.Strong("Interactive D3 Analysis (Average Intensity): "), html.Br(),
                        "This interactive visualization ranks countries by their average normalized nutrient balance per year, "
                        "focusing on intensity rather than total accumulation. "
                        "Hover over bars to compare normalized intensity (log-scaled) with raw nutrient balance values."
                    ]),
                    style={
                        'padding': '15px',
                        'color': TEXT_COLOR,
                        'background-color': 'rgba(255,255,255,0.05)',
                        'border-radius': '8px',
                        'margin-top': '10px',
                        'line-height': '1.5'
                    }
                )
            ])
        ]
    )
]
