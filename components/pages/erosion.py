from dash import html
from ..styles import TEXT_COLOR
from ..helpers.data_loader import load_data
from ..graph import get_graph
from ..card import get_card
from ..filters import get_country_filter, get_erosion_filter, get_year_slider, get_erosion_type_filter_fixed

# Load the data
df = load_data()

erosion = [
    # Filter controls with fixed erosion type filter
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
            get_erosion_type_filter_fixed(df, 1),
            get_year_slider(df, 3)
        ]
    ),
    
    # KPI cards with hover support
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr 1fr 1fr',
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },
        children=[
            get_card('kpi-total-observations', 'Total Observations', 1, '28px'),
            get_card('kpi-land-at-risk', 'Agricultural Land at Risk', 1, '28px'),
            get_card('kpi-severe-risk-percent', 'Severe Risk %', 1, '28px'),
            get_card('kpi-high-risk-countries', 'High-Risk Countries', 1, '28px'),
        ]
    ),
    
    # 3 visualizations
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
                        html.Strong("Erosion Risk Evolution Analysis: "), html.Br(),
                        "The most significant trend shows that erosion risks follow distinct cycles, rather than simply worsening over time, ",
                        "with major peaks around 2001 and 2013 (reaching ~45+ units), which likely correspond to extreme weather events and economic pressures on farming practices. ",
                        "The volatility pattern reveals that erosion became more predictable during 2005-2010 when commodity prices were high and farmers invested more in soil conservation. ",
                        "Still, uncertainty increased dramatically after 2010 as climate variability intensified. ",
                        html.Br(), html.Br(),
                        "Critically, wind and water erosion now behave as separate threats rather than seasonal variations of the same problem - ",
                        "wind erosion spikes during drought periods when crops can't protect soil, ",
                        "while water erosion peaks during intense rainfall events that overwhelm degraded soils. ",
                        "This means the farms are becoming vulnerable to both too little and too much water simultaneously, requiring dual protection strategies that address soil structure, crop cover, and water management together rather than treating each erosion type independently."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                          'border-radius': '8px', 'margin-top': '10px', 'line-height': '1.5'}
                )
            ]),
            
            # Visualization 2: NORMALIZED Geographic Risk Distribution Matrix
            html.Div([
                get_graph('erosion-geographic-matrix', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Normalized Geographic Risk Distribution Analysis:"), html.Br(),
                        "The agricultural land normalization reveals a striking reversal in erosion risk priorities that challenges conventional assumptions about which countries face the most severe soil degradation per hectare of farmland. ",
                        "Malta emerges as having the highest normalized erosion intensity, followed by Slovenia and Denmark, indicating that smaller European countries with intensive agricultural practices face disproportionately severe erosion pressure relative to their limited agricultural land base. ",
                        "This pattern suggests that high-density farming systems in constrained agricultural areas create concentrated soil vulnerability that was previously masked when looking at absolute erosion totals.",
                        html.Br(), html.Br(),
                        "The heatmap exposes a critical water erosion crisis in the smaller agricultural economies - Malta, Slovenia, and Denmark show severe normalized water erosion intensities (dark red coloring), ",
                        "while larger agricultural nations like Canada and Australia, despite having significant absolute erosion, show more moderate per-hectare intensity. ",
                        "Notably, wind erosion appears to be a more specialized threat, with Netherlands and Denmark showing the highest normalized wind erosion intensity, ",
                        "suggesting that specific geographic and agricultural conditions in these densely farmed regions create optimal conditions for wind-driven soil loss.",
                        html.Br(), html.Br(),
                        "The continental bubble analysis reveals that Europe, despite having extensive monitoring coverage (100+ observations), shows moderate normalized intensity, ",
                        "indicating effective erosion management relative to agricultural density, while Asia and Oceania demonstrate higher per-hectare erosion intensity with fewer monitoring points. ",
                        "This creates a concerning surveillance gap where regions with high agricultural intensity may be experiencing severe per-hectare erosion without adequate monitoring. ",
                        "For policy makers, this analysis indicates that erosion prevention strategies should prioritize intensive support for small-scale, high-density agricultural systems ",
                        "rather than focusing solely on countries with the largest absolute erosion totals, as the per-hectare impact reveals where agricultural sustainability is most critically threatened."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'margin-top': '10px', 'line-height': '1.5'}
                )
            ]),
            
            # Visualization 3: Risk Pattern Analysis
            html.Div([
                get_graph('erosion-risk-patterns', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Erosion Risk Pattern Analysis:"), html.Br(),
                        "This matrix shows how different types of erosion compare across risk levels, revealing important patterns for agricultural planning. ",
                        "Water erosion clearly dominates the monitoring data with 325 total observations compared to 113 for wind erosion, which means most of our erosion knowledge comes from water-related soil loss events. ",
                        "The data reveals that moderate-risk water erosion is our most common challenge (112 cases), suggesting this should be where we focus most of the prevention efforts since these situations are manageable before they become critical. ",
                        html.Br(), html.Br(),
                        "However, a concerning pattern emerges at the severe risk level where wind erosion, despite having fewer total observations, shows proportionally similar severe cases (12 for wind vs. 50 for water), indicating that when wind erosion does occur, it can quickly become as dangerous as water erosion, ",
                        "For agricultural decision-makers, this means that while water erosion requires ongoing attention due to its frequency, wind erosion demands equally serious prevention measures because it can escalate rapidly to severe levels (50 cases each for both types) suggests that early intervention works equally well for both erosion types, ",
                        "emphasizing the importance of proactive soil management that addresses both water retention and wind protection through integrated practices such as cover cropping, windbreaks, and proper tillage timing."
                    ]),
                    style={'padding': '15px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                          'border-radius': '8px', 'margin-top': '10px', 'line-height': '1.5'}
                )
            ])
        ]
    )
]