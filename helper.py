import numpy as np
import pandas as pd

# Returns list of years and countries with 'Overall' option at the top
def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    countries = df['region'].dropna().unique().tolist()
    countries.sort()
    countries.insert(0, 'Overall')

    return years, countries

# Computes medal tally based on year and country filters
def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
        flag = 0
    elif year == 'Overall':
        temp_df = medal_df[medal_df['region'] == country]
        flag = 1
    elif country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
        flag = 0
    else:
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]
        flag = 0

    if flag == 1:
        x = temp_df.groupby('Year')[['Gold', 'Silver', 'Bronze']].sum().sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region')[['Gold', 'Silver', 'Bronze']].sum().sort_values('Gold', ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
    return x

# Time series: countries participating over the years
def participating_nations_over_time(df):
    nations_over_time = df.drop_duplicates(['Year', 'region'])['Year'].value_counts().reset_index()
    nations_over_time.columns = ['Edition', 'No of Countries']
    return nations_over_time.sort_values('Edition')

# Time series: number of events over the years
def events_over_time(df):
    events_over_time = df.drop_duplicates(['Year', 'Event'])['Year'].value_counts().reset_index()
    events_over_time.columns = ['Edition', 'No of Events']
    return events_over_time.sort_values('Edition')

# Time series: number of athletes over the years
def athletes_over_time(df):
    athletes_over_time = df.drop_duplicates(['Year', 'Name'])['Year'].value_counts().reset_index()
    athletes_over_time.columns = ['Edition', 'No of Athletes']
    return athletes_over_time.sort_values('Edition')

# Top 15 most successful athletes globally or by sport
def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    top_athletes = temp_df['Name'].value_counts().reset_index().head(15)
    top_athletes.columns = ['Name', 'Medals']

    merged_df = top_athletes.merge(df, on='Name', how='left')
    return merged_df[['Name', 'Medals', 'Sport', 'region']].drop_duplicates('Name')

# Year-wise medal tally for a country
def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    temp_df = temp_df[temp_df['region'] == country]
    temp_df = temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    medals_by_year = temp_df.groupby('Year').count()['Medal'].reset_index()
    return medals_by_year

# Heatmap of sports vs years showing medal counts for a country
def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    temp_df = temp_df[temp_df['region'] == country]
    temp_df = temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    pt = temp_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt

# Top 10 medal-winning athletes of a selected country
def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    top_athletes = temp_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Name', 'Medals']

    merged_df = top_athletes.merge(df, on='Name', how='left')
    return merged_df[['Name', 'Medals', 'Sport']].drop_duplicates('Name').reset_index(drop=True)

# Returns data for scatter plot: height vs weight for a sport
def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region']).copy()
    athlete_df['Medal'] = athlete_df['Medal'].fillna('No Medal')

    if sport != 'Overall':
        return athlete_df[athlete_df['Sport'] == sport]
    return athlete_df

# Returns year-wise male vs female participation counts
def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)

    return final
