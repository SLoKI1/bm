from telebot import telebot,types
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['id'])
def id(message):
    bot.send_message(message.chat.id,message.from_user.id)
    
# @bot.message_handler(commands=['idmsg'])
# def id(message):
#     bot.send_message(message.chat.id,message.message_id)
    
    
# @bot.message_handler(content_types=['photo'])
# def detect_product(message):
#     bot.send_message(message.chat.id,message.forward_from_chat.id)


bot.polling(none_stop=True)