import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from dotenv import load_dotenv
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



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


def print_email():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    driver.set_window_size(800, 650)

    html_file_path = os.path.abspath("D:/python-projects/bike_weather/src/templates/weather_forecast.html")
    driver.get("file://" + html_file_path)

    WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[1]')))
    screenshot_path = "D:/python-projects/bike_weather/src/screenshots/forecast_screenshot.png"
    driver.save_screenshot(screenshot_path)
    driver.quit()

    return screenshot_path


def send_email(screenshot_path):
    load_dotenv()
    today = datetime.today().strftime('%d/%m')

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = os.environ['FROM']
    smtp_password = os.environ['PASSWORD']

    with open(screenshot_path, 'rb') as img_file:
        img_data = img_file.read()

    html_content = '''
    <html lang="pt-BR">
    <body>
        <img src="cid:image1">
    </body>
    </html>
    '''

    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = os.environ['TO']
    message['Subject'] = f'Weather Forecast - {today}'
    message.attach(MIMEText(html_content, 'html'))
    img = MIMEImage(img_data)
    img.add_header('Content-ID', '<image1>')

    img.add_header('Content-Disposition', 'attachment', filename='weather forecast')

    message.attach(img)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, message['To'], message.as_string())
        server.quit()


def main():
    load_dotenv()
    latitude = os.environ['LATITUDE']
    longitude = os.environ['LONGITUDE']
    base_url = 'https://api.open-meteo.com/v1/forecast'
    url = f'{base_url}?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation_probability&timezone=America%2FSao_Paulo&forecast_days=3'

    response_json = get_api_data(url)
    weather_dataframe = select_weather_data(response_json)
    training_days_dataframe = select_training_days_data(weather_dataframe)

    alert_day = determine_alert_day()
    alert_day_dataframe = get_alert_dataframe(training_days_dataframe, alert_day)
    email_data = format_email_data(alert_day_dataframe)

    processed_data = process_email_data(email_data)
    message_html = format_email_content(processed_data)
    save_html(message_html)
    screenshot_path = print_email()
    send_email(screenshot_path)


if __name__ == "__main__":
    main()
