import telebot
from telebot import types

# Указать токен вашего бота, который вы получили от BotFather
TOKEN = '7024914121:AAFFVd1z5ddy3U-1JLVsYih3uLGg4i6uOzI'

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Словарь с каталогом товаров (можно заменить на базу данных)
catalog = {
    1: {"name": "Пельмени", "price": 200, "photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcREp30RkWTJw40TWqVsn4EFjvZyjmEocebwk6OwbTsLAA&s",
        "description": "Очень вкусные пельмени"},
    2: {"name": "Вареники", "price": 150, "photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcREp30RkWTJw40TWqVsn4EFjvZyjmEocebwk6OwbTsLAA&s",
        "description": "Сочные вареники"},
    3: {"name": "Блины", "price": 180, "photo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcREp30RkWTJw40TWqVsn4EFjvZyjmEocebwk6OwbTsLAA&s",
        "description": "Пышные блины"},
    # Добавьте другие товары сюда
}

# Корзина пользователя (словарь для каждого чата)
user_baskets = {}


# Обработчик команды /start или любого текстового сообщения
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    if message.text == '/start':
        send_welcome_message(message)
    elif message.text == '🍽 Меню':
        send_catalog_menu(message)
    elif message.text == '🛒 Корзина':
        show_basket(message)
    elif message.text == '🛍️ Оформить заказ':
        checkout(message)
    else:
        bot.send_message(user_id, "Используйте кнопки для взаимодействия.")


# Функция отправки приветственного сообщения с клавиатурой
def send_welcome_message(message):
    user_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🍽 Меню"), types.KeyboardButton("🛒 Корзина"))
    markup.add(types.KeyboardButton("🛍️ Оформить заказ"))  # Кнопка "Оформить заказ" в главном меню
    bot.send_message(user_id, "Привет! Чем могу помочь?", reply_markup=markup)


# Функция отправки меню каталога
def send_catalog_menu(message):
    user_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)

    for item_id, item_info in catalog.items():
        item_name = item_info['name']
        # Добавляем кнопку для каждого товара в меню каталога
        markup.add(types.InlineKeyboardButton(item_name, callback_data=f"view_item_{item_id}"))

    # Добавляем кнопку "Назад в главное меню"
    markup.add(types.InlineKeyboardButton("🔙 Назад в главное меню", callback_data="back_to_main_menu"))

    bot.send_message(user_id, "Выберите товар из каталога:", reply_markup=markup)


# Функция показа информации о товаре при выборе из меню каталога
def view_catalog_item(user_id, item_id):
    if item_id in catalog:
        item_info = catalog[item_id]
        item_name = item_info['name']
        item_price = item_info['price']
        item_description = item_info['description']
        item_photo = item_info['photo']

        # Определяем количество данного товара в корзине пользователя
        quantity_in_basket = user_baskets.get(user_id, {}).get(item_id, 0)

        # Создаем сообщение с информацией о товаре и кнопками для управления количеством в корзине
        text = f"<b>{item_name}</b>\nЦена: {item_price} руб.\n\n{item_description}"
        text += f"\n\nКоличество в корзине: {quantity_in_basket}"

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("➕", callback_data=f"add_to_basket_{item_id}"),
            types.InlineKeyboardButton("➖", callback_data=f"remove_from_basket_{item_id}")
        )

        # Добавляем кнопку "Вернуться в каталог"
        markup.add(types.InlineKeyboardButton("🔙 Вернуться в каталог", callback_data="return_to_catalog"))

        # Отправляем сообщение с фотографией товара и кнопками
        bot.send_photo(user_id, item_photo, caption=text, reply_markup=markup, parse_mode='HTML')
    else:
        bot.send_message(user_id, "Товар не найден.")


# Функция показа содержимого корзины
def show_basket(message):
    user_id = message.chat.id
    if user_id in user_baskets and user_baskets[user_id]:
        basket_message = "Ваша корзина:\n"
        total_price = 0
        for item_id, quantity in user_baskets[user_id].items():
            item_info = catalog[item_id]
            item_total_price = item_info['price'] * quantity
            basket_message += f"{item_info['name']} - {quantity} шт. - {item_total_price} руб.\n"
            total_price += item_total_price
        basket_message += f"Итого: {total_price} руб."

        # Добавляем кнопку "Очистить корзину"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Очистить корзину", callback_data="clear_basket"))

        bot.send_message(user_id, basket_message, reply_markup=markup)
    else:
        bot.send_message(user_id, "Ваша корзина пуста.")

# Функция полной очистки корзины
def clear_basket(user_id):
    if user_id in user_baskets:
        user_baskets[user_id] = {}  # Очищаем корзину пользователя
        bot.send_message(user_id, "Корзина очищена.")
    else:
        bot.send_message(user_id, "Ваша корзина уже пуста.")

# Функция оформления заказа
def checkout(message):
    user_id = message.chat.id
    if user_id in user_baskets and user_baskets[user_id]:
        total_price = sum(catalog[item_id]['price'] * quantity for item_id, quantity in user_baskets[user_id].items())
        bot.send_message(user_id, f"Ваш заказ на сумму {total_price} руб. оформлен.")
        user_baskets[user_id] = {}  # Очищаем корзину после оформления заказа
    else:
        bot.send_message(user_id, "Ваша корзина пуста.")


# Обработчик нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    if call.data.startswith('view_item_'):
        item_id = int(call.data.replace('view_item_', ''))  # Получаем item_id из callback_data
        view_catalog_item(user_id, item_id)
    elif call.data.startswith('add_to_basket_'):
        item_id = int(call.data.replace('add_to_basket_', ''))  # Получаем item_id из callback_data
        add_to_basket(user_id, item_id, 'add')  # Добавляем товар в корзину
    elif call.data.startswith('remove_from_basket_'):
        item_id = int(call.data.replace('remove_from_basket_', ''))  # Получаем item_id из callback_data
        add_to_basket(user_id, item_id, 'remove')  # Удаляем товар из корзины
    elif call.data == 'clear_basket':
        clear_basket(user_id)  # Очищаем корзину
    elif call.data == 'back_to_main_menu':
        send_welcome_message(call.message)
    elif call.data == 'return_to_catalog':
        send_catalog_menu(call.message)  # Отправляем пользователю меню каталога

# Функция добавления и удаления товара из корзины
def add_to_basket(user_id, item_id, action):
    if action == 'add':
        # Добавляем товар в корзину
        if user_id not in user_baskets:
            user_baskets[user_id] = {}
        if item_id in user_baskets[user_id]:
            user_baskets[user_id][item_id] += 1
        else:
            user_baskets[user_id][item_id] = 1
    elif action == 'remove':
        # Удаляем товар из корзины
        if user_id in user_baskets and item_id in user_baskets[user_id] and user_baskets[user_id][item_id] > 0:
            user_baskets[user_id][item_id] -= 1
            if user_baskets[user_id][item_id] == 0:
                del user_baskets[user_id][item_id]

    # Пересылаем обновленную информацию о товаре в корзине
    view_catalog_item(user_id, item_id)




# Запуск бота
bot.polling()