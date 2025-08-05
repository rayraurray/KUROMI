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


"""
Extract agricultural land area data from the dataset
Returns a dictionary mapping country to agricultural land area in thousands of hectares
"""
def get_agricultural_land_area_from_dataset(df):
    # Filter for agricultural land area data
    land_data = df[df['measure_category'] == 'Total agricultural land area'].copy()
    
    if land_data.empty:
        return {}
    
    # Get the latest year's data for each country
    latest_year = land_data['year'].max()
    latest_land_data = land_data[land_data['year'] == latest_year]
    
    # Create mapping - values are already in thousands of hectares
    country_land_mapping = {}
    for _, row in latest_land_data.iterrows():
        country_land_mapping[row['country']] = row['obs_value']
    
    return country_land_mapping


"""
Normalize values using logarithmic scaling to reduce extreme differences

Args:
    df: DataFrame with 'country' column to normalize
    source_df: The full dataset containing agricultural land area data
    value_column: Column to normalize

Returns:
    DataFrame with normalized column added
"""
def normalize_by_agricultural_land(df, source_df, value_column='obs_value'):
 
    import numpy as np
    
    # Get agricultural land area mapping from dataset
    land_mapping = get_agricultural_land_area_from_dataset(source_df)
    
    normalized_df = df.copy()
    new_column = f"{value_column}_log_normalized"
    
    # Initialize normalized column with original values
    normalized_df[new_column] = normalized_df[value_column]
    
    for country in df['country'].unique():
        if country in land_mapping:
            mask = df['country'] == country
            ag_land_1000ha = land_mapping[country]
            
            # Logarithmic normalization: contamination / log10(area + 1)
            # Adding 1 to prevent log(0) issues
            normalized_df.loc[mask, new_column] = (
                df.loc[mask, value_column] / np.log10(ag_land_1000ha + 1)
            )
    
    return normalized_df

