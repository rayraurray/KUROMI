from dash import html, dcc
from ..styles import TEXT_COLOR
from ..helpers.data_loader import load_data
from ..graph import get_graph
from ..card import get_card
from ..filters import get_country_filter, get_year_slider, get_water_filter, get_contamination_type_filter

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
    
    # 3 advanced visualizations
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr',
            'grid-gap': '30px',
            'margin': '40px 0px 0px 0px'
        },
        children=[
            # Visualization 1: Geographic Contamination Analysis
            html.Div([
                get_graph('water-contamination-geographic', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Geographic Water Contamination Analysis: "), html.Br(),
                        "This geographic visualization reveals a striking paradox where developed nations with strict environmental governance show the highest contamination detection rate, ",
                        "suggesting that water quality challenges may be more widespread globally than currently documented. ",
                        "The Flemish Region's alarming 65% contamination rate, alongside Norway and Greece's concerning levels above 55%, likely reflects their sophisticated monitoring networks capable of detecting pollution that remains invisible in countries with limited surveillance infrastructure.",
                        html.Br(), html.Br(),
                        "Notably, the clustering of high contamination rates among wealthy European nations and developed countries such as Canada (50%) and Australia (45%) points to the environmental costs of intensive agricultural practices combined with stringent monitoring standards that reveal the true extent of agricultural runoff impacts. ",
                        "The dramatically lower rates in countries such as Korea (18%), Netherlands (19%), and Austria (16%) may represent either genuinely superior agricultural water management practices or significant underreporting due to monitoring gaps. ",
                        "This visualization underscores the urgent need for global investment in water quality monitoring infrastructure, as the absence of data in many regions likely masks substantial contamination problems that could threaten both agricultural sustainability and public health - ",
                        "making the high-detection countries inadvertent early warning systems for worldwide agricultural pollution trends."
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