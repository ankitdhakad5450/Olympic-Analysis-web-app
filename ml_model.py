# ml_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

def prepare_ml_data(df):
    df = df[['Age', 'Height', 'Weight', 'Sex', 'Sport', 'region', 'Medal']]
    df = df.dropna(subset=['Age', 'Height', 'Weight', 'Sex', 'Sport', 'region'])
    df['Medal'] = df['Medal'].fillna('No Medal')
    df['Medal'] = df['Medal'].apply(lambda x: 0 if x == 'No Medal' else 1)
    df = pd.get_dummies(df, columns=['Sex', 'Sport', 'region'], drop_first=False)

    X = df.drop('Medal', axis=1)
    y = df['Medal']

    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

def train_model(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    return acc, cm

def predict_medal(model, input_df):
    return model.predict(input_df)

def predict_medal_proba(model, input_df):
    return model.predict_proba(input_df)[0][1]
