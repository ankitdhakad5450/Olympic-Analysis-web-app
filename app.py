import streamlit as st
import pandas as pd
import preprocessor,helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff


df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')

# Load the preprocessed data
df = preprocessor.preprocess(df,region_df)

# App title
st.title("Olympics Data Analysis")
st.sidebar.title("Olympics Data Analysis")
st.sidebar.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTKUDQcxKK4OCk73VLDEJSfZP0YGMa_X4cULg&s')
# Sidebar selection
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country wise Analysis', 'Athlete wise Analysis')
)


st.dataframe(df)

if user_menu == 'Medal Tally':
    st.sidebar.header('Medal Tally')

    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally =  helper.fetch_medal_tally(df, selected_year, selected_country)
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title(" Medal Tally in " + str(selected_year) + " Olympics ")
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " Overall performance ")
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics ")
    st.dataframe(medal_tally)

if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.participating_nations_over_time(df)
    fig = px.line(nations_over_time, x="Edition", y="No of Countries")
    st.title("Participating Nations Over The Year")
    st.plotly_chart(fig)

    events_over_time = helper.events_over_time(df)
    fig = px.line(events_over_time, x="Edition", y="No of Events")
    st.title("Events Over The Year")
    st.plotly_chart(fig)

    athletes_over_time = helper.athletes_over_time(df)
    fig = px.line(athletes_over_time, x="Edition", y="No of Athletes")
    st.title("Athletes Participation Over The Year")
    st.plotly_chart(fig)

    st.title("No. of Events over time(Every Sport)")
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    axis = sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype('int'),
                annot=True)
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    sport = 'Overall'
    top_athletes = helper.most_successful(df, sport)
    top_athletes = top_athletes.reset_index(drop=True)
    st.dataframe(top_athletes)

if user_menu == 'Country wise Analysis':

    st.sidebar.title('Country wise Analysis')

    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    country_df = helper.yearwise_medal_tally(df,selected_country)
    fig = px.line(country_df, x="Year", y="Medal")
    st.title(selected_country + " Medal Tally over the years ")
    st.plotly_chart(fig)

    st.title(selected_country + " excels in the following sports")
    pt = helper.country_event_heatmap(df,selected_country)
    fig, ax = plt.subplots(figsize=(20,20))
    axis = sns.heatmap(pt,annot=True)
    st.pyplot(fig)

    st.title("Top 10 athletes of " + selected_country)
    top10_df = helper.most_successful_countrywise(df, selected_country)
    st.table(top10_df)

if user_menu == 'Athlete wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'],show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    # Get top 30 most popular sports by medal count
    famous_sports = athlete_df['Sport'].value_counts().head(30).index.tolist()

    x = []
    name = []

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
        name.append(sport)

    # Plot age distribution
    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(width=1000, height=600)
    st.title("Sport-wise Age Patterns of Gold Medalists")
    st.plotly_chart(fig)

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height Vs Weight Distribution')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    axis = sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'],s=60)
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")

    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(width=1000, height=600)
    st.plotly_chart(fig)























