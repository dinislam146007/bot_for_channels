import telebot
from telebot import types
import threading

bot_token = ""
channel_id = ""
user_id = ''
count = 0
aunt = 2
co = 0
media_group = []
bot = telebot.TeleBot(bot_token)
photo_ids = ''
user_states = {}
user_storage = {}
user_storage[1] = {}
timer_flak = False


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет! Вы можете отправить любые свои идеи или задать вопрос. Бот принимает:\n- Текст\n- Видео\n- Фото\n- Видеосообщения\n- Голосовые сообщения\n \n [Разработчик](https://t.me/dinislam_ku_channel)",
                     parse_mode="Markdown")


@bot.message_handler()
def get_message(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Опубликовать', callback_data='channel'))
    markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'answer:{message.chat.id}:{message.text}'))
    bot.send_message(user_id, message.text, reply_markup=markup)
    bot.reply_to(message, '✅Ваше сообщение успешно отправлено!')


@bot.callback_query_handler(func=lambda call: call.data == 'channel')
def chanel(call):
    bot.send_message(channel_id, call.message.text)



@bot.message_handler(content_types=['photo', 'video'])
def photo_handler(message):
    global media_group, timer_flak, photo_ids, aunt, co
    if co == 0:
        user_storage[aunt + 1] = {'photo_ids': [], 'caption': [], 'video': []}
    co += 1
    markup = types.InlineKeyboardMarkup()
    caption = message.caption
    if caption != None:
        user_storage[aunt + 1]['caption'].append(caption)
    if message.content_type == 'photo':
        photo = [message.photo[-1].file_id]
        media_group += [telebot.types.InputMediaPhoto(photo_id, caption=caption) for photo_id in photo]
        user_storage[aunt + 1]["photo_ids"].append(photo)
    elif message.content_type == 'video':
        video = [message.video.file_id]
        media_group += [telebot.types.InputMediaVideo(video_id, caption=caption) for video_id in video]
        user_storage[aunt + 1]["video"].append(video)

    def timer_callback():
        global timer_flak, aunt, co
        aunt += 1
        co = 0
        bot.send_media_group(user_id, media=media_group)
        cap = user_storage[1].get('caption', [])
        markup.add(types.InlineKeyboardButton('Опубликовать', callback_data=f"publish_media:{cap}"))
        markup.add(types.InlineKeyboardButton('Ответить', callback_data=f"answer:{message.chat.id}:{'Медиа файл(ы)'}"))
        bot.send_message(user_id, f'Альбом{aunt}', reply_markup=markup)
        media_group.clear()
        timer_flak = False

    if timer_flak == False:
        timer_flak = True
        delay = 5
        timer = threading.Timer(delay, timer_callback)
        timer.start()


@bot.callback_query_handler(func=lambda call: call.data.startswith('publish_media'))
def doc(call):
    au = int(call.message.text[6:])
    caption = user_storage[au].get('caption', '')
    cap = f"{caption}"
    caption_flak = False
    ca = cap[2:-2]
    ca = ca.replace(r'\n', ' \n')
    user_data_list = user_storage[au].get('photo_ids', [])
    photo_flak = f'{user_data_list}'
    user_video = user_storage[au].get('video', [])
    video_flak = f'{user_video}'
    media = []
    c = 0
    if photo_flak == '[]':
        pass
    else:
        for i in user_data_list:
            c += 1
            photo = i[0]
            if c == 1:
                media += [telebot.types.InputMediaPhoto(photo, caption=ca)]
            else:
                media += [telebot.types.InputMediaPhoto(photo)]
        caption_flak = True
    if video_flak == '[]':
        pass
    else:
        for j in user_video:
            video = j[0]
            if caption_flak is False:
                media += [telebot.types.InputMediaVideo(video, caption=ca)]
                caption_flak = True
            else:
                media += [telebot.types.InputMediaVideo(video)]

    bot.send_media_group(channel_id, media=media)
    del user_storage[au]


@bot.message_handler(content_types=['video_note'])
def handle_video_note(message):
    global aunt
    video_note_file_id = message.video_note.file_id
    bot.send_video(chat_id=user_id, video=video_note_file_id)
    user_storage[aunt] = {'video_note': f"{video_note_file_id}"}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Опубликовать', callback_data='video_note'))
    markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'answer:{message.chat.id}:{"Видеосообщение"}'))
    bot.send_message(user_id, f'Видеосообщение{aunt}', reply_markup=markup)
    bot.reply_to(message, '✅Ваше сообщение успешно отправлено!')
    aunt += 1


@bot.callback_query_handler(func=lambda call: call.data.startswith('video_note'))
def video_note(call):
    au = int(call.message.text[14:])
    video_note_id = user_storage[au].get('video_note', [])
    bot.send_video(chat_id=channel_id, video=video_note_id)
    del user_storage[au]




@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    global aunt
    voice_id = message.voice.file_id
    bot.send_voice(user_id, voice_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Опубликовать', callback_data='voice'))
    markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'answer:{message.chat.id}:{"Голосовое сообщение"}'))
    user_storage[aunt] = {'voice': f"{voice_id}"}
    bot.send_message(user_id, f'Голосовое сообщение{aunt}', reply_markup=markup)
    bot.reply_to(message, '✅Ваше сообщение успешно отправлено')
    aunt += 1


@bot.callback_query_handler(func=lambda call: call.data.startswith('voice'))
def voice(call):
    au = int(call.message.text[19:])
    voice_id = user_storage[au].get('voice', [])
    bot.send_voice(channel_id, voice_id)
    del user_storage[au]


@bot.message_handler(content_types=['document'])
def handle_document(message):
    global aunt
    document_id = message.document.file_id
    caption = message.caption
    bot.send_document(message.chat.id, document_id, caption=caption)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Опубликовать', callback_data=f'doc {caption}'))
    markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'answer{message.chat.id}:{"Документ"}'))
    user_storage[aunt] = {'doc': f"{document_id}", "caption": f'{caption}'}
    bot.send_message(user_id, f'Документ{aunt}', reply_markup=markup)
    bot.reply_to(message, '✅Ваше сообщение успешно отправлено')
    aunt += 1


@bot.callback_query_handler(func=lambda call: call.data.startswith('doc'))
def doc(call):
    au = int(call.message.text[8:])
    document_id = user_storage[au].get('doc', [])
    caption = f"{user_storage[au].get('caption', [])}"[1:-1]
    if caption == 'None':
        bot.send_document(channel_id, document_id)
    else:
        bot.send_document(channel_id, document_id, caption=caption)
    del user_storage[au]


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    global aunt
    caption = message.caption
    # Получаем информацию о аудиофайле
    audio_id = message.audio.file_id
    markup = types.InlineKeyboardMarkup()
    user_storage[aunt] = {'audio': f"{audio_id}", 'caption': f"{caption}"}
    bot.send_audio(user_id, audio_id, caption=caption)
    markup.add(types.InlineKeyboardButton('Опубликовать', callback_data=f'audio'))
    markup.add(types.InlineKeyboardButton('Ответить', callback_data=f'answer:{message.chat.id}:{"Аудио"}'))
    bot.send_message(user_id, f'Аудио{aunt}', reply_markup=markup)
    aunt += 1

    # Отправляем аудиофайл обратно пользователю
@bot.callback_query_handler(func=lambda call: call.data.startswith('audio'))
def doc(call):
    au = int(call.message.text[5:])
    audio_id = user_storage[au].get('audio', [])
    caption = f"{user_storage[au].get('caption', [])}"
    if caption == 'None':
        bot.send_document(channel_id, audio_id)
    else:
        bot.send_document(channel_id, audio_id, caption=caption)
    del user_storage[au]
@bot.callback_query_handler(func=lambda call: call.data.startswith('otvet'))
def answer(call):
    # vopros = call.data.split(':')[2]
    # ser = call.data.split(':')[1]
    question = call.data.split(":")[1]
    markup = types.ForceReply(selective=False)
    bot.send_message(call.message.chat.id, f'Введите ответ на вопрос:\n{call.data.split(":")[1]}', reply_markup=markup)
    def handle_text_input(message):
        markup1 = types.InlineKeyboardMarkup()
        markup1.add(types.InlineKeyboardButton('Ответить',
                                              callback_data=f'answer:{message.chat.id}:{message.text}'))

        bot.send_message(call.data.split(':')[2], f'❓ Вопрос:\n{question} \n💬 Ответ: \n{message.text}', reply_markup=markup1)
        bot.send_message(message.chat.id, '✅ Ваше сообщение успешно отправлено! ✅')
    bot.register_next_step_handler(call.message, handle_text_input)

@bot.callback_query_handler(func=lambda call: call.data.startswith('answer'))
def answer(call):
    # vopros = call.data.split(':')[2]
    # ser = call.data.split(':')[1]
    question = call.data.split(":")[2]
    id = call.data.split(":")[1]
    markup = types.ForceReply(selective=False)
    bot.send_message(user_id, f'Введите ответ на вопрос:\n{call.data.split(":")[2]}', reply_markup=markup)
    def handle_text_input(message):
        markup1 = types.InlineKeyboardMarkup()
        markup1.add(types.InlineKeyboardButton('Ответить',
                                              callback_data=f'otvet:{message.text}:{message.chat.id}'))
        bot.send_message(message.chat.id, '✅ Ваше сообщение успешно отправлено! ✅')
        bot.send_message(id, f'❓ Вопрос:\n {question} \n 💬 Ответ: \n{message.text}', reply_markup=markup1)
    bot.register_next_step_handler(call.message, handle_text_input)


bot.infinity_polling()
