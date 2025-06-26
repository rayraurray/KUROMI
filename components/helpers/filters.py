import textwrap

AGGREGATE_REGIONS = ['World', 'OECD', 'OECD Asia Oceania', 'OECD America', 'OECD Europe']
AGGREGATE_REGIONS_ALT = AGGREGATE_REGIONS + ['EU']

def apply_filters(df, category, year_range):
    d = df[df['measure_category'] == category] if category != 'All' else df
    start, end = year_range
    return d[(d.year >= start) & (d.year <= end)]

def remove_aggregates(df, map_view=False):
    df = df[~df.country.isin(AGGREGATE_REGIONS)]
    if map_view:
        df = df[~df.country.isin(AGGREGATE_REGIONS_ALT)]
    return df

def style_title(raw_title):
    return "<br>".join(textwrap.wrap(raw_title, width=85))