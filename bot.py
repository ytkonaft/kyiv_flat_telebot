import telebot
import requests
from config import TOKEN, URL
from constants import PRICE_FROM, PRICE_TO, ROOMS
from bs4 import BeautifulSoup as BS
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

store = {}

bot = telebot.TeleBot(TOKEN)

defaultUserState = {
  "step": 'init',
  "priceMin": 18000,
  "priceMax": 21000,
  "rooms": 3
}

@bot.message_handler(func=lambda message: True)
def echo(message):
  user_id = message.from_user.id
  user = store.get(user_id, dict(defaultUserState))
  store[user_id] = user
  stateMachine(message, store[user_id])




def stateMachine(message, user):
  text = message.text
  if text == '/go':
    sendResult(message, user)
  elif text == '/from':
    user['step'] = PRICE_FROM
    bot.send_message(message.chat.id, "Введите минимальную цену")
  elif text.startswith('/to'):
    user['step'] = PRICE_TO
    bot.send_message(message.chat.id, "Введите максимальную цену")
  elif text =='/rooms':
    user['step'] = ROOMS
    bot.send_message(message.chat.id, "Введите минимальную цену")
  elif user['step'] == PRICE_FROM:
    price = message.text.strip()
    user['priceMin'] = price
    bot.send_message(message.chat.id, f"Минимальная цена{price}")
  elif user['step'] == PRICE_TO:
    price = message.text.strip()
    user['priceMax'] = price
    bot.send_message(message.chat.id, f"Максимальная цена{price}")
  elif user['step'] == ROOMS:
    rooms = message.text.strip()
    user['rooms'] = rooms
    bot.send_message(message.chat.id, f"Установлено комнат {rooms}")
  else:
    bot.send_message(message.chat.id, getHelp())


def getHelp():
  return f"Available commands: \n" \
         f"/from \n" \
         f"/to \n" \
         f"/rooms \n" \
         f"/go \n"

def getParams(user):
  return {
  'search[filter_float_number_of_rooms:from]': user["rooms"],
  'search[filter_float_price:from]': user["priceMin"],
  'search[filter_float_price:to]': user["priceMax"],
  'search[order]': 'created_at'
 }

def gen_markup(url):
  markup = InlineKeyboardMarkup()
  markup.add(InlineKeyboardButton("See", url=url))
  return markup

def sendResult(message, user):
  r = requests.get(URL, getParams(user))
  html = BS(r.content, 'html.parser')
  for el in html.select('.offers .offer-wrapper'):
    title = el.select('h3 strong')[0]
    price = el.select('.price strong')[0]
    time = el.select('.space.rel .breadcrumb:last-child span')[0]
    link = el.select('.thumb')[0]
    image = el.select('.thumb img')[0]
    image_url = image['src']
    textMessage = f"{image_url} \n {title.text} \n {price.text} \n {time.text} \n "
    bot.send_message(message.chat.id, textMessage, reply_markup=gen_markup(link['href']))



bot.polling()

