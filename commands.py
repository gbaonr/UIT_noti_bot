from background_task import *


# Command: /start
async def start(update: Update, context: CallbackContext):
    """Xử lý lệnh /start - Đăng ký nhận thông báo"""
    chat_id = update.effective_chat.id

    users = load_registered_users()

    if chat_id not in users:
        users.append(chat_id)
        save_registered_users(users)
        await update.message.reply_text("Bạn đã đăng ký nhận thông báo thành công! ✅")
    else:
        await update.message.reply_text("Bạn đã đăng ký trước đó rồi! 🔔")


# Command: /see_my_id
async def see_my_id(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID của bạn là: {chat_id}")


# Command: /stop
async def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    users = load_registered_users()

    if chat_id in users:
        users.remove(chat_id)
        save_registered_users(users)
        await update.message.reply_text("Bạn đã hủy đăng ký nhận thông báo! ☹️")
    else:
        await update.message.reply_text(
            "⚠️ Bạn chưa đăng ký nhận thông báo!\n\n📌 Hãy sử dụng lệnh /start để đăng ký nhận thông báo."
        )


# Command: /check
async def check_new_notification(update: Update, context: CallbackContext):
    """
    - Check for new noti,if there is any, create the messages and return
    --> Return: [message1, message2] with message1 is for tbao_chung and message2 is for tin_noi_bat

    """

    if not is_user(update.effective_chat.id):
        await update.message.reply_text(
            "⚠️ Bạn chưa đăng ký nhận thông báo!\n\n📌 Hãy sử dụng lệnh /start để đăng ký nhận thông báo."
        )
        return

    latest_notification = get_latest_notification()
    last_notification = load_last_notification()
    if not last_notification:
        last_notification = {}
    tbao_chung = latest_notification.get("tbao_chung", [])
    tin_noi_bat = latest_notification.get("tin_noi_bat", [])
    old_tbao_chung = last_notification.get("tbao_chung", [])
    old_tin_noi_bat = last_notification.get("tin_noi_bat", [])
    messages = ["Nothing new", "Nothing new"]
    if tbao_chung != old_tbao_chung:
        news = [x for x in tbao_chung if x not in old_tbao_chung]
        messages[0] = create_message(news, type="tbao_chung")
    if tin_noi_bat != old_tin_noi_bat:
        news = [x for x in tin_noi_bat if x not in old_tin_noi_bat]
        messages[1] = create_message(news, type="tin_noi_bat")
    chat_id = update.effective_chat.id
    if messages[0] != "Nothing new":
        # await update.message.reply_text(messages[0])
        await send_to_all(messages[0])
        save_last_notification(latest_notification)
    if messages[1] != "Nothing new":
        # await update.message.reply_text(messages[1])
        await send_to_all(messages[1])
        save_last_notification(latest_notification)
    if messages[0] == messages[1]:
        await update.message.reply_text(messages[0])


# Command: /get
async def get(update: Update, context: CallbackContext):
    """Command to get the last notification"""
    last_notifications = load_last_notification()
    tbao_chung = last_notifications.get("tbao_chung", [])
    tin_noi_bat = last_notifications.get("tin_noi_bat", [])
    message1 = create_message(tbao_chung, type="tbao_chung")
    message2 = create_message(tin_noi_bat, type="tin_noi_bat")
    await send_message(update.effective_chat.id, message1)
    await send_message(update.effective_chat.id, message2)


# MessageHandler echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    if update.message.text:
        await update.message.reply_text(update.message.text)
    elif update.message.sticker:
        await update.message.reply_sticker(update.message.sticker)


# Command: /help
async def help_command(update: Update, context: CallbackContext):
    help_text = """
    /start:  Đăng ký nhận tin nhắn mỗi 8 tiếng (Tin nhắn thông báo có hoặc không có update mới từ web students)
/stop:  Hủy đăng ký nhận thông báo 
/see_my_id:  Xem Chat ID của bạn
/check:  Kiểm tra thông báo mới
/get:  Lấy thông báo cuối cùng  
/help:  Hiển thị hướng dẫn sử dụng
Bot sẽ nhại lại bất cứ tin nhắn nào của bạn nếu không phải là lệnh của bot
    """
    await update.message.reply_text(help_text)
