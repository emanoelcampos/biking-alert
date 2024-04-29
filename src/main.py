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


def process_email_data(email_data):
    day = datetime.strptime(email_data['day'][1], "%Y-%m-%d").strftime("%d/%m")

    hour_precipitation_list = []
    any_rainy = False

    for i in range(len(email_data['hour'])):
        hour = email_data['hour'][i]
        precipitation_probability = email_data['hourly_precipitation_probability'][i]
        if precipitation_probability > 0:
            any_rainy = True
        hour_and_precipitation = f'<div class="info"><div class="time">{hour}</div><div class="percentage">{precipitation_probability}%</div></div>'
        hour_precipitation_list.append(hour_and_precipitation)

    hour_and_precipitation = "".join(hour_precipitation_list)

    return {
        'day': day,
        'hour_and_percentage': hour_and_precipitation,
        'any_rainy': any_rainy
    }


def determine_icon(any_rainy):
    if any_rainy:
        return "../images/rainy.png"
    else:
        return "../images/sunny.png"


def format_email_content(data):
    with open("../src/templates/email_template.html", "r") as file:
        html_template = file.read()

    message_html = html_template.replace("{day}", data['day'])
    message_html = message_html.replace("{icon}", determine_icon(data['any_rainy']))
    message_html = message_html.replace("{hour_percentage}", data['hour_and_percentage'])

    return message_html


def save_html(message_html):
    with open("../src/templates/weather_forecast.html", 'w', encoding='utf-8') as file:
        file.write(message_html)
