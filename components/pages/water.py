from dash import html, dcc
import json
from ..styles import TEXT_COLOR
from ..helpers.data_loader import load_data
from ..graph import get_graph
from ..card import get_card
from ..filters import get_country_filter, get_year_slider, get_water_filter, get_contamination_type_filter

def get_high_risk_countries_d3_viz(df, span=1):
    """
    Creates a D3.js visualization for high-risk countries KPI
    Shows an interactive bar chart with risk levels and detailed country information
    """
    return html.Div([
        html.H3("Normalized High-Risk Countries Analysis (using D3.js)", 
                style={
                    'color': TEXT_COLOR, 
                    'textAlign': 'center',
                    'marginBottom': '20px',
                    'fontSize': '18px',
                    'fontWeight': 'bold'
                }),
        
        # Container for the D3 visualization
        html.Div(id='d3-high-risk-countries', 
                style={
                    'width': '100%', 
                    'height': '500px',
                    'border': '1px solid rgba(255,255,255,0.1)',
                    'borderRadius': '8px',
                    'backgroundColor': 'rgba(255,255,255,0.02)',
                    'position': 'relative'
                }),
        
        # Data store for passing filtered data to D3
        dcc.Store(id='high-risk-countries-data'),
        
        # Hidden div for client-side callback output
        html.Div(id='d3-update-trigger', style={'display': 'none'}),
        
        # Legend and controls
        html.Div([
            html.Div([
                html.Span("Risk Level: ", style={'color': TEXT_COLOR, 'fontWeight': 'bold'}),
                html.Span("Severe (>50%)", style={'color': '#f94449', 'marginRight': '15px'}),
                html.Span("High (30-50%)", style={'color': '#fdac68', 'marginRight': '15px'}),
                html.Span("Moderate (15-30%)", style={'color': '#fae588', 'marginRight': '15px'}),
                html.Span("Low (<15%)", style={'color': '#b9ffaf'})
            ], style={'textAlign': 'center', 'marginTop': '10px'})
        ]),
        
    ], style={
        'gridColumn': f'span {span}',
        'backgroundColor': 'rgba(255,255,255,0.05)',
        'borderRadius': '8px',
        'padding': '20px'
    })


# Load the data
df = load_data()

water = [

    # Filter controls - Only 3 filters + year slider
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr 1fr',
            'grid-gap': '20px',
            'margin': '0px 0px'
        },
        children=[
            get_country_filter(df, 1),
            get_water_filter(df, 1),
            get_contamination_type_filter(1),
            get_year_slider(df, 3)  # Year slider spans all 3 columns
        ]
    ),

    # KPI cards with hover support - 4 cards
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr 1fr 1fr',
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },
        children=[
            get_card('kpi-high-contamination-countries', 'High Risk Countries', 1, '28px'),
            get_card('kpi-avg-contamination-rate', 'Average Contamination', 1, '28px'),
            get_card('kpi-total-water-abstraction', 'Total Water Use', 1, '28px'),
            get_card('kpi-worst-contamination-type', 'Worst Pollutant', 1, '28px'),
        ]
    ),

    # 4 advanced visualizations
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr',
            'grid-gap': '30px',
            'margin': '40px 0px 0px 0px'
        },
        children=[
            
            # Visualization 1: High-Risk Countries D3.js
            html.Div([
                get_high_risk_countries_d3_viz(df, 1),
                html.Div(
                    children=html.P([
                        html.Strong("Interactive High-Risk Countries Analysis: "), html.Br(),
                        "This D3.js interactive visualization displays water contamination rates normalized by agricultural land area using logarithmic scaling, revealing the true contamination intensity per hectare of farmland rather than absolute contamination levels. ",
                        "The normalization exposes Greece as having the most severe contamination intensity (57.5%) among countries with agricultural monitoring data, followed by Luxembourg and Canada showing nearly equivalent high-risk status around 49%. ",
                        "The color-coded risk classification shows that only Greece reaches the severe risk threshold (>50%, red), while five countries fall into the high-risk category (30-50%, orange), and the remaining countries demonstrate moderate contamination levels (15-30%, yellow) with none qualifying as low risk in this filtered dataset. ",
                        html.Br(), html.Br(),
                        "The interactive D3 implementation provides smooth animated transitions when filters change, allowing users to explore how different contamination types, water sources, and time periods affect country rankings in real-time. ",
                        "Hover interactions reveal detailed monitoring information including the number of surveillance sites and primary pollutant types, with summary statistics showing an average contamination rate of 23.5% across all displayed countries. ",
                        "This normalized approach fundamentally shifts the focus from countries with large agricultural sectors to those with intensive contamination per unit of farmland, indicating that targeted intervention strategies should prioritize agricultural systems with high contamination density rather than simply addressing countries with the highest absolute contamination volumes."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'margin-top': '10px', 'line-height': '1.5'}
                )
            ]),

            # Visualization 2: Dynamic Multi-Axis Trends with Abstraction Overlay
            html.Div([
                get_graph('water-trends-dual-axis', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Dual-Axis Temporal Analysis with Water Use Correlation:"), html.Br(),
                        "This visualization shows a concerning disconnect between agricultural water consumption patterns and contamination monitoring that exposes critical gaps in environmental governance over the past three decades. ",
                        "The dramatic spike in pesticide contamination detection around 2020 (reaching nearly 100%) coincides with relatively stable water abstraction levels, suggesting this surge reflects enhanced monitoring capabilities and stricter detection standards rather than a sudden environmental catastrophe - ",
                        "indicating that pesticide contamination was likely severely underreported in earlier decades. The persistence of phosphorus contamination at elevated levels (25-35%) throughout the 2000s and 2010s, ",
                        "despite fluctuating water usage patterns, points to legacy pollution from accumulated fertilizer applications that creates long-term groundwater contamination independent of current agricultural intensity.",
                        html.Br(), html.Br(),
                        " Most significantly, the relatively stable nitrate contamination levels (5-15%) against a backdrop of increasing water abstraction from the 1990s through 2015 suggest either effective nitrogen management practices were implemented or that nitrate monitoring protocols remained inadequate to capture the true extent of fertilizer-related contamination. ",
                        "The lack of clear correlation between water consumption peaks (mid-1990s, 2015) and immediate contamination spikes indicates that agricultural water pollution operates on delayed timescales, where current contamination rates reflect historical farming practices rather than present-day water usage, ",
                        "making this visualization a powerful reminder that today's agricultural decisions will determine water quality challenges for decades to come."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)',
                          'border-radius': '8px', 'margin-top': '10px', 'line-height': '1.5'}
                )
            ]),

            # Visualization 3: Water Quality vs Usage Correlation Analysis
            html.Div([
                get_graph('water-quality-usage-analysis', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Water Quality vs Usage Efficiency Analysis:"), html.Br(),
                        "The normalized intensity analysis reveals Luxembourg as having the highest contamination score (~22) despite minimal water usage, indicating extremely concentrated pollution per agricultural hectare that likely stems from intensive farming practices rather than excessive water consumption. ",
                        "Greece emerges as a critical case study with high contamination intensity (~15) paired with exceptionally high normalized water usage (approaching 2500 on the usage score), suggesting a dual crisis where both contamination density and water consumption efficiency require immediate intervention. ",
                        "Australia presents an interesting contrast with the highest normalized water usage score but relatively moderate contamination intensity (~5), indicating potential for optimization through improved water treatment and agricultural practices rather than usage reduction.",
                        html.Br(), html.Br(),
                        "The water source distribution reveals a critical infrastructure insight: 76.7% reliance on surface water versus 23.3% groundwater creates systemic vulnerability to agricultural runoff contamination across the monitored countries. ",
                        "Countries like Denmark, Czechia, and Finland demonstrate similar contamination intensity scores (8-10 range) despite varying water usage patterns, suggesting that contamination issues may be more closely linked to agricultural intensity and source water management than to consumption volume. ",
                        "This dual-axis analysis indicates that effective water quality improvement strategies must address both contamination intensity per hectare and usage efficiency simultaneously, with particular attention to surface water protection measures given the heavy reliance on this more vulnerable water source across agricultural systems."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'margin-top': '10px', 'line-height': '1.5'}
                )
            ])
        ]
    )
]