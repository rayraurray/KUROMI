from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..card import get_card
from ..graph import get_graph
from ..filters import get_category_filter, get_year_filter, get_year_slider,get_country_filter, get_unit_filter, get_nutrients_filter, get_status_filter

df = load_data()

nutrients = [
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
            get_nutrients_filter(df,1),
            get_status_filter(df,1),
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
            get_card('avg-nitrogen', "Average Nitrogen Balance", 1, '32px'),
            get_card('avg-phosphorus', "Average Phosphorus Balance", 1, '32px'),

            # Trend Chart
            get_graph('dual-line-chart', 2),
            html.Div(
                children=html.P([
                    html.Strong("Inputs/Outputs Analysis: "), html.Br(),
                    "This line chart illustrates the trends in nutrient inputs and outputs for both Nitrogen and Phosphorus from 1985 to 2023. Nitrogen inputs (in blue) are consistently the highest, starting around 130M and gradually increasing to a peak of nearly 290M around 2015. "
                    "Nitrogen outputs (in red) follow a similar upward trend, though consistently lower than inputs, indicating a long-term surplus of nitrogen in the system. This surplus suggests an accumulation of nitrogen in soils, potentially contributing to environmental issues like eutrophication.",
                    html.Br(), html.Br(),
                    "Phosphorus inputs (green) and outputs (purple) show a more modest scale, ranging between 20M and 45M for inputs, and 10M to 30M for outputs. The values rise steadily through the early 2000s and plateau slightly before 2015. All four curves experience a steep decline after 2020, with values dropping to near zero by 2023. "
                    "This sudden drop across all variables likely reflects a disruption in data collection, reporting practices, or availability rather than an actual global halt in nutrient use. The chart highlights the consistent nutrient imbalance over time, particularly for nitrogen, and raises questions about the completeness of recent data."
                ]),
                style={'padding': '10px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'grid-column': 'span 2'}
            ),

            # Area Chart
            get_graph('avg-balance-bar-chart', 2),
            html.Div(
                children=html.P([
                    html.Strong("Average Nutrient Balance Analysis: "), html.Br(),
                    "This bar chart displays the average nutrient balance per country for Nitrogen (blue) and Phosphorus (red). Nitrogen shows significantly higher average values than Phosphorus across almost all countries. "
                    "Notable peaks in nitrogen balance are observed in China, India, and the United States, each exceeding 15M or even 20M in average balance, indicating intensive nutrient usage or accumulation in these regions.",
                    html.Br(), html.Br(),
                    "Phosphorus levels remain comparatively low, rarely exceeding 5M, and follow similar patterns of distribution, though with smaller magnitudes. Some countries such as Kazakhstan and Latvia show negative average balances for nitrogen, "
                    "suggesting more output than input—potentially due to soil depletion or better nutrient efficiency. Overall, the chart highlights global disparities in nutrient management, with a few countries driving the bulk of nutrient surpluses."
                ]),
                style={'padding': '10px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'grid-column': 'span 2'}
            ),

            # Line Chart
            get_graph('scatter-nitrogen-input-output', 2),
            html.Div(
                children=html.P([
                    html.Strong("Nitrogen Input vs. Output Analysis: "), html.Br(),
                    "This scatter plot compares Nitrogen Input vs. Output by Country. Each point represents a country, showing how much nitrogen is applied (input) versus how much is removed or utilized (output). "
                    "The chart highlights China and the United States as having the highest nitrogen activity, with China leading both in input (~1.6B) and output (~820M), indicating a large surplus and potentially inefficient nitrogen use.",
                    html.Br(), html.Br(),
                    "Most other countries cluster at the lower end of the scale, indicating much smaller nitrogen usage. Some countries like India and the European Union show relatively high inputs but lower outputs, suggesting nutrient imbalances or losses. "
                    "Overall, the chart reveals significant disparities in nitrogen efficiency across nations, with some countries potentially overapplying nitrogen relative to agricultural uptake."
                ]),
                style={'padding': '10px', 'color': TEXT_COLOR, 'background-color': 'rgba(255,255,255,0.05)', 
                        'border-radius': '8px', 'grid-column': 'span 2'}
            ),
        ]
    )
]