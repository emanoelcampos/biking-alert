import requests
import pandas as pd
from _datetime import datetime


def get_api_data(url):
    response = requests.get(url)
    return response.json()


def select_weather_data(data):
    df_date = pd.DataFrame(data['hourly']['time'], columns=['date'])
    df_precipitation = pd.DataFrame(data['hourly']['precipitation_probability'],
                                    columns=['hourly_precipitation_probability'])
    df_temperature = pd.DataFrame(data['hourly']['temperature_2m'], columns=['hourly_temperature_2m'])

    weather_dataframe = pd.concat([df_date, df_temperature, df_precipitation], axis=1)

    return weather_dataframe


def select_training_days_data(weather_dataframe):
    weather_dataframe['day_of_week'] = weather_dataframe['date'].apply(
        lambda x: datetime.strptime(x[:10], "%Y-%m-%d").strftime('%A'))

    training_days_dataframe = weather_dataframe[
        weather_dataframe['day_of_week'].isin(['Tuesday', 'Thursday', 'Saturday'])]

    return training_days_dataframe
