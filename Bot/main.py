import sqlite3
from telebot import telebot,types
from config import TOKEN,IDCHANL,TEXT,IDAUROR,LINKCHANL,TGSUPPORT,IDTGSUPPURT

bot = telebot.TeleBot(TOKEN)

def db_execute(db_ex):
    connection = sqlite3.connect('mydatabase.sqlite3')
    cursor = connection.cursor()
    cursor.execute(db_ex)   
    connection.commit()
    connection.close()

# детект заказа  --------------------------------------------------------------------------------------------------------------    
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.forward_from:
        if message.forward_from.id == IDTGSUPPURT:
            bot.send_message(message.chat.id,"Записал интересующий вас товар.")
            db_execute(f"UPDATE users SET product = '{message.caption}' WHERE id_users = {message.from_user.id}")  
        else:
            bot.reply_to(message,"Это не от нас.")
    elif message.forward_from_chat:
        if message.forward_origin.chat.id == IDCHANL:
            bot.send_message(message.chat.id,"Записал интересующий вас товар.")
            db_execute(f"UPDATE users SET product = '{message.caption}' WHERE id_users = {message.from_user.id}")  
        else:
            bot.reply_to(message,"Это не от нас.")
    else:
        bot.send_message(IDAUROR,f"Поступило фото от {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} {message.from_user.id} ")
        bot.forward_message(chat_id=IDAUROR, from_chat_id=message.chat.id, message_id=message.message_id)
        
# Запись ФИО пользователя --------------------------------------------------АМ------------------------------------------------------------
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Да, я соглашаюсь с соглашением")
    btn2 = types.KeyboardButton("Нет, я отказываюсь")
    markup.add(btn1, btn2)
    mesg = bot.send_message(message.chat.id, "Ознакомтесь !", reply_markup=markup )
    bot.send_message(message.chat.id, TEXT)
    bot.register_next_step_handler(mesg,start_text) 
    
def start_text(message):
    if message.text == "Да, я соглашаюсь с соглашением":
        bot.reply_to(message, "Вы согласились",reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(message.chat.id,f"Теперь все хорошо, выберите товар из [канала]({LINKCHANL}) и кнопкой 'Переслать' отправте сюда. [Канал]({LINKCHANL}) ", parse_mode='Markdown')
        db_execute(f'INSERT INTO users (id_users) SELECT {message.from_user.id} WHERE NOT EXISTS (SELECT 1 FROM users WHERE id_users = {message.from_user.id})')
    elif message.text == "Нет, я отказываюсь":
        bot.reply_to(message, "Вы отказываюсь от соглашения. Если передумаете напишите. [ /start ]",reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.reply_to(message, "Надо нажать на одну из кнопок которые вам предлогали. Перезапустите команду [ /start ]",reply_markup=types.ReplyKeyboardRemove())

# Запись ФИО пользователя --------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=["fio"])
def fio(message):
    mesg = bot.send_message(message.chat.id,"Напишите ваше ФИО. В одном сообщении.")
    bot.register_next_step_handler(mesg,fio_text) 
    
def fio_text(message):
    bot.send_message(message.chat.id,"Записал ваше ФИО. \n/adress - Туда записывать Адрес куда отправлять товар \n/comment - Комментарий для заказа если требуется. типа \n(Заверните в подарочную упаковку). Информация о заказе [ /buy ]")
    if message.text != None:
        db_execute(f"UPDATE users SET fio = '{message.text}' WHERE id_users = {message.from_user.id}")
    else:
        print("fio_text")

# Запись Адресса пользователя --------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['adress'])
def enter_adress(message):
    mesg = bot.send_message(message.chat.id,"Напишите Страну,республики, края, области, автономного округа (области),района, населенного пункта (города, поселка и т.п.),улицы, номер дома, номер квартиры | или отправте ссылку на ваш дом с квартирой в https://yandex.ru/maps или https://www.google.ru/maps формат ссылка кв.-- . В одном сообщении.")
    bot.register_next_step_handler(mesg,enter_adress_text) 
    
def enter_adress_text(message):
    bot.send_message(message.chat.id,"Записал ваш адресс. \n/fio - туда писать ФИО \n/comment - Комментарий для заказа если требуется. типа \n(Заверните в подарочную упаковку). Информация о заказе [ /buy ] ")
    db_execute(f"UPDATE users SET adress = '{message.text}' WHERE id_users = {message.from_user.id}")

# Запись комментария пользователя --------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['comment'])
def com(message):
    mesg = bot.send_message(message.chat.id,"Напишите комментакий к заказу. Ели его нет то напишите [ - ]")
    bot.register_next_step_handler(mesg,com_text) 

def com_text(message):
    bot.reply_to(message,"Записал ваш комментакий. \n/fio - туда писать ФИО \n/adress - Туда записывать Адрес куда отправлять товар. Информация о заказе [ /buy ] ")
    db_execute(f"UPDATE users SET comment = '{message.text}' WHERE id_users = {message.from_user.id}")

# Запись покупки пользователя --------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['buy','start'])
def buy(message):
    connection = sqlite3.connect('mydatabase.sqlite3')
    cursor = connection.cursor()
    cursor.execute(f'SELECT iif( "id_users" = {message.from_user.id}, "True", "False" ) FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
    relult_start = cursor.fetchone()
    if relult_start == None:
        start(message)
        bot.send_message(message.chat.id,"/fio - туда писать ФИО \n/adress - Туда записывать Адрес куда отправлять товар \n/comment - Комментарий для заказа если требуется. типа \n(Заверните в подарочную упаковку)")
    elif relult_start[0] == "True":
        cursor.execute(f'SELECT fio FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_fio = cursor.fetchone()
        if relult_fio[0] != None:
            bot.send_message(message.chat.id,f"ФИО : {relult_fio[0]}")
        elif relult_fio[0] == None:
            bot.send_message(message.chat.id,f"Запишите ваше ФИО. [ /fio ]")
        else:
            print('buy_relult_fio')
            
        cursor.execute(f'SELECT adress FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_adress = cursor.fetchone()
        if relult_adress[0] != None:
            bot.send_message(message.chat.id,f"Адресс : {relult_adress[0]}")
        elif relult_adress[0] == None:
            bot.send_message(message.chat.id,f"Запишите ваш Адресс. [ /adress ]")
        else:
            print('buy_relult_adress')

        cursor.execute(f'SELECT comment FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_comment = cursor.fetchone()
        if relult_comment[0] != None:
            bot.send_message(message.chat.id,f"Комментарий : {relult_comment[0]}")
        elif relult_comment[0] == None:
            bot.send_message(message.chat.id,f"Запишите ваш комментарий если он требуется. [ /comment ]")
        else:
            print('buy_relult_comment')

        cursor.execute(f'SELECT product FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_product = cursor.fetchone()
        if relult_product[0] != None:
            bot.send_message(message.chat.id,f"Продукт : {relult_product[0]}")
        elif relult_product[0] == None:
            bot.send_message(message.chat.id,f"Теперь все хорошо, выберите товар из [канала]({LINKCHANL}) и кнопкой 'Переслать' отправте сюда. [КАНАЛ]({LINKCHANL}) ", parse_mode='Markdown')
        else:
            print('buy_relult_product')
            
        # and relult_comment[0] != None
        if relult_fio[0] != None and relult_adress[0] != None and relult_product[0] != None :
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Да, я подтверждаю заказ")
            btn2 = types.KeyboardButton("Нет, я отказываюсь от заказа")
            markup.add(btn1, btn2)
            mesg = bot.reply_to(message, "Вы покупаете ?", reply_markup=markup )
            bot.register_next_step_handler(mesg,itig_buy) 
        else:
            # если что то написать и потом /buy,/start то тут вылезит err+buy
            # print('err+buy')
            pass
    else:
        print("buy")

    connection.commit()
    connection.close()

def itig_buy(message):
    if message.text == "Да, я подтверждаю заказ":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Да, я перевел.")
        btn2 = types.KeyboardButton("Нет, я не перевел.")
        markup.add(btn1, btn2)
        
        connection = sqlite3.connect('mydatabase.sqlite3')
        cursor = connection.cursor()
        cursor.execute(f'SELECT product FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_product = cursor.fetchone()
        connection.commit()
        connection.close()
        
        bot.send_message(message.chat.id,f"Способ оплаты: на карту Россельхозбанка\nЦена / Товар: {relult_product[0]}\nВаш ID: {message.from_user.id}\nРеквизиты для оплаты:\n\n6234462005869505\n__________________________\n\nВы платите физическому лицу.")
        mesg = bot.reply_to(message, "Вы перевели ?", reply_markup=markup )
        bot.register_next_step_handler(mesg,pay) 
    elif message.text == "Нет, я отказываюсь от заказа":
        bot.send_message(message.chat.id,f"Если вы потом захотите купить у нас то отредактируйте данные заказа если они устареют для вас.",reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id,f"Перезапустите команду /buy",reply_markup=types.ReplyKeyboardRemove())

def pay(message):
    if message.text == "Да, я перевел.":
        bot.send_message(message.chat.id,f"Отправте нам скрин перевода и после этого, оформление закончится,\n если у нас будут вопросы к вам то напишим с даннгого аккаунта {TGSUPPORT}" ,reply_markup=types.ReplyKeyboardRemove())
        connection = sqlite3.connect('mydatabase.sqlite3')
        cursor = connection.cursor()
        cursor.execute(f'SELECT fio FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_fio = cursor.fetchone()
        cursor.execute(f'SELECT adress FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_adress = cursor.fetchone()
        cursor.execute(f'SELECT comment FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_comment = cursor.fetchone()
        cursor.execute(f'SELECT product FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_product = cursor.fetchone()
        bot.send_message(IDAUROR,f"Проверяйте оплату. Заказ от {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username} {message.from_user.id} ( ФИО : {relult_fio[0]} | Адресс : [ {relult_adress[0]} ] | Продукт : {relult_product[0]} ) | Комментарий : [ {relult_comment[0]}]")
        cursor.execute(f'SELECT id FROM users WHERE id_users = {message.from_user.id} LIMIT 1')
        relult_redact_id_users = cursor.fetchone()
        redact_id_users = f"{message.from_user.id}_{relult_redact_id_users[0]}"
        cursor.execute(f'UPDATE users SET id_users = "{redact_id_users}" WHERE id_users = {message.from_user.id}')
        connection.commit()
        connection.close()
    elif message.text == "Нет, я не перевел.":
        bot.send_message(message.chat.id,f"Приходите когда наберетесь смелости.",reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id,f"Перезапустите команду /buy",reply_markup=types.ReplyKeyboardRemove())
        
bot.polling(non_stop=True, interval=0,timeout=600)