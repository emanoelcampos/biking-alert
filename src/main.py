import requests
import pandas as pd


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
