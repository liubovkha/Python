from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import credentials
import requests
import datetime

TOKEN = f"{credentials.TOKEN}"
API_KEY = f"{credentials.WEATHER_API_KEY}"

TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
DAY_AFTER_TOMORROW = TODAY + datetime.timedelta(days=2)

CITY_NAME_TO_CHOOSE = {
    "London": "London,UK",
    "Paris": "Paris,France",
    "Helsinki": "Helsinki,Finland"
}

DATE_TO_CHOOSE = {
    "Today": f"{TODAY}",
    "Tomorrow": f"{TOMORROW}",
    "The day after tomorrow": f"{DAY_AFTER_TOMORROW}"
}

user_city_map = {}

bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=3)
    for city_name in CITY_NAME_TO_CHOOSE.keys():
        item_button = KeyboardButton(city_name)
        markup.add(item_button)
    bot.send_message(message.chat.id, "Where are you?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in CITY_NAME_TO_CHOOSE.keys())
def send_date_choice(message):
    user_id = message.from_user.id
    user_city_map[user_id] = CITY_NAME_TO_CHOOSE[message.text]

    markup = ReplyKeyboardMarkup(row_width=3)
    for weather_date in DATE_TO_CHOOSE.keys():
        item_button = KeyboardButton(weather_date)
        markup.add(item_button)
    bot.send_message(message.chat.id, "When do you plan to go outside?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in DATE_TO_CHOOSE.keys())
def send_advice(message):
    user_id = message.from_user.id
    city = user_city_map.get(user_id)

    weather_date = message.text
    date = DATE_TO_CHOOSE[weather_date]
    weather, description = get_weather_by_hours_for_day_from_api(date=date, city=city)
    bot.send_message(message.chat.id, text=f"{description}")

def get_weather_by_hours_for_day_from_api(*, date: str, city: str) -> list[dict]:
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/{date}/{date}?key={API_KEY}"
    response = requests.get(url)
    weather_by_days = response.json()["days"]
    weather_description = response.json()["description"]
    print(weather_by_days)
    return weather_by_days, weather_description


bot.infinity_polling()