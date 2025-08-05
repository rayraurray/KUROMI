from dash import html, dcc
from ..styles import BACKGROUND_COLOR, TEXT_COLOR, FONT_FAMILY, VIZ_COLOR
from ..helpers.data_loader import load_data
from ..card import get_card
from ..graph import get_graph
from ..filters import (
    get_category_filter, get_year_slider, get_country_filter,
    get_nutrients_filter, get_status_filter
)

df = load_data()

nutrients = [
    # ===========================
    # FILTER ROW
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
            get_nutrients_filter(df, 1),
            get_status_filter(df, 1),
            get_year_slider(df, 2),
        ]
    ),

    # ===========================
    # KPI CARDS
    # ===========================
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr 1fr',
            'grid-gap': '20px',
            'margin': '50px 0px 0px 0px'
        },
        children=[
            get_card('avg-nitrogen', "Avg Nitrogen Balance (Normalized)", 1, '32px'),
            get_card('avg-phosphorus', "Avg Phosphorus Balance (Normalized)", 1, '32px'),
        ]
    ),

    # ===========================
    # DUAL LINE CHART + EXPLANATION
    # ===========================
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr',
            'grid-gap': '20px',
            'margin': '40px 0px 0px 0px'
        },
        children=[
            get_graph('dual-line-chart', 1),
            html.Div(
                children=html.P([
                    html.Strong("Inputs/Outputs Analysis (Normalized): "), html.Br(),
                    "This chart shows normalized trends in nutrient inputs and outputs for Nitrogen and Phosphorus between 1985–2023. "
                    "Nitrogen inputs remain consistently higher than outputs, suggesting long-term nutrient surplus accumulation, "
                    "while Phosphorus tracks at lower magnitudes but follows similar patterns. "
                    "The sharp decline after 2020 likely reflects reporting or data collection issues rather than actual nutrient cessation."
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
        ]
    ),

    # ===========================
    # AVERAGE BALANCE BAR + EXPLANATION
    # ===========================
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr',
            'grid-gap': '20px',
            'margin': '40px 0px 0px 0px'
        },
        children=[
            get_graph('avg-balance-bar-chart', 1),
            html.Div(
                children=html.P([
                    html.Strong("Avg Nutrient Balance Analysis (Normalized): "), html.Br(),
                    "This bar chart displays normalized average nutrient balances per country. "
                    "Nitrogen shows the highest intensity in regions like China, India, and the US, while Phosphorus remains lower globally. "
                    "Negative balances in countries such as Kazakhstan or Latvia indicate nutrient depletion or efficient nutrient management."
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
        ]
    ),

    # ===========================
    # NITROGEN INPUT VS OUTPUT + EXPLANATION
    # ===========================
    html.Div(
        style={
            'display': 'grid',
            'grid-template-columns': '1fr',
            'grid-gap': '20px',
            'margin': '40px 0px 0px 0px'
        },
        children=[
            get_graph('scatter-nitrogen-input-output', 1),
            html.Div(
                children=html.P([
                    html.Strong("Nitrogen Input vs Output (Normalized): "), html.Br(),
                    "This scatter plot compares normalized nitrogen input vs output per country. "
                    "China and the US dominate both metrics, but inputs exceed outputs significantly, highlighting inefficiency. "
                    "Other countries cluster at lower scales, revealing disparities in nutrient use and efficiency across nations."
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
        ]
    ),

    # ===========================
    # D3 GROUPED BAR: INPUTS VS OUTPUTS
    # ===========================
    html.Div([
        html.H4("D3 Nutrient Inputs vs Outputs (Normalized)", style={'color': TEXT_COLOR}),
        dcc.Store(id="nutrients-d3-data"),
        html.Div(id="nutrients-d3-container", style={
            "border": "1px solid rgba(255,255,255,0.2)",
            "height": "400px",
            "backgroundColor": "rgba(255,255,255,0.02)",
            "borderRadius": "6px"
        }),
        html.Div(id='nutrients-d3-trigger', style={'display': 'none'}),
        html.Div(
            children=html.P([
                html.Strong("Interactive Inputs vs Outputs Analysis: "), html.Br(),
                "This grouped bar chart compares normalized nutrient inputs (blue) and outputs (red) by country. "
                "Countries with large gaps between inputs and outputs indicate nutrient surpluses and potential inefficiencies, "
                "while closer bars show better balance and efficiency."
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
    ], style={'margin-top': '40px'}),

]
