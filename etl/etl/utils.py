from bs4 import BeautifulSoup
import pandas as pd

def timestamp_to_date(timestamp):
    return pd.to_datetime(timestamp, unit='ms')

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text()

def extract_skill_names(skills_data):
    return [skill['name'] for skill in skills_data if 'name' in skill]

def convert_data(df, config):
    """
    Converts column data types in the dataframe according to the provided configuration.
    
    Args:
    df (pd.DataFrame): The dataframe to convert.
    config (dict): A dictionary where keys are column names and values are tuples
                   specifying the new data type or a function to apply to the column.
    
    Returns:
    pd.DataFrame: The dataframe with converted column types.
    """
    for column, operation in config.items():
        if callable(operation):
            # Apply a function if the operation is callable
            df[column] = df[column].apply(operation)
        else:
            # Change data type directly
            df[column] = df[column].astype(operation)
    
    return df
