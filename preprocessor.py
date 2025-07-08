import pandas as pd

def preprocess(df, region_df):
    """
    Preprocesses Olympic dataset by:
    - Filtering only Summer Olympics
    - Merging NOC codes with region info
    - Dropping duplicates and unnecessary columns
    - One-hot encoding medals
    """

    # 1. Filter for Summer Olympics only
    df = df[df['Season'] == 'Summer'].copy()

    # 2. Drop existing 'region' and 'notes' columns (if exist)
    df.drop(columns=[col for col in ['region', 'notes'] if col in df.columns], inplace=True)

    # 3. Merge with NOC region dataframe
    df = df.merge(region_df, on='NOC', how='left')

    # 4. Drop duplicate records
    df.drop_duplicates(inplace=True)

    # 5. Drop old medal count columns if they exist (in case they were previously processed)
    df.drop(columns=[col for col in ['Gold', 'Silver', 'Bronze'] if col in df.columns], inplace=True)

    # 6. One-hot encode the 'Medal' column into individual columns: 'Gold', 'Silver', 'Bronze'
    medal_dummies = pd.get_dummies(df['Medal'])  # NaN values ignored
    df = pd.concat([df, medal_dummies], axis=1)

    return df
