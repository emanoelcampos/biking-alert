import requests
import pandas as pd
from datetime import datetime, timedelta


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


def determine_alert_day():
    today = datetime.now()
    if today.weekday() in [0, 2, 4]:
        return today


def get_alert_dataframe(training_days_dataframe, alert_day):
    if alert_day:
        training_day = (alert_day + timedelta(days=1)).strftime('%Y-%m-%d')
        alert_day_dataframe = training_days_dataframe[training_days_dataframe['date'].str.contains(training_day)]
        alert_day_dataframe = alert_day_dataframe.sort_values(by='hourly_precipitation_probability',
                                                              ascending=False).head(3)
        return alert_day_dataframe


def format_email_data(alert_day_dataframe):
    email_data = {
        'day': [],
        'hour': [],
        'hourly_precipitation_probability': []
    }

    for index, row in alert_day_dataframe.iterrows():
        day = row['date'][:10]
        hour = row['date'][11:]
        hourly_precipitation_probability = row['hourly_precipitation_probability']
        email_data['day'].append(day)
        email_data['hour'].append(hour)
        email_data['hourly_precipitation_probability'].append(hourly_precipitation_probability)

    return email_data
