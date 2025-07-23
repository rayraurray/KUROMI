from dash import html, dcc
import numpy as np
from plotly.subplots import make_subplots
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..graph import get_graph
from ..card import get_card
from ..filters import get_country_filter, get_year_filter, get_erosion_filter, get_status_filter, get_year_slider

df = load_data()

erosion = [
    # Filter controls
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 0px'
        },
        children=[
            get_country_filter(df, 1),
            get_erosion_filter(df, 1),
            get_status_filter(df, 1),
            get_year_slider(df, 3)
        ]
    ),
    
    # KPI cards with clearer metrics
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr 1fr 1fr',
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },
        children=[
            get_card('kpi-total-observations', 'Total Observations', 1, '28px'),
            get_card('kpi-critical-risk-areas', 'Critical Risk Areas', 1, '28px'),
            get_card('kpi-avg-erosion-intensity', 'Avg Erosion Intensity', 1, '28px'),
            get_card('kpi-countries-affected', 'Countries Affected', 1, '28px'),
            
            # Clear KPI explanation
            html.Div(
                children=[
                    html.P([
                        html.Strong("Key Erosion Insights:"), " Track total erosion observations across regions, ",
                        "identify critical areas requiring immediate intervention, monitor average intensity levels, ",
                        "and assess the geographic spread of erosion impacts."
                    ])
                ],
                style={'grid-column': 'span 4', 'padding': '15px', 'color': TEXT_COLOR, 
                      'background-color': 'rgba(255,255,255,0.05)', 'border-radius': '8px', 'margin-top': '20px'}
            )
        ]
    ),
    
    # Three focused visualizations
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr',
            'grid-gap': '30px',
            'margin': '40px 0px 0px 0px'
        },
        children=[
            # Visualization 1: Erosion Risk Evolution Over Time
            html.Div([
                get_graph('erosion-temporal-evolution', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Erosion Risk Evolution:"), " This timeline reveals how erosion risks have intensified ",
                        "over time across different regions. The area chart shows the cumulative impact while the line ",
                        "overlay highlights critical trend changes. Peak periods indicate when interventions are most needed."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                          'border-radius': '8px', 'margin-top': '10px'}
                )
            ]),
            
            # Visualization 2: Geographic Risk Distribution & Intensity Heatmap
            html.Div([
                get_graph('erosion-geographic-heatmap', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Geographic Risk Distribution:"), " The heatmap identifies erosion hotspots by country ",
                        "and erosion type. Darker colors indicate higher risk concentrations. The bubble overlay shows ",
                        "observation density, helping prioritize monitoring efforts in data-sparse high-risk areas."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                          'border-radius': '8px', 'margin-top': '10px'}
                )
            ]),
            
            # Visualization 3: Risk Level Distribution & Comparative Analysis
            html.Div([
                get_graph('erosion-risk-comparison', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Risk Level Analysis:"), " Compare erosion risk distributions across different ",
                        "categories and regions. The violin plots reveal risk concentration patterns while box plots ",
                        "show statistical spreads. This analysis helps identify which areas face the most variable ",
                        "and extreme erosion conditions."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                          'border-radius': '8px', 'margin-top': '10px'}
                )
            ])
        ]
    )
]