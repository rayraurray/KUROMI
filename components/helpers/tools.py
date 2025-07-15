import textwrap

AGGREGATE_REGIONS = ['World', 'OECD', 'OECD Asia Oceania', 'OECD America', 'OECD Europe']
AGGREGATE_REGIONS_ALT = AGGREGATE_REGIONS + ['EU']

def apply_filters(
    df,
    selected_countries=None,
    year_range=None,
    selected_years=None,
    selected_nutrients=None,
    selected_units=None,
    selected_categories=None,
    selected_water_types=None,
    selected_erosion_levels=None,
    selected_status=None
):
    """
    Apply optional multi-select filters. Each selection list may contain 'All'.
    Only filters provided (not None) are applied.
    year_range is a tuple or list [start, end].
    """
    d = df.copy()

    # Year filter
    if year_range:
        start, end = year_range
        d = d[(d['year'] >= start) & (d['year'] <= end)]

    # Country filter
    if selected_years and 'All' not in selected_years:
        d = d[d['year'].isin(selected_years)]

    # Country filter
    if selected_countries and 'All' not in selected_countries:
        d = d[d['country'].isin(selected_countries)]

    # Nutrient filter
    if selected_nutrients and 'All' not in selected_nutrients:
        d = d[d['nutrients'].isin(selected_nutrients)]

    # Unit filter
    if selected_units and 'All' not in selected_units:
        d = d[d['measure_unit'].isin(selected_units)]

    # Measure category filter
    if selected_categories and 'All' not in selected_categories:
        d = d[d['measure_category'].isin(selected_categories)]

    # Water type filter
    if selected_water_types and 'All' not in selected_water_types:
        d = d[d['water_type'].isin(selected_water_types)]

    # Erosion risk level filter
    if selected_erosion_levels and 'All' not in selected_erosion_levels:
        d = d[d['erosion_risk_level'].isin(selected_erosion_levels)]

    if selected_status and 'All' not in selected_status:
        d= d[d['observation_status'].isin(selected_status)]

    return d

def remove_aggregates(df, map_view=False):
    df = df[~df.country.isin(AGGREGATE_REGIONS)]
    if map_view:
        df = df[~df.country.isin(AGGREGATE_REGIONS_ALT)]
    return df

def style_title(raw_title):
    return "<br>".join(textwrap.wrap(raw_title, width=85))