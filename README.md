# Cycling Weather Forecast

## Project Description
The Cycling Weather Forecast is a Python-based project designed to provide weather forecasts for bike training sessions. It fetches weather data from an API and processes it to determine the time of day and the percentage of rainfall. This information is then formatted into an email and sent to the user, providing them with a convenient and personalized weather forecast for their training sessions.

## Technologies Used

The project is developed using Python and utilizes several libraries and frameworks including:

- `os` for interacting with the operating system
- `datetime` for handling date and time data
- `smtplib` and `email.mime` for sending emails
- `selenium` for automating web browser interaction
- `dotenv` for managing environment variables
- `pandas` for data manipulation and analysis

## Lessons Learned

During the development of this project, several challenges were overcome and new skills were acquired. Working with APIs to fetch and process data provided valuable experience in handling JSON data and understanding how APIs work. Additionally, automating the process of sending emails with Python was a challenging but rewarding task that required a deep understanding of the SMTP protocol and MIME standards.  

## Usage

To use this project, follow these steps: 

1. Clone the repository to your local machine.
2. Install the required Python libraries by running `pip install -r requirements.txt`.
3. Set up your environment variables in a `.env` file. You will need to specify your latitude, longitude, and email credentials.
4. Run the main script with `python src/main.py`.