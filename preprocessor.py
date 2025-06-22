import pandas as pd



def preprocess(df,region_df):


    # Filter for Summer Olympics
    df = df[df['Season'] == 'Summer']

    # Drop 'region' and 'notes' if they already exist to avoid merge conflict
    for col in ['region', 'notes']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Merge with region_df
    df = df.merge(region_df, on='NOC', how='left')

    # Drop duplicate rows
    df.drop_duplicates(inplace=True)

    # Drop existing medal columns if already present
    for medal in ['Gold', 'Silver', 'Bronze']:
        if medal in df.columns:
            df.drop(columns=[medal], inplace=True)

    # One-hot encode medals
    medal_dummies = pd.get_dummies(df['Medal'])
    df = pd.concat([df, medal_dummies], axis=1)

    return df
