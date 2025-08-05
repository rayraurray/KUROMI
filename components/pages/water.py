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
        html.H3("High-Risk Countries Interactive Analysis", 
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
            html.Div([
                get_high_risk_countries_d3_viz(df, 1),
                html.Div(
                    children=html.P([
                        html.Strong("Interactive High-Risk Countries Analysis: "), html.Br(),
                        "This D3.js visualization provides an interactive bar chart of countries with contamination rates above 30%. ",
                        "Each bar is color-coded by risk level: red for severe (>50%), orange for high (30-50%), yellow for moderate (15-30%), and green for low (<15%). ",
                        "Hover over any bar to see detailed information including the specific contamination rate, number of monitoring sites, and the main pollutant type. ",
                        html.Br(), html.Br(),
                        "The visualization animates when filters change, providing smooth transitions that help track how different countries move in and out of high-risk categories. ",
                        "Countries are automatically sorted by contamination severity, with summary statistics displayed in the top-right corner showing average contamination rates and counts of severe vs high-risk countries. ",
                        "This interactive approach allows for deeper exploration of the data compared to static KPI cards, revealing patterns in agricultural water quality that require immediate attention and policy intervention."
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
                        "This visualization highlights a concerning inverse relationship between water contamination rates and usage patterns across the top 10 most contaminated countries. Norway stands out as an anomaly with the highest contamination rate (66%) but remarkably low water usage, ",
                        "suggesting that contamination issues may stem from intensive agricultural practices rather than volume-based inefficiencies. ",
                        "In contrast, Greece and Australia demonstrate high water consumption (normalized values of 94 and 100, respectively) with moderate contamination levels, indicating potential for optimization through improved water treatment infrastructure rather than usage reduction.",
                        html.Br(), html.Br(),
                        "The water source distribution (76.7% surface water vs. 23.3% groundwater) provides critical context for intervention strategies. Countries heavily reliant on surface water face greater contamination vulnerability from agricultural runoff, ",
                        "while the smaller groundwater fraction likely experiences concentrated pollution impacts. This distribution suggests that stakeholders should prioritize surface water protection measures and consider strategic shifts toward groundwater utilization where geologically feasible, ",
                        "particularly for countries such as France and Canada, showing moderate contamination despite significant usage. The visualization implies that water quality degradation is not simply a function of usage volume but rather reflects agricultural intensity, water source management, and treatment infrastructure effectiveness."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                          'border-radius': '8px', 'margin-top': '10px', 'line-height': '1.5'}
                )
            ])
        ]
    )
]