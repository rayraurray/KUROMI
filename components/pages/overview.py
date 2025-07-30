from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..card import get_card
from ..graph import get_graph
from ..filters import get_category_filter, get_year_filter, get_year_slider,get_country_filter, get_unit_filter

df = load_data()

overview = [
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

    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },

        children=[
            # Summary Card
            get_card('total-indicators-display', "Total Indicators", 1, '32px'),
            get_card('total-countries', "Total Countries", 1, '32px'),
            get_card('avg-nutrient', "Average Nutrient Balance", 1, '32px'),
            get_card('percent-normal', "% Normal Observation Status", 1, '32px'),

            # Trend Chart
            get_graph('trend-chart', 2),
            html.Div(
                children=html.P([
                    html.Strong("Average Nutrient Balance Analysis: "), html.Br(),
                    "The chart titled Average Balance Over Time by Nutrient (1985–2023) visualizes the long-term trends of Nitrogen and Phosphorus nutrient balances. "
                    "Throughout most of the observed period, Nitrogen consistently maintains a much higher average balance than Phosphorus, indicating its dominant role in nutrient accumulation. "
                    "Nitrogen values exhibit periodic fluctuations but remain relatively stable between 1.8M to 2.4M units, with notable peaks around the late 1980s, early 2000s, and a sharp spike in 2020 approaching 2.9M. "
                    "This spike is followed by a dramatic drop in 2021 to below 1M, suggesting a possible anomaly, significant policy shift, or data reporting issue in those years.",
                    html.Br(), html.Br(),
                    "Phosphorus, on the other hand, shows a steadier and flatter trend with values mostly ranging from 0.3M to 0.45M units. Like Nitrogen, it also experiences a striking increase in 2020 reaching around 0.85M, "
                    "followed by a sharp decline to nearly 0.15M in 2021. The parallel patterns in both nutrients in recent years may indicate a common external influence, such as changes in agricultural practices, environmental regulations, "
                    "or data collection methods. Overall, while Nitrogen exhibits more volatility, both nutrients highlight significant deviations in 2020–2021 that warrant deeper investigation."
                ]),
                style={'padding': '10px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'grid-column': 'span 2'}
            ),
            # Line Chart
            html.Div([
                get_graph('race-chart', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Top 10 Countries Analysis: "), html.Br(),
                        "The bar chart shows the Top 10 Countries by Total Observations (1985–2023). "
                        "China leads significantly with over 11.8 billion total observations, "
                        "followed by the United States at around 10.3 billion. "
                        "The EU, India, and Brazil also show high observation totals, ranging between 4.5 and 6 billion.",
                        html.Br(), html.Br(),
                        "Other countries like Australia, Mexico, Russia, and Argentina contribute smaller but notable values,"
                        " between 1.5 and 3 billion. The presence of both “EU” and “European Union” suggests a possible duplication or inconsistency in labeling that may need to be cleaned."
                    ]),
                    style={'padding': '10px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                            'border-radius': '8px', 'grid-column': 'span 1', 'margin-top':'20px'}
                )
            ]),
            
            # Area Chart
            html.Div([
                get_graph('area-chart', 1),
                html.Div(
                    children=html.P([
                        html.Strong("Balance by Countries Analysis: "), html.Br(),
                        "The heatmap displays the total nutrient balance by country and year from 1985 to 2023. "
                        "Darker shades indicate higher balances, with Canada and Indonesia standing out due to consistently darker bands, "
                        "especially post-2000, suggesting sustained high nutrient activity.",
                        html.Br(), html.Br(),
                        "In contrast, many countries such as Latvia, Malta, and Estonia show lighter colors or gaps, reflecting lower or inconsistent data availability. "
                        "The variation across years and countries highlights uneven data reporting or differing agricultural practices over time."
                    ]),
                    style={'padding': '10px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'grid-column': 'span 1', 'margin-top':'20px'}
                )
            ])
        ]
    )
]