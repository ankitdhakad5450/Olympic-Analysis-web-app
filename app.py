# app.py
import streamlit as st
import pandas as pd
import preprocessor, helper, ml_model
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
from sklearn.metrics import accuracy_score, confusion_matrix

@st.cache_data
def load_data():
    df = pd.read_csv('athlete_events.csv')
    region_df = pd.read_csv('noc_regions.csv')
    return preprocessor.preprocess(df, region_df)

df = load_data()

@st.cache_resource
def load_model(df):
    X_train, X_test, y_train, y_test = ml_model.prepare_ml_data(df)
    model = ml_model.train_model(X_train, y_train)
    return model, X_train, X_test, y_train, y_test

model, X_train, X_test, y_train, y_test = load_model(df)

# App title
st.title("Olympics Data Analysis")
st.sidebar.title("Olympics Data Analysis")
st.sidebar.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTKUDQcxKK4OCk73VLDEJSfZP0YGMa_X4cULg&s')

# Sidebar selection
user_menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country wise Analysis', 'Athlete wise Analysis', 'Medal Prediction')
)

if user_menu == 'Medal Tally':
    st.sidebar.header('Medal Tally')
    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)
    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    elif selected_year != 'Overall' and selected_country == 'Overall':
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == 'Overall' and selected_country != 'Overall':
        st.title(f"{selected_country} Overall Performance")
    else:
        st.title(f"{selected_country} Performance in {selected_year} Olympics")
    st.dataframe(medal_tally)

elif user_menu == 'Overall Analysis':
    st.title("Top Statistics")
    editions = df['Year'].nunique() - 1
    cities = df['City'].nunique()
    sports = df['Sport'].nunique()
    events = df['Event'].nunique()
    athletes = df['Name'].nunique()
    nations = df['region'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Editions", editions)
    col2.metric("Hosts", cities)
    col3.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events", events)
    col2.metric("Nations", nations)
    col3.metric("Athletes", athletes)

    st.title("Participating Nations Over The Year")
    nations_over_time = helper.participating_nations_over_time(df)
    fig = px.line(nations_over_time, x="Edition", y="No of Countries")
    st.plotly_chart(fig)

    st.title("Events Over The Year")
    events_over_time = helper.events_over_time(df)
    fig = px.line(events_over_time, x="Edition", y="No of Events")
    st.plotly_chart(fig)

    st.title("Athletes Participation Over The Year")
    athletes_over_time = helper.athletes_over_time(df)
    fig = px.line(athletes_over_time, x="Edition", y="No of Athletes")
    st.plotly_chart(fig)

    st.title("No. of Events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    heatmap_data = x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0).astype(int)
    sns.heatmap(heatmap_data, annot=True, ax=ax)
    st.pyplot(fig)

    st.title("Most Successful Athletes")
    top_athletes = helper.most_successful(df, 'Overall').reset_index(drop=True)
    st.dataframe(top_athletes)

elif user_menu == 'Country wise Analysis':
    st.sidebar.header('Country wise Analysis')
    country_list = sorted(df['region'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox('Select a Country', country_list)

    st.title(f"{selected_country} Medal Tally over the years")
    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_df, x="Year", y="Medal")
    st.plotly_chart(fig)

    st.title(f"{selected_country} excels in the following sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    sns.heatmap(pt, annot=True, ax=ax)
    st.pyplot(fig)

    st.title(f"Top 10 athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df, selected_country)
    st.table(top10_df)

elif user_menu == 'Athlete wise Analysis':
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    st.title("Distribution of Age")
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()
    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist', 'Silver Medalist', 'Bronze Medalist'], show_hist=False, show_rug=False)
    st.plotly_chart(fig)

    st.title("Sport-wise Age Patterns of Gold Medalists")
    famous_sports = athlete_df['Sport'].value_counts().head(30).index.tolist()
    dist_data = [athlete_df[(athlete_df['Sport'] == sport) & (athlete_df['Medal'] == 'Gold')]['Age'].dropna() for sport in famous_sports]
    fig = ff.create_distplot(dist_data, famous_sports, show_hist=False, show_rug=False)
    st.plotly_chart(fig)

    st.title('Height Vs Weight Distribution')
    sport_list = sorted(df['Sport'].unique().tolist())
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    sns.scatterplot(data=temp_df, x='Weight', y='Height', hue='Medal', style='Sex', s=60, ax=ax)
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    st.plotly_chart(fig)

elif user_menu == 'Medal Prediction':
    st.title("\U0001F3AF Medal Prediction using ML")

    acc, cm = ml_model.evaluate_model(model, X_test, y_test)
    st.write(f"**Model Accuracy:** {acc * 100:.2f}%")
    st.write("**Confusion Matrix:**")
    st.write(cm)

    st.header("\U0001F52E Try Predicting")
    sports = sorted(df['Sport'].dropna().unique().tolist())
    countries = sorted(df['region'].dropna().unique().tolist())

    age = st.slider("Age", 10, 60, 25)
    height = st.slider("Height (cm)", 120, 230, 175)
    weight = st.slider("Weight (kg)", 30, 150, 70)
    sex = st.selectbox("Sex", ['M', 'F'])
    sport = st.selectbox("Sport", sports)
    country = st.selectbox("Country", countries)

    input_df = pd.DataFrame({
        'Age': [age],
        'Height': [height],
        'Weight': [weight],
        f'Sex_{sex}': [1],
        f'Sport_{sport}': [1],
        f'region_{country}': [1]
    })

    missing_cols = set(X_train.columns) - set(input_df.columns)
    default_df = pd.DataFrame(0, index=input_df.index, columns=list(missing_cols))
    input_df = pd.concat([input_df, default_df], axis=1)
    input_df = input_df[X_train.columns]

    proba = ml_model.predict_medal_proba(model, input_df)
    if proba > 0.5:
        st.success("\U0001F3C5 This athlete is likely to win a medal!")
    else:
        st.error("\u2639\ufe0f This athlete may not win a medal.")
    st.write(f"\U0001F522 Probability of winning a medal: {proba:.2f}")
